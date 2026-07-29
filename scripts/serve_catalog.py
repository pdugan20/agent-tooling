#!/usr/bin/env python3
"""Serve the local catalog without browser caching during UI iteration."""

from __future__ import annotations

import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import IO

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


class NoCacheRequestHandler(SimpleHTTPRequestHandler):
    """Serve catalog assets with headers that force browsers to revalidate."""

    def send_head(self) -> IO[bytes] | None:
        # SimpleHTTPRequestHandler otherwise returns 304 for conditional
        # requests, which can leave an already-open browser tab on stale assets.
        for header in ("If-Modified-Since", "If-None-Match"):
            if header in self.headers:
                del self.headers[header]
        return super().send_head()

    def end_headers(self) -> None:
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        super().end_headers()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bind", default="127.0.0.1")
    parser.add_argument("--port", default=4173, type=int)
    args = parser.parse_args()

    handler = partial(NoCacheRequestHandler, directory=REPOSITORY_ROOT)
    server = ThreadingHTTPServer((args.bind, args.port), handler)
    print(f"Serving catalog at http://{args.bind}:{args.port}/catalog/", flush=True)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
