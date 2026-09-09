"""Local HTTP backend and static frontend. Start with: python app.py"""
import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import engine

STATIC = Path(__file__).resolve().parent / 'static'


class Handler(BaseHTTPRequestHandler):
    def send(self, code, body, content_type='application/json; charset=utf-8'):
        if not isinstance(body, bytes):
            body = json.dumps(body).encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(body)))
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = self.path.split('?')[0]
        if path == '/api/status':
            return self.send(200, engine.status())
        assets = {'/': ('index.html', 'text/html'), '/app.js': ('app.js', 'text/javascript'), '/style.css': ('style.css', 'text/css')}
        if path not in assets:
            return self.send(404, {'error': 'Not found'})
        filename, mime = assets[path]
        self.send(200, (STATIC / filename).read_bytes(), mime + '; charset=utf-8')

    def do_POST(self):
        if self.path != '/api/generate':
            return self.send(404, {'error': 'Not found'})
        # Local same-origin application only; no permissive CORS.
        origin = self.headers.get('Origin')
        if origin and origin != 'http://' + self.headers.get('Host', ''):
            return self.send(403, {'error': 'Cross-origin request rejected'})
        try:
            if self.headers.get_content_type() != 'application/json':
                raise ValueError('Expected JSON request.')
            length = int(self.headers.get('Content-Length', '0'))
            if not 0 < length <= 20000:
                raise ValueError('Request is empty or too large.')
            data = json.loads(self.rfile.read(length))
            if not isinstance(data, dict):
                raise ValueError('Expected a JSON object.')
            result = engine.generate(data.get('text'), data.get('count', 10))
            self.send(200, result)
        except (ValueError, UnicodeDecodeError) as exc:
            self.send(400, {'error': str(exc)})
        except ImportError:
            self.send(503, {'error': 'Install dependencies with: python -m pip install -r requirements.txt'})
        except Exception as exc:
            print('Prediction error:', repr(exc))
            self.send(500, {'error': 'Could not load or run the model. Check the VS Code terminal for details. If loading fails, install the TensorFlow version recorded in models/config.json.'})


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=8000)
    args = parser.parse_args()
    server = ThreadingHTTPServer(('127.0.0.1', args.port), Handler)
    print(f'Next Word Studio: http://127.0.0.1:{args.port}', flush=True)
    print('Press Ctrl+C to stop. First prediction loads the model and may take a moment.', flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.server_close()
