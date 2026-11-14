# RGO.md

## Stack
Static archived Roblox page snapshots served by Python 3 built-in threaded HTTP server via serve.py; gzip and cache headers. No app build toolchain or backend.

## Data model
None; static archived HTML, assets and captured response mappings only.

## Routing / surface
/ → index.html archived Robux purchase snapshot; /<page>.html → localized, category, and other captured pages; relative assets served from assets/.

## Invariants (DO NOT VIOLATE)
_(empty)_

## Recent changes (last 10)
- 2026-11-14: Removed the captured Android app-promotion bumper from 90 static pages and hid it on download snapshots; mapped /catalog to the archived marketplace page, preserving query strings. Verified HTTP 200 for /catalog and its captured query URL; archive references and replay shims still pass checks.
- 2026-11-14: Added an offline archive reference checker and enhanced replay shims in all 101 snapshots to match recorded responses despite query-order differences or changing sessionId/requestId values; preserved exact match behavior.
- 2026-11-14: Added compressed threaded static serving, README and .gitignore; fixed case-sensitive asset paths across 101 snapshots. Verified local asset references resolve.
- 2026-11-14: Made the public GitHub snapshot serve over HTTP on port 3000; it returns HTTP 200 for the root page.
