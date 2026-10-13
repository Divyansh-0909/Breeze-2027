"""Serve the bundled, isolated pilot after extracting the review ZIP. No npm required."""
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlsplit, unquote
import mimetypes
import os

ROOT = Path(__file__).resolve().parents[3]
PREVIEW = Path(__file__).resolve().parent
HTML = '''<!doctype html><html><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Gullyverse Stage 2A isolated rock preview</title>
<style>html,body,#root{height:100%;width:100%;margin:0;background:#737d87}
#label,#toolbar{position:absolute;color:#eceee8;font:12px system-ui;background:#14211be0;padding:10px;max-width:calc(100% - 40px)}
#label{top:12px;left:12px}#toolbar{bottom:12px;left:12px}
button{padding:6px;margin:3px;color:#eee;background:#283d31;border:1px solid #718a78}</style>
<div id="root"></div><script src="/pilot.js"></script></html>'''.encode()

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        path = unquote(urlsplit(self.path).path)
        try:
            if path == '/':
                data, kind = HTML, 'text/html; charset=utf-8'
            else:
                target = PREVIEW / 'pilot.js' if path == '/pilot.js' else (ROOT / 'public' / path.lstrip('/')).resolve()
                if target != PREVIEW / 'pilot.js' and not target.is_relative_to(ROOT / 'public'):
                    self.send_error(403)
                    return
                data = target.read_bytes()
                kind = {'.glb': 'model/gltf-binary', '.js': 'text/javascript', '.ttf': 'font/ttf'}.get(target.suffix, mimetypes.guess_type(str(target))[0] or 'application/octet-stream')
            self.send_response(200)
            self.send_header('Content-Type', kind)
            self.send_header('Content-Length', str(len(data)))
            self.end_headers()
            self.wfile.write(data)
        except (FileNotFoundError, IsADirectoryError):
            self.send_error(404)

if __name__ == '__main__':
    host, port = os.environ.get('PILOT_HOST', '127.0.0.1'), int(os.environ.get('PILOT_PORT', '3002'))
    print(f'Isolated pilot: http://{host}:{port} — default production experience unchanged', flush=True)
    ThreadingHTTPServer((host, port), Handler).serve_forever()
