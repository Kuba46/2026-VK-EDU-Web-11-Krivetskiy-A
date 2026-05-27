import json
from urllib.parse import parse_qs

def app(environ, start_response):
    method = environ.get('REQUEST_METHOD', 'GET').upper()
    query = parse_qs(environ.get('QUERY_STRING', ''), keep_blank_values=True)

    post_params = {}
    if method == 'POST':
        try:
            length = int(environ.get('CONTENT_LENGTH') or 0)
        except (TypeError, ValueError):
            length = 0
        body = environ['wsgi.input'].read(length).decode('utf-8') if length else ''
        post_params = parse_qs(body, keep_blank_values=True)

    payload = {
        'method': method,
        'get': {k: v for k, v in query.items()},
        'post': {k: v for k, v in post_params.items()},
    }

    response = json.dumps(payload, ensure_ascii=False, indent=2).encode('utf-8')
    headers = [
        ('Content-Type', 'application/json; charset=utf-8'),
        ('Content-Length', str(len(response))),
    ]
    start_response('200 OK', headers)
    return [response]
