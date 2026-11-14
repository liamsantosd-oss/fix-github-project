#!/usr/bin/env python3
"""Check local references in this static Roblox archive without opening a browser."""
from __future__ import annotations

from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
import argparse
import re
import sys

ROOT = Path(__file__).resolve().parent
SKIP_PREFIXES = ("data:", "blob:", "javascript:", "mailto:", "tel:", "//", "http:", "https:")


class References(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.items: list[tuple[str, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs = dict(attrs)
        for name in ("src", "href", "poster", "action"):
            value = attrs.get(name)
            if value:
                self.items.append((name, value.strip()))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--quiet", action="store_true", help="only print failures and summary")
    args = parser.parse_args()

    html_files = sorted(ROOT.glob("*.html"))
    missing: list[tuple[Path, str, str]] = []
    checked = 0
    for html_file in html_files:
        tree = References()
        try:
            tree.feed(html_file.read_text(encoding="utf-8", errors="replace"))
        except OSError as exc:
            missing.append((html_file, "read", str(exc)))
            continue
        for attribute, raw in tree.items:
            if raw.startswith(SKIP_PREFIXES) or raw.startswith("#"):
                continue
            # Ignore templated values and whitespace-only URLs rather than treating them as paths.
            if not raw or "{{" in raw or "}}" in raw:
                continue
            parts = urlsplit(raw)
            if parts.scheme or parts.netloc:
                continue
            path = unquote(parts.path)
            if not path:
                continue
            checked += 1
            target = (html_file.parent / path).resolve()
            try:
                target.relative_to(ROOT)
            except ValueError:
                missing.append((html_file, attribute, raw + " (outside archive)"))
                continue
            if not target.is_file():
                missing.append((html_file, attribute, raw))

    print(f"Scanned {len(html_files)} HTML pages; checked {checked} local references.")
    if missing:
        counts = Counter((item[1], item[2]) for item in missing)
        print(f"Found {len(missing)} missing/unreadable references ({len(counts)} unique):")
        for page, attribute, value in missing[:100]:
            print(f"  {page.relative_to(ROOT)} [{attribute}] {value}")
        if len(missing) > 100:
            print(f"  ... and {len(missing) - 100} more")
        return 1
    print("All checked local src/href/poster/action references resolve.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
