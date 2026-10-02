#!/usr/bin/env python3
"""Offline checks for the quota-aware catalog scan.

Run with `python3 scripts/test_metadata_catalog.py`. No network, no pytest.
"""

import sys
import tempfile
from pathlib import Path
from urllib.error import HTTPError
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))

import metadata_catalog as mc


def _entries(n):
    return [{"owner": "acme", "name": f"repo{i:04d}", "branch": "main", "skillsPath": "skills"} for i in range(n)]


def _fake_github(fail_after):
    """A GitHub that answers `fail_after` tree requests and then runs out of quota."""
    state = {"calls": 0}

    def jget(url, token, budget=None):
        state["calls"] += 1
        if state["calls"] > fail_after:
            headers = {"X-RateLimit-Remaining": "0", "X-RateLimit-Reset": "1789000000"}
            error = HTTPError(url, 403, "rate limit exceeded", headers, None)
            if budget is not None:
                budget.note_rate_limit(error.code, headers)
            raise error
        return {"tree": [{"type": "blob", "path": "skills/one/SKILL.md"}], "truncated": False}

    return jget, state


def test_spent_quota_never_erases_a_measured_count():
    real, mc._jget = mc._jget, _fake_github(10)[0]
    try:
        entries = _entries(50)
        first, cursor = mc.count_skills(entries, max_workers=2, previous={}, offset=0)
        assert cursor == 0, cursor
        assert sum(1 for r in first.values() if r["status"] == "ok") == 10
        assert sum(1 for r in first.values() if r["status"] == "pending") == 40

        second, _ = mc.count_skills(entries, max_workers=2, previous=first, offset=cursor)
        counted = [k for k, r in first.items() if r["status"] == "ok"]
        for key in counted:
            assert second[key]["count"] == 1, second[key]
            assert second[key]["status"] == "ok", second[key]

        # Carrying the same row again must not stack another clause onto the note.
        third, _ = mc.count_skills(entries, max_workers=2, previous=second, offset=0)
        for key in counted:
            note = third[key]["note"]
            assert note.count(mc.CARRY_NOTE) <= 1, note
    finally:
        mc._jget = real


def test_uncounted_repositories_go_first():
    real, mc._jget = mc._jget, _fake_github(5)[0]
    try:
        entries = _entries(20)
        previous = {f"acme/repo{i:04d}": {"full": f"acme/repo{i:04d}", "count": 3, "status": "ok",
                                          "branch": "main", "path": "skills", "note": ""}
                    for i in range(15)}
        counts, _ = mc.count_skills(entries, max_workers=1, previous=previous, offset=0)
        # The five that nobody had counted are exactly the five that got the quota.
        for i in range(15, 20):
            assert counts[f"acme/repo{i:04d}"]["status"] == "ok", counts[f"acme/repo{i:04d}"]
    finally:
        mc._jget = real


def _measured(entries):
    return {f"{e['owner']}/{e['name']}": {
        "full": f"{e['owner']}/{e['name']}", "count": 7, "status": "ok",
        "branch": e["branch"], "path": e["skillsPath"], "note": "",
    } for e in entries}


def test_http_429_stops_requests_and_preserves_counts():
    entries = _entries(3)
    previous = _measured(entries)
    for headers in ({"Retry-After": "60"}, {}):
        error = HTTPError("https://api.github.com/test", 429, "Too Many Requests", headers, None)
        # Patch the transport, not _jget, so both HTTP handling layers are tested.
        with patch.object(mc, "urlopen", side_effect=error) as transport:
            counts, cursor = mc.count_skills(entries, max_workers=1, previous=previous)
        assert transport.call_count == 1, transport.call_count
        assert cursor == 0, cursor
        for row in counts.values():
            assert row["count"] == 7 and row["status"] == "ok", row
            assert mc.CARRY_NOTE in row["note"], row


def test_http_403_only_spends_budget_when_rate_limited():
    entries = _entries(3)
    previous = _measured(entries)
    cases = [
        ({"X-RateLimit-Remaining": "0"}, True),
        ({"Retry-After": "60"}, True),
        ({"X-RateLimit-Remaining": "10"}, False),
    ]
    for headers, exhausted in cases:
        error = HTTPError("https://api.github.com/test", 403, "Forbidden", headers, None)
        with patch.object(mc, "urlopen", side_effect=error) as transport:
            counts, _ = mc.count_skills(entries, max_workers=1, previous=previous)
        assert transport.call_count == (1 if exhausted else 3), transport.call_count
        for row in counts.values():
            assert row["status"] == ("ok" if exhausted else "forbidden"), row
            assert row["count"] == (7 if exhausted else 0), row


