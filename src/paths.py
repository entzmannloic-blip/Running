# -*- coding: utf-8 -*-
"""Chemins du pipeline : valables sous Windows, Linux et en CI.

WORK  = dossier de travail du build (copie de src/ + fichiers generes).
        Defaut : <depot>/build (ignore par Git). Surchargeable par RUNNING_WORK.
SITE  = WORK/site : le site tel qu'il sera publie (index.html, data/*.json,
        src/app.js, sw.js, manifest, icones). C'est ce que servent les tests.
"""
import functools
import os
import threading
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
WORK = os.environ.get("RUNNING_WORK") or os.path.join(ROOT, "build")
SITE = os.path.join(WORK, "site")
OUT_HTML = os.path.join(SITE, "index.html")
DATA_JSON = os.path.join(WORK, "data.json")

_server = None


class _Handler(SimpleHTTPRequestHandler):
    extensions_map = dict(SimpleHTTPRequestHandler.extensions_map, **{
        ".js": "text/javascript", ".json": "application/json", ".html": "text/html; charset=utf-8",
        ".webmanifest": "application/manifest+json",
    })

    def log_message(self, *args):
        pass

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()


def html_url():
    """Sert SITE sur http://127.0.0.1:<port>/ (fetch et service worker exigent http, pas file://)."""
    global _server
    if _server is None:
        handler = functools.partial(_Handler, directory=SITE)
        _server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
        threading.Thread(target=_server.serve_forever, daemon=True).start()
    return f"http://127.0.0.1:{_server.server_address[1]}/index.html"


def site_text():
    """Tout ce que le site expedie en texte : index.html + app.js + data/*.json."""
    parts = []
    for rel in ["index.html", os.path.join("src", "app.js")]:
        p = os.path.join(SITE, rel)
        if os.path.exists(p):
            parts.append(open(p, encoding="utf-8").read())
    d = os.path.join(SITE, "data")
    if os.path.isdir(d):
        for name in sorted(os.listdir(d)):
            parts.append(open(os.path.join(d, name), encoding="utf-8").read())
    return "\n".join(parts)
