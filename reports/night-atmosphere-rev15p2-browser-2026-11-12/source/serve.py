from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlsplit,unquote
import sys
R=Path(__file__).resolve().parents[1];B=R.parent/'night-atmosphere-rev15p-pilot-2026-11-11'
class Handler(SimpleHTTPRequestHandler):
 def translate_path(self,path):
  p=unquote(urlsplit(path).path)
  if p.startswith('/vendor/three/'):base=R/'viewer/vendor/three';rel=p.removeprefix('/vendor/three/')
  elif p.startswith('/baseline/'):base=B/'viewer';rel=p.removeprefix('/baseline/') or 'index.html'
  else:base=R/'viewer';rel=p.lstrip('/') or 'index.html'
  result=(base/rel).resolve();return str(result) if result.is_relative_to(base.resolve()) else '/nonexistent'
 def end_headers(self):self.send_header('Cache-Control','no-store');super().end_headers()
ThreadingHTTPServer(('127.0.0.1',int(sys.argv[1]) if len(sys.argv)>1 else 8767),Handler).serve_forever()
