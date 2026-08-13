# -*- coding: utf-8 -*-
"""
Local server for the desktop version of "זוכר שמות תלמידים".
Stdlib only — no pip install needed. Serves index.html and stores all app
data as a real file on disk (data/data.json) instead of the browser's
localStorage, which is capped at ~5MB.

Binds to 127.0.0.1 only — not reachable from other devices on the network.
"""
import http.server
import json
import os
import socketserver
import sys
import threading
import time
import webbrowser

PORT = 8733
HERE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(HERE, 'data')
DATA_FILE = os.path.join(DATA_DIR, 'data.json')


def read_data():
    if not os.path.exists(DATA_FILE):
        return {}
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def write_data(obj):
    os.makedirs(DATA_DIR, exist_ok=True)
    tmp_path = DATA_FILE + '.tmp'
    with open(tmp_path, 'w', encoding='utf-8') as f:
        json.dump(obj, f, ensure_ascii=False)
    os.replace(tmp_path, DATA_FILE)  # atomic — never leaves a half-written file


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=HERE, **kwargs)

    def log_message(self, fmt, *args):
        pass  # keep the console quiet

    def do_GET(self):
        if self.path.startswith('/data/') or self.path.endswith('.py'):
            self.send_response(403)
            self.end_headers()
            return
        if self.path == '/api/data':
            body = json.dumps(read_data(), ensure_ascii=False).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        super().do_GET()

    def do_POST(self):
        if self.path == '/api/data':
            length = int(self.headers.get('Content-Length', 0))
            raw = self.rfile.read(length)
            try:
                obj = json.loads(raw.decode('utf-8'))
            except json.JSONDecodeError:
                self.send_response(400)
                self.end_headers()
                return
            write_data(obj)
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"ok":true}')
            return
        self.send_response(404)
        self.end_headers()


def open_browser_when_ready():
    time.sleep(0.6)
    webbrowser.open(f'http://localhost:{PORT}')


if __name__ == '__main__':
    os.makedirs(DATA_DIR, exist_ok=True)
    print('========================================')
    print(' זוכר שמות תלמידים — גרסה מקומית')
    print(f' http://localhost:{PORT}')
    print(' לסגירה: סגור את החלון הזה (Ctrl+C)')
    print('========================================')
    threading.Thread(target=open_browser_when_ready, daemon=True).start()
    try:
        with socketserver.TCPServer(('127.0.0.1', PORT), Handler) as httpd:
            httpd.serve_forever()
    except OSError as e:
        print(f'\nשגיאה בהפעלת השרת על פורט {PORT}: {e}')
        print('ייתכן שהאפליקציה כבר פתוחה בחלון אחר — בדוק את הדפדפן.')
        input('לחץ Enter לסגירה...')
        sys.exit(1)
    except KeyboardInterrupt:
        pass
