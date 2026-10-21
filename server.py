#!/usr/bin/env python3
# Minimal static server with HTTP Range support (needed for video seeking).
import os
import re
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

ROOT = os.path.dirname(os.path.abspath(__file__))
PORT = 8780


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=ROOT, **kwargs)

    def do_GET(self):
        path = self.translate_path(self.path)
        if os.path.isdir(path):
            return super().do_GET()
        if not os.path.isfile(path):
            self.send_error(404)
            return

        size = os.path.getsize(path)
        start, end = 0, size - 1
        code = 200
        header = self.headers.get('Range')
        if header:
            m = re.match(r'bytes=(\d*)-(\d*)', header)
            if m:
                if m.group(1):
                    start = int(m.group(1))
                if m.group(2):
                    end = int(m.group(2))
                end = min(end, size - 1)
                code = 206

        if start > end or start >= size:
            self.send_error(416)
            return

        length = end - start + 1
        self.send_response(code)
        self.send_header('Content-Type', self.guess_type(path))
        self.send_header('Accept-Ranges', 'bytes')
        self.send_header('Content-Length', str(length))
        if code == 206:
            self.send_header('Content-Range', 'bytes %d-%d/%d' % (start, end, size))
        self.end_headers()

        with open(path, 'rb') as f:
            f.seek(start)
            remaining = length
            while remaining > 0:
                chunk = f.read(min(65536, remaining))
                if not chunk:
                    break
                try:
                    self.wfile.write(chunk)
                except (BrokenPipeError, ConnectionResetError):
                    break
                remaining -= len(chunk)

    def log_message(self, *args):
        pass


if __name__ == '__main__':
    print('')
    print('  GUICHU DECK  →  http://localhost:%d/' % PORT)
    print('  关闭这个窗口即停止服务')
    print('')
    ThreadingHTTPServer(('127.0.0.1', PORT), Handler).serve_forever()
