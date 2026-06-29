# release: npm install && npm run build && python3 -m ensurepip --upgrade && python3 -m pip install --no-cache-dir -r requirements.txt && python3 manage.py migrate && python3 manage.py collectstatic --noinput
web: python manage.py migrate && gunicorn coinductor.wsgi
