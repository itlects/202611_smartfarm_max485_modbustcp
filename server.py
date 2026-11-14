"""Python 3.13 classroom server. Hardware mode requires MySQL; demo is explicit."""
import os, json, time, secrets, hashlib, hmac, threading
from pathlib import Path
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from http.cookies import SimpleCookie
from modbus import Gateway

DEMO = os.getenv('FARM_MODE', 'hardware') == 'demo'
USER = os.getenv('FARM_USER', 'smartfarm2026')
SALT = secrets.token_bytes(16)
PASSWORD = hashlib.scrypt(os.getenv('FARM_PASSWORD', 'smartfarm1234').encode(), salt=SALT, n=16384, r=8, p=1)
sessions = {}
session_lock = threading.Lock()
state_lock = threading.RLock()
gateway = Gateway(os.getenv('ESP32_HOST', '192.168.1.50'))
state = {u: {'unit': u, 'online': False, 'registers': [], 'time': None} for u in (1, 2)}
demo_regs = {u: [650, 25, 0, 0, 0, 0, 0, 0] for u in (1, 2)}
demo_until = 0

def database():
    import pymysql
    return pymysql.connect(host=os.getenv('DB_HOST', '127.0.0.1'), user=os.getenv('DB_USER', 'smartfarm'), password=os.environ['DB_PASSWORD'], database='smartfarm', charset='utf8mb4', autocommit=True)

def save(kind, unit, payload):
    if DEMO:
        return
    with database() as db, db.cursor() as cur:
        cur.execute('INSERT INTO events(kind,unit,payload) VALUES(%s,%s,%s)', (kind, unit, json.dumps(payload)))

def poll():
    global demo_until
    while True:
        for u in (1, 2):
            try:
                with state_lock:
                    if DEMO and demo_until and time.monotonic() >= demo_until:
                        demo_regs[2][4] = 0
                        demo_until = 0
                    regs = list(demo_regs[u]) if DEMO else gateway.read(u)
                    save('sample', u, regs)
                    state[u] = {'unit': u, 'online': True, 'registers': regs, 'time': time.time()}
            except Exception as exc:
                with state_lock:
                    state[u] = {'unit': u, 'online': False, 'registers': [], 'time': time.time(), 'error': str(exc)}
        time.sleep(2)

class Handler(BaseHTTPRequestHandler):
    def send(self, code, data, cookie=None):
        body = json.dumps(data, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Cache-Control', 'no-store')
        self.send_header('Content-Length', str(len(body)))
        if cookie:
            self.send_header('Set-Cookie', cookie)
        self.end_headers()
        self.wfile.write(body)

    def authorized(self):
        try:
            c = SimpleCookie(self.headers.get('Cookie', ''))
            token = c['farm'].value
            with session_lock:
                return sessions.get(token, 0) > time.time()
        except (KeyError, ValueError):
            return False

    def do_GET(self):
        if self.path == '/':
            body = (Path(__file__).parent/'web/index.html').read_bytes()
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif not self.authorized():
            self.send(401, {'error': '로그인이 필요합니다'})
        elif self.path == '/api/state':
            with state_lock:
                self.send(200, {'mode': 'demo' if DEMO else 'hardware', 'nodes': list(state.values())})
        elif self.path == '/api/history':
            if DEMO:
                self.send(200, {'rows': [], 'mode': 'demo'})
            else:
                try:
                    with database() as db, db.cursor() as cur:
                        cur.execute('SELECT id,kind,unit,payload,CAST(created_at AS CHAR) FROM events ORDER BY id DESC LIMIT 100')
                        self.send(200, {'rows': cur.fetchall()})
                except Exception:
                    self.send(503, {'error': 'DB 연결 오류'})
        else:
            self.send(404, {'error': 'Not found'})

    def do_POST(self):
        global demo_until
        # Reject cross-site form submissions; no CORS and JSON only.
        if self.headers.get('Content-Type', '').split(';')[0] != 'application/json':
            return self.send(415, {'error': 'JSON required'})
        try:
            size = int(self.headers.get('Content-Length', '0'))
            if not 0 < size <= 1024:
                raise ValueError()
            data = json.loads(self.rfile.read(size))
            if not isinstance(data, dict):
                raise ValueError()
        except (ValueError, json.JSONDecodeError):
            return self.send(400, {'error': 'Invalid JSON'})
        if self.path == '/api/login':
            supplied = hashlib.scrypt(str(data.get('password', '')).encode(), salt=SALT, n=16384, r=8, p=1)
            if data.get('username') != USER or not hmac.compare_digest(supplied, PASSWORD):
                return self.send(401, {'error': '계정 또는 암호 확인'})
            token = secrets.token_urlsafe(32)
            with session_lock:
                now = time.time()
                for k in list(sessions):
                    if sessions[k] < now:
                        del sessions[k]
                if len(sessions) >= 200:
                    return self.send(429, {'error': '세션 한도'})
                sessions[token] = now + 28800
            return self.send(200, {'ok': True}, f'farm={token}; HttpOnly; SameSite=Strict; Path=/; Max-Age=28800')
        if not self.authorized():
            return self.send(401, {'error': '로그인이 필요합니다'})
        if self.path != '/api/control':
            return self.send(404, {'error': 'Not found'})
        try:
            unit, address, value = data['unit'], data['address'], data['value']
            if any(type(v) is not int for v in (unit, address, value)):
                raise ValueError()
            limits = {3: 3, 4: 1, 5: 1, 6: 100, 7: 1}
            if unit not in (1, 2) or address not in limits or not 0 <= value <= limits[address] or (unit == 1 and address in (4, 5, 7)):
                raise ValueError()
            with state_lock:
                # Audit intent before any hardware mutation; never send if DB is down.
                save('requested', unit, data)
                if DEMO:
                    demo_regs[unit][address] = value
                    if address == 4:
                        demo_until = time.monotonic()+10 if value else 0
                else:
                    gateway.write(unit, address, value)
                save('acknowledged', unit, data)
            self.send(200, {'ok': True, 'message': '명령 확인됨; 실제 상태는 다음 조회에서 확인'})
        except (KeyError, ValueError):
            self.send(400, {'error': '허용되지 않은 제어값'})
        except Exception:
            self.send(503, {'error': '통신/DB 오류. 명령 결과 불확실; 상태를 확인하세요'})

if __name__ == '__main__':
    if not DEMO:
        with database() as db, db.cursor() as cur:
            cur.execute('SELECT VERSION()')
            print('MySQL:', cur.fetchone()[0])
    threading.Thread(target=poll, daemon=True).start()
    print('Mode:', 'demo' if DEMO else 'hardware', 'URL: http://localhost:8000')
    ThreadingHTTPServer((os.getenv('FARM_BIND', '127.0.0.1'), 8000), Handler).serve_forever()
