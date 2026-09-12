#!/usr/bin/env python3
from __future__ import annotations
import json, os, re
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

UA = "awesome-metadata-catalog/1.0"
# Statuses that came from an answered request. Anything else is an unknown the
# next run should spend its quota on first.
MEASURED = {"ok", "truncated", "missing"}
CARRY_NOTE = "not rechecked this run, GitHub hourly quota spent"
RELATED_LISTS = [
    (
        "loqimean/awesome-claude-code-hooks",
        "https://github.com/loqimean/awesome-claude-code-hooks",
        "Curated list of Claude Code hooks for extending and automating Claude Code workflows.",
    ),
]


class Budget:
    """One run's share of the GitHub hourly quota.

    The catalog needs one tree request per source repository, and the list is
    already larger than an hour's allowance. Once the allowance is spent every
    further request comes back 403, so the run stops asking instead of turning
    the rest of the catalog into error rows.
    """

    def __init__(self) -> None:
        self.spent = False
        self.reset_at = ""

    def note_403(self, headers) -> bool:
        """True when this 403 is the quota running out, not a private repo."""
        if headers.get("X-RateLimit-Remaining") == "0" or headers.get("Retry-After"):
            self.spent = True
            reset = headers.get("X-RateLimit-Reset")
            if reset and reset.isdigit():
                self.reset_at = datetime.fromtimestamp(int(reset), timezone.utc).strftime("%H:%M UTC")
            return True
        return False


