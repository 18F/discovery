web: python manage.py migrate --noinput && python manage.py createcachetable && python manage.py collectstatic --noinput && waitress-serve --expose-tracebacks --port=$PORT mirage.wsgi:application
