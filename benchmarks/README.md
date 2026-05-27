# Benchmarks (ab/wrk)

Все размеры документов должны быть примерно одинаковыми. В качестве общего документа используется `ask_krivetskiy/static/sample.html`.

## Запуск gunicorn

```bash
# Django приложение (порт 8000)
.venv/bin/gunicorn -c deploy/gunicorn.conf.py

# WSGI скрипт с GET/POST (порт 8081)
.venv/bin/gunicorn -b 127.0.0.1:8081 wsgi_simple:app

# WSGI отдаёт статический файл (порт 8082)
.venv/bin/gunicorn -b 127.0.0.1:8082 wsgi_static:app
```

## Запуск nginx

```bash
nginx -c /Users/ikuba46/VK Education/1 Term/WebDev/2026-VK-EDU-Web-11-Krivetskiy-A/deploy/nginx.conf
```

## Измерения (5 сценариев)

```bash
# 1) Статика напрямую через nginx
ab -n 5000 -c 100 http://localhost/sample.html

# 2) Статика напрямую через gunicorn
ab -n 5000 -c 100 http://127.0.0.1:8082/sample.html

# 3) Динамика напрямую через gunicorn
ab -n 5000 -c 100 "http://127.0.0.1:8081/?foo=bar&baz=1"

# 4) Динамика через nginx -> gunicorn
ab -n 5000 -c 100 "http://localhost/?foo=bar&baz=1"

# 5) Динамика через nginx -> gunicorn (proxy_cache)
ab -n 5000 -c 100 "http://localhost/?foo=bar&baz=1"
```

## Результаты

Скопируй вывод `ab`/`wrk` в файл `benchmarks/results.txt`.
