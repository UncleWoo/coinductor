release: npm install && npm run build && python manage.py migrate && python manage.py collectstatic --noinput
web: gunicorn coinductor.wsgi
