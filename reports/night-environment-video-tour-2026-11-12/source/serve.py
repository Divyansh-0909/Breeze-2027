from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import unquote,urlsplit
import sys
R=Path(__file__).resolve().parents[1]/'viewer'
class Handler(SimpleHTTPRequestHandler):
 def translate_path(self,path):
  rel=unquote(urlsplit(path).path).lstrip('/') or 'index.html';p=(R/rel).resolve()
  return str(p) if p.is_relative_to(R.resolve()) else '/nonexistent'
 def end_headers(self):self.send_header('Cache-Control','no-store');super().end_headers()
ThreadingHTTPServer(('127.0.0.1',int(sys.argv[1]) if len(sys.argv)>1 else 8771),Handler).serve_forever()
