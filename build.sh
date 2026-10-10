
#!/usr/bin/env bash
set -o errexit

cd todo

pip install -r requirement.txt
python manage.py collectstatic --no-input
python manage.py migrate
python manage.py spectacular --file schema.yaml