def test_changed_measurements_are_prioritized_and_not_carried():
    # A branch change, a path change, or both invalidate a previous count.
    for changes in ({"branch": "develop"}, {"skillsPath": "new-skills"},
                    {"branch": "develop", "skillsPath": "new-skills"}):
        entries = _entries(3)
        previous = _measured(entries)
        entries[2].update(changes)
        ordered, fresh_count = mc._scan_order(entries, previous, offset=1)
        assert fresh_count == 1, fresh_count
        assert ordered[0] == entries[2], ordered

        error = HTTPError("https://api.github.com/test", 429, "Too Many Requests",
                          {"Retry-After": "60"}, None)
        with patch.object(mc, "urlopen", side_effect=error) as transport:
            counts, _ = mc.count_skills(entries, max_workers=1, previous=previous, offset=1)
        assert transport.call_count == 1, transport.call_count
        assert "/repo0002/" in transport.call_args.args[0].full_url
        changed = counts["acme/repo0002"]
        assert changed["status"] == "pending" and changed["count"] == 0, changed
        assert changed["branch"] == entries[2]["branch"], changed
        assert changed["path"] == entries[2]["skillsPath"], changed
        for i in range(2):
            assert counts[f"acme/repo{i:04d}"]["count"] == 7, counts

        # Also exercise the already-spent fast path, where no request is made.
        budget = mc.Budget()
        budget.spent = True
        with patch.object(mc, "urlopen") as transport:
            changed = mc._count_skill(entries[2], None, budget, previous)
        transport.assert_not_called()
        assert changed["status"] == "pending" and changed["count"] == 0, changed


def test_changed_measurement_receives_a_fresh_count():
    entries = _entries(3)
    previous = _measured(entries)
    entries[2].update(branch="develop", skillsPath="new-skills")
    calls = []

    def jget(url, token, budget=None):
        calls.append(url)
        if len(calls) > 1:
            budget.note_rate_limit(429, {})
            raise HTTPError(url, 429, "Too Many Requests", {}, None)
        return {"tree": [{"type": "blob", "path": "new-skills/one/SKILL.md"}]}

    with patch.object(mc, "_jget", side_effect=jget):
        counts, _ = mc.count_skills(entries, max_workers=1, previous=previous)
    assert "/repo0002/git/trees/develop?" in calls[0], calls
    row = counts["acme/repo0002"]
    assert row["status"] == "ok" and row["count"] == 1, row
    assert row["branch"] == "develop" and row["path"] == "new-skills", row


def test_cursor_rotates_previously_measured_repositories():
    entries = _entries(5)
    previous = _measured(entries)
    with patch.object(mc, "_jget", side_effect=_fake_github(2)[0]):
        counts, cursor = mc.count_skills(entries, max_workers=1, previous=previous)
    assert cursor == 2, cursor
    assert {k for k, r in counts.items() if mc.CARRY_NOTE not in r["note"]} == {
        "acme/repo0000", "acme/repo0001",
    }, counts
    with patch.object(mc, "_jget", side_effect=_fake_github(2)[0]):
        counts, cursor = mc.count_skills(entries, max_workers=1, previous=counts, offset=cursor)
    assert cursor == 4, cursor
    assert {k for k, r in counts.items() if mc.CARRY_NOTE not in r["note"]} == {
        "acme/repo0002", "acme/repo0003",
    }, counts


def test_readme_round_trip_keeps_counts_and_cursor():
    entries = _entries(3)
    counts = {
        "acme/repo0000": {"full": "acme/repo0000", "count": 12, "status": "ok", "branch": "main", "path": "skills", "note": ""},
        "acme/repo0001": {"full": "acme/repo0001", "count": 0, "status": "missing", "branch": "main", "path": "skills", "note": "HTTP 404"},
        "acme/repo0002": {"full": "acme/repo0002", "count": 7, "status": "truncated", "branch": "main", "path": "skills", "note": "tree truncated; count is lower bound"},
    }
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "README.md"
        path.write_text(mc.render_readme(entries, counts, next_offset=4242), encoding="utf-8")
        previous, offset = mc.read_previous(str(path))
        assert offset == 4242, offset
        for key, row in counts.items():
            assert previous[key]["count"] == row["count"], (key, previous[key])
            assert previous[key]["status"] == row["status"], (key, previous[key])


if __name__ == "__main__":
    failures = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_"):
            try:
                fn()
                print(f"ok   {name}")
            except AssertionError as exc:
                failures += 1
                print(f"FAIL {name}: {exc}")
    sys.exit(1 if failures else 0)
