#!/usr/bin/env python3
"""Check every URL in tools.csv. Prints dead/suspicious links.

Usage: python3 scripts/check_links.py [--out report.txt]
Many sites block bots (403/429/999), so those are reported as 'blocked', not dead.
"""
import csv
import sys
import urllib.request
import urllib.error
import socket
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
UA = "Mozilla/5.0 (compatible; awesome-marketing-link-check/1.0)"


def check(url):
    for method in ("HEAD", "GET"):
        req = urllib.request.Request(url, method=method, headers={"User-Agent": UA})
        try:
            with urllib.request.urlopen(req, timeout=15) as r:
                return url, r.status, ""
        except urllib.error.HTTPError as e:
            if e.code in (403, 429, 999, 401, 503) or (method == "HEAD" and e.code in (405, 400, 404, 501)):
                if method == "HEAD":
                    continue
                return url, e.code, "blocked" if e.code != 404 else ""
            return url, e.code, ""
        except (urllib.error.URLError, socket.timeout, ConnectionError, OSError) as e:
            if method == "HEAD":
                continue
            return url, 0, str(getattr(e, "reason", e))[:80]
    return url, 0, "unknown"


def main():
    rows = list(csv.DictReader(open(ROOT / "tools.csv", encoding="utf-8")))
    urls = sorted({r["url"] for r in rows})
    names = {}
    for r in rows:
        names.setdefault(r["url"], r["name"])
    with ThreadPoolExecutor(max_workers=24) as ex:
        results = list(ex.map(check, urls))
    bad = [(u, s, m) for u, s, m in results if s == 0 or s >= 400 and m != "blocked"]
    blocked = [(u, s) for u, s, m in results if m == "blocked"]
    print(f"checked {len(urls)} urls: {len(bad)} dead/suspicious, {len(blocked)} bot-blocked")
    for u, s, m in sorted(bad):
        print(f"DEAD? [{s}] {names[u]} -> {u} {m}")
    if "--blocked" in sys.argv:
        for u, s in sorted(blocked):
            print(f"BLOCKED [{s}] {names[u]} -> {u}")


if __name__ == "__main__":
    main()