def _jget(url: str, token: str | None, budget: "Budget | None" = None) -> dict:
    headers = {"User-Agent": UA, "Accept": "application/vnd.github+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    try:
        with urlopen(Request(url, headers=headers), timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except HTTPError as e:
        if e.code == 403 and budget is not None:
            budget.note_403(e.headers)
        raise


def fetch_repos_from_sources(sources: list[dict]) -> list[dict]:
    token = os.environ.get("GITHUB_TOKEN")
    merged: dict[str, dict] = {}
    for source in sources:
        data = _jget(source["url"], token)
        items = data.values() if isinstance(data, dict) else data
        for entry in items:
            owner = entry.get("owner") or entry.get("repoOwner") or ""
            name = entry.get("name") if entry.get("repoOwner") is None else entry.get("repoName")
            if owner and name and entry.get("enabled", True):
                merged[f"{owner}/{name}"] = entry
    return list(merged.values())


def _fields(entry: dict) -> dict:
    return {
        "owner": entry.get("owner") or entry.get("repoOwner") or "",
        "name": entry.get("name") if entry.get("repoOwner") is None else entry.get("repoName"),
        "branch": entry.get("branch") or entry.get("repoBranch") or "main",
        "path": (entry.get("skillsPath") or entry.get("agentsPath") or entry.get("pluginPath") or entry.get("subPath") or "").strip("/"),
    }


def _carry_over(full: str, f: dict, previous: dict, budget: "Budget") -> dict:
    """What to publish for a repository this run could not reach.

    A stale number that was measured is worth more than a fresh zero that was
    not, so the previous row is reused verbatim when there is one.
    """
    kept = previous.get(full)
    when = f" (quota resets {budget.reset_at})" if budget.reset_at else ""
    if kept and kept.get("status") in MEASURED:
        # Strip the marker a previous carry-over may have left, so the note
        # does not grow by one clause per skipped run.
        note = (kept.get("note") or "").split(CARRY_NOTE)[0].strip().rstrip(";").strip()
        note = f"{note}; " if note else ""
        return {**kept, "full": full, "branch": f["branch"], "path": f["path"],
                "note": f"{note}{CARRY_NOTE}{when}", "_carried": True}
    return {"full": full, "count": 0, "status": "pending", "branch": f["branch"], "path": f["path"],
            "note": f"not counted yet, GitHub hourly quota spent{when}", "_carried": True}


def _count_skill(entry: dict, token: str | None, budget: "Budget", previous: dict) -> dict:
    f = _fields(entry)
    full = f"{f['owner']}/{f['name']}"
    if budget.spent:
        return _carry_over(full, f, previous, budget)
    try:
        tree = _jget(f"https://api.github.com/repos/{full}/git/trees/{f['branch']}?recursive=1", token, budget)
    except HTTPError as e:
        if e.code == 403 and budget.spent:
            return _carry_over(full, f, previous, budget)
        status = "missing" if e.code == 404 else "forbidden" if e.code == 403 else "error"
        return {"full": full, "count": 0, "status": status, "note": f"HTTP {e.code}", "branch": f["branch"], "path": f["path"]}
    except (URLError, OSError, TimeoutError) as e:
        return {"full": full, "count": 0, "status": "error", "note": str(e)[:120], "branch": f["branch"], "path": f["path"]}
    count = 0
    base = f["path"]
    for n in tree.get("tree", []):
        if n.get("type") != "blob":
            continue
        p = n["path"]
        if base and not (p.startswith(base + "/") or p == base):
            continue
        if p.endswith("/SKILL.md") or p == "SKILL.md":
            count += 1
    trunc = bool(tree.get("truncated", False))
    return {"full": full, "count": count, "status": "truncated" if trunc else "ok", "note": "tree truncated; count is lower bound" if trunc else "", "branch": f["branch"], "path": f["path"]}


def _scan_order(entries: list[dict], previous: dict, offset: int) -> tuple[list[dict], int]:
    """Repositories nobody has counted yet go first, the rest rotate.

    Source configs grow by appending, so a fixed order spends the whole quota
    on the same head of the list and every newly added repository starves: on
    12 Sep 2026 all 392 unreachable rows sat at index 4780 and beyond, out of
    5174.
    """
    fresh, known = [], []
    for e in entries:
        f = _fields(e)
        row = previous.get(f"{f['owner']}/{f['name']}")
        (known if row and row.get("status") in MEASURED else fresh).append(e)
    if known:
        start = offset % len(known)
        known = known[start:] + known[:start]
    return fresh + known, len(fresh)


def count_skills(entries: list[dict], max_workers: int = 8, previous: dict | None = None,
                 offset: int = 0) -> tuple[dict[str, dict], int]:
    """Count skills for as many repositories as the hourly quota allows.

    Returns the counts and the cursor the next run should start from. The
    cursor stays 0 while one run still covers the whole catalog.
    """
    token = os.environ.get("GITHUB_TOKEN")
    previous = previous or {}
    budget = Budget()
    ordered, fresh_count = _scan_order(entries, previous, offset)
    out, carried = {}, set()
    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        futs = {ex.submit(_count_skill, e, token, budget, previous): e for e in ordered}
        for fut in as_completed(futs):
            r = fut.result()
            if r.pop("_carried", False):
                carried.add(r["full"])
            out[r["full"]] = r
    if not carried:
        return out, 0
    known_done = 0
    for e in ordered[fresh_count:]:
        f = _fields(e)
        if f"{f['owner']}/{f['name']}" not in carried:
            known_done += 1
    return out, offset + known_done


OFFSET_MARK = "<!-- scan-offset: "
_ROW = re.compile(r"^\| \[([^\]]+)\]\([^)]*\) \| (\u2265?[\d,]+) \| `([^`]*)` \| `([^`]*)` \| \S+ (\w+) \|(.*)\|\s*$")
_STATUS_WORD = {"ok": "ok", "truncated": "truncated", "missing": "missing", "forbidden": "forbidden", "error": "error", "pending": "pending"}


def read_previous(output_file: str) -> tuple[dict, int]:
    """Recover the last run's table so a spent quota cannot erase it."""
    path = Path(output_file)
    if not path.exists():
        return {}, 0
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return {}, 0
    offset = 0
    for line in text.split("\n"):
        if line.startswith(OFFSET_MARK):
            digits = line[len(OFFSET_MARK):].split("-")[0].strip()
            offset = int(digits) if digits.isdigit() else 0
            break
    rows = {}
    for line in text.split("\n"):
        m = _ROW.match(line)
        if not m:
            continue
        full, count, branch, path_, status, note = m.groups()
        status = _STATUS_WORD.get(status, status)
        rows[full] = {
            "full": full,
            "count": int(count.lstrip("\u2265").replace(",", "")),
            "status": status,
            "branch": branch,
            "path": "" if path_ == "." else path_,
            "note": note.strip().replace("\\|", "|"),
        }
    return rows, offset


def render_readme(entries: list[dict], counts: dict[str, dict], next_offset: int = 0) -> str:
    rows = []
    for e in entries:
        f = _fields(e)
        full = f"{f['owner']}/{f['name']}"
        rows.append({**f, **counts.get(full, {"count": 0, "status": "error", "note": "missing count"})})
    rows.sort(key=lambda r: (r["status"] not in {"ok", "truncated"}, r["owner"].lower(), r["name"].lower()))
    total = sum(r["count"] for r in rows)
    ok = sum(1 for r in rows if r["status"] == "ok")
    trunc = sum(1 for r in rows if r["status"] == "truncated")
    bad = len(rows) - ok - trunc
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        "# Awesome Claude Skills",
        "",
        "[![Awesome](https://awesome.re/badge.svg)](https://awesome.re)",
        "",
        "Metadata catalog for Claude Code skill source repositories. This repo does **not** clone or mirror upstream skill content; it only tracks source repos from [awesome-repo-configs](https://github.com/Chat2AnyLLM/awesome-repo-configs) and counts discoverable `SKILL.md` files via GitHub API.",
        "",
        f"- Enabled source repositories: **{len(rows)}**",
        f"- Discoverable skills: **{total:,}**",
        f"- Healthy repos: **{ok}** · Truncated: **{trunc}** · Unavailable: **{bad}**",
        f"- Last updated: **{ts}**",
        "",
        f"{OFFSET_MARK}{next_offset} -->",
        "",
        "## Related Lists",
        "",
        *[f"- [{name}]({url}) - {description}" for name, url, description in RELATED_LISTS],
        "",
        "## Source Catalog",
        "",
        "| Repository | Skills | Branch | Path | Status | Note |",
        "| --- | ---: | --- | --- | --- | --- |",
    ]
    for r in rows:
        repo = f"[{r['full']}](https://github.com/{r['full']})"
        count = f"≥{r['count']:,}" if r['status'] == 'truncated' else f"{r['count']:,}"
        path = f"`{r['path'] or '.'}`"
        status = {"ok": "✅ ok", "truncated": "⚠️ truncated", "missing": "❌ missing", "forbidden": "⛔ forbidden", "error": "❌ error", "pending": "⏳ pending"}.get(r['status'], r['status'])
        note = (r.get("note") or "").replace("|", "\\|")
        lines.append(f"| {repo} | {count} | `{r['branch']}` | {path} | {status} | {note} |")
    lines += ["", "## Contributing", "", "Add or disable source repositories in [awesome-repo-configs](https://github.com/Chat2AnyLLM/awesome-repo-configs). This repository is a metadata-only catalog."]
    return "\n".join(lines) + "\n"