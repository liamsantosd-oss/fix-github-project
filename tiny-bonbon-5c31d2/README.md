# tiny-bonbon-5c31d2

A static, locally archived snapshot of Roblox pages. This is not a live Roblox client: login, purchase, account, and other server-backed actions need Roblox's online services and are not provided by this archive.

## Pages
- `home.html` — archived Roblox landing page.
- `index.html` — archived Robux purchase page (the server root `/` serves this file by default).
- `/catalog` is served from `catalog.html`, matching the original Roblox Marketplace URL. The capture remains static and does not provide live Roblox services.
- Other root-level HTML files — archived localized, catalog, chart, login, and support pages.

## Run locally
Requires Python 3.8+; no package installation or build step is needed.

```bash
python3 serve.py
```

Then open <http://localhost:3000/>. To open the landing capture, visit <http://localhost:3000/home.html>.

Alternatively, run `python3 -m http.server 3000` from this directory.

## Performance notes
The repository contains many captured pages and assets (about 200 MB total). Only files referenced by the page you open need to be requested by the browser, but some archived pages embed large asset maps and substantial scripts. For smaller clones, keep the exact page(s) and assets you need.

## Troubleshooting
- If a local image is missing on Linux, filenames are case-sensitive; keep asset references lowercase to match the files in `assets/`.
- If a route or button needs live Roblox data or authentication, use the official Roblox website; this archive is read-only capture content.
- The archived Android app-promotion bumper is removed from captured pages.
- Run `python3 check_archive.py` to check that local `src`, `href`, `poster`, and `action` references in all root HTML snapshots resolve to files. The checker skips external URLs, fragments, and embedded data URLs.
