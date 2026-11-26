"""Local preview that behaves like the live site on Vercel.

    python3 tools/serve.py          # then open http://localhost:8000

- Clean URLs: /works/young-virtuoso-i serves works/young-virtuoso-i.html, and
  a request ending in .html redirects to the clean address.
- Sends the headers from vercel.json (security policy included), so problems
  show up here before they reach the live site.
- Missing pages get 404.html with a 404 status.
"""
import http.server
import json
import os
import sys
from urllib.parse import urlsplit

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
os.chdir(ROOT)
with open("vercel.json") as f:
    HEADERS = [(h["key"], h["value"]) for rule in json.load(f)["headers"] for h in rule["headers"]]


class Handler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        for k, v in HEADERS:
            if k != "Strict-Transport-Security":  # HTTPS-only; meaningless on localhost
                self.send_header(k, v)
        super().end_headers()

    def do_GET(self):
        parts = urlsplit(self.path)
        path = parts.path
        if path.startswith("/_vercel/"):  # Vercel Analytics exists only on the live site
            self.send_response(200)
            self.send_header("Content-Type", "application/javascript")
            self.end_headers()
            return
        if path.endswith(".html") and path != "/404.html":
            clean = path[:-5]
            clean = clean[:-5] if clean.endswith("index") else clean
            self.send_response(308)
            self.send_header("Location", clean + (f"?{parts.query}" if parts.query else ""))
            self.end_headers()
            return
        local = path.lstrip("/")
        if path != "/" and os.path.isfile(local.rstrip("/") + ".html") and not os.path.isfile(local):
            self.path = "/" + local.rstrip("/") + ".html" + (f"?{parts.query}" if parts.query else "")
        elif path != "/" and not os.path.exists(local):
            self.send_response(404)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            with open("404.html", "rb") as f:
                self.wfile.write(f.read())
            return
        super().do_GET()


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    print(f"Previewing on http://localhost:{port}")
    http.server.ThreadingHTTPServer(("", port), Handler).serve_forever()
