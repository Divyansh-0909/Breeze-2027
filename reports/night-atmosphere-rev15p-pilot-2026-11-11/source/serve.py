"""Loopback-only viewer; explicit vendor allowlist, no repository/web app serving."""
from pathlib import Path
import sys
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlsplit,unquote
R=Path(__file__).resolve().parents[1];VENDOR=R/'viewer/vendor/three' if (R/'viewer/vendor/three').exists() else R.parents[1]/'node_modules/three'
class Handler(SimpleHTTPRequestHandler):
 def translate_path(self,path):
  path=unquote(urlsplit(path).path)
  base=VENDOR if path.startswith('/vendor/three/') else R/'viewer'
  rel=path.removeprefix('/vendor/three/') if base==VENDOR else path.lstrip('/') or 'index.html'
  result=(base/rel).resolve()
  return str(result) if result.is_relative_to(base.resolve()) else '/nonexistent'
 def end_headers(self):
  self.send_header('Cache-Control','no-store');super().end_headers()
ThreadingHTTPServer(('127.0.0.1',int(sys.argv[1]) if len(sys.argv)>1 else 8765),Handler).serve_forever()
