# Benchmarks (ab/wrk)

Все размеры документов должны быть примерно одинаковыми. В качестве общего документа используется `ask_deltarune/static/sample.html`.

## Запуск gunicorn

### Django приложение (порт 8080)

```bash
.venv/bin/gunicorn -c deploy/gunicorn.conf.py
```

# WSGI скрипт с GET/POST (порт 8081)

```bash
.venv/bin/gunicorn -b 127.0.0.1:8081 wsgi_simple:app
```

# WSGI отдаёт статический файл (порт 8082)

```bash
.venv/bin/gunicorn -b 127.0.0.1:8082 wsgi_static:app
```

## Запуск nginx

```bash
cd 2026-VK-EDU-Web-11-Krivetskiy-A
nginx -c deploy/nginx.conf
```

## Измерения (5 сценариев)

**1. Статика напрямую через nginx**
```bash
ab -n 5000 -c 100 http://localhost/sample.html
```

**2. Статика напрямую через gunicorn**
```bash
ab -n 5000 -c 100 http://127.0.0.1:8082/sample.html
```

**3. Динамика напрямую через gunicorn**
```bash
ab -n 5000 -c 100 "http://127.0.0.1:8081/?foo=bar&baz=1"
```

**4. Динамика через nginx -> gunicorn**
```bash
ab -n 5000 -c 100 "http://localhost/?foo=bar&baz=1"
```

**5. Динамика через nginx -> gunicorn (proxy_cache)**
```bash
ab -n 5000 -c 100 "http://localhost/?foo=bar&baz=1"
```
