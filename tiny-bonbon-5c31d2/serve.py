#!/usr/bin/env python3
"""Serve the archived Roblox snapshot with compression and cache headers."""

from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit
import argparse
import gzip
import mimetypes
import re

ROOT = Path(__file__).resolve().parent
COMPRESSIBLE = {"text/html", "text/css", "text/javascript", "application/javascript", "application/json", "image/svg+xml"}


class SnapshotHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def end_headers(self):
        self.send_header("X-Content-Type-Options", "nosniff")
        # The replay shim intentionally restores captured response bodies from
        # local static assets, so all external requests remain blocked by CSP.
        self.send_header("Cache-Control", "public, max-age=31536000, immutable" if "/assets/" in self.path else "no-cache")
        self.send_header("Vary", "Accept-Encoding")
        super().end_headers()

    def send_head(self):
        parsed = urlsplit(self.path)
        # The real Roblox Marketplace route is /catalog. Prefer the archived
        # canonical English capture, preserving /catalog's query string on-page.
        normalized_path = re.sub(r"/+$", "", parsed.path or "/") or "/"
        if normalized_path in ("/catalog", "/catalog.html"):
            requested = ROOT / "catalog.html"
        elif normalized_path == "/" and not (ROOT / "index.html").exists():
            requested = ROOT / "home.html"
        else:
            requested = Path(self.translate_path(self.path))
        if requested.is_dir():
            requested = requested / "index.html"
        try:
            stat = requested.stat()
            source = requested.open("rb")
        except OSError:
            self.send_error(404, "File not found")
            return None

        content_type = mimetypes.guess_type(str(requested))[0] or "application/octet-stream"
        can_compress = content_type.split(";", 1)[0] in COMPRESSIBLE
        wants_gzip = "gzip" in self.headers.get("Accept-Encoding", "").lower()

        if can_compress and wants_gzip:
            try:
                with source:
                    body = gzip.compress(source.read(), compresslevel=6, mtime=0)
            except OSError:
                self.send_error(500, "Could not read file")
                return None
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Encoding", "gzip")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Last-Modified", self.date_time_string(stat.st_mtime))
            self.end_headers()
            if self.command != "HEAD":
                self.wfile.write(body)
            return None

        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(stat.st_size))
        self.send_header("Last-Modified", self.date_time_string(stat.st_mtime))
        self.end_headers()
        if self.command == "HEAD":
            source.close()
            return None
        return source


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="127.0.0.1", help="bind address (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=3000, help="port (default: 3000)")
    args = parser.parse_args()

    server = ThreadingHTTPServer((args.host, args.port), SnapshotHandler)
    print(f"Serving {ROOT} at http://{args.host}:{args.port} (Ctrl+C to stop)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
