release: npm install && npm run build && python3 manage.py migrate && python3 manage.py collectstatic --noinput
web: gunicorn coinductor.wsgi
