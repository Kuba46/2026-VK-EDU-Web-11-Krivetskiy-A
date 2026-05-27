from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
STATIC_FILE = BASE_DIR / 'ask_krivetskiy' / 'static' / 'sample.html'


def app(environ, start_response):
    content = STATIC_FILE.read_bytes() if STATIC_FILE.exists() else b''
    headers = [
        ('Content-Type', 'text/html; charset=utf-8'),
        ('Content-Length', str(len(content))),
    ]
    start_response('200 OK', headers)
    return [content]
