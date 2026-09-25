#!/usr/bin/env python3
"""Offline checks for the quota-aware catalog scan.

Run with `python3 scripts/test_metadata_catalog.py`. No network, no pytest.
"""

import sys
import tempfile
from pathlib import Path
from urllib.error import HTTPError

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
                budget.note_403(headers)
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
