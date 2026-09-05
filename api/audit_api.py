"""Private API for the opt-in FiveM audit starter. Python 3 standard library only."""
import argparse, json, os, secrets, sys
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

SESSIONS = {}
SECRET = ''
DATA = Path('data/reports')
def body(request):
    n = int(request.headers.get('Content-Length', '0'))
    if n > 1_000_000: raise ValueError('Body too large')
    return json.loads(request.rfile.read(n))
def code(): return secrets.token_hex(4).upper()[:4] + '-' + secrets.token_hex(4).upper()[:4]
class Api(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args): print(fmt % args)
    def send_json(self, status, value):
        raw=json.dumps(value).encode(); self.send_response(status); self.send_header('Content-Type','application/json'); self.send_header('Content-Length',str(len(raw))); self.end_headers(); self.wfile.write(raw)
    def authorized(self): return secrets.compare_digest(self.headers.get('X-Server-Secret',''), SECRET)
    def do_POST(self):
        try:
            data=body(self)
            if self.path == '/sessions':
                if not self.authorized(): return self.send_json(401, {'error':'unauthorized'})
                c=code(); SESSIONS[c]={'createdAt':datetime.now(timezone.utc).isoformat(),'player':data.get('player','unknown'),'received':False}; return self.send_json(201, {'code':c})
            if self.path == '/reports':
                c=data.get('playerCode','')
                if c not in SESSIONS: return self.send_json(404, {'error':'unknown or expired player code'})
                DATA.mkdir(parents=True,exist_ok=True); (DATA / (c + '.json')).write_text(json.dumps(data,indent=2), encoding='utf-8'); SESSIONS[c]['received']=True
                return self.send_json(201, {'ok':True})
            return self.send_json(404, {'error':'not found'})
        except (ValueError, json.JSONDecodeError) as e: self.send_json(400, {'error':str(e)})
    def do_GET(self):
        if self.path == '/admin/scans':
            if not self.authorized(): return self.send_json(401, {'error':'unauthorized'})
            return self.send_json(200, [{'code': c, **v} for c, v in SESSIONS.items()])
        if self.path.startswith('/status/'):
            if not self.authorized(): return self.send_json(401, {'error':'unauthorized'})
            c=self.path.rsplit('/',1)[-1]; return self.send_json(200, SESSIONS.get(c, {'error':'not found'}))
        if self.path == '/':
            raw = Path(__file__).with_name('dashboard.html').read_bytes()
            self.send_response(200); self.send_header('Content-Type', 'text/html; charset=utf-8'); self.send_header('Content-Length', str(len(raw))); self.end_headers(); return self.wfile.write(raw)
        self.send_json(404, {'error':'not found'})
if __name__ == '__main__':
    p=argparse.ArgumentParser(); p.add_argument('--secret', default=os.getenv('AUDIT_SECRET')); p.add_argument('--port',type=int,default=int(os.getenv('PORT', '8080'))); p.add_argument('--host', default='127.0.0.1'); a=p.parse_args(); SECRET=a.secret
    if not SECRET: p.error('Set AUDIT_SECRET or pass --secret.')
    print('Private audit API listening. Put it behind HTTPS before public deployment.')
    ThreadingHTTPServer((a.host,a.port),Api).serve_forever()
