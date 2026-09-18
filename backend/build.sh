#!/usr/bin/env bash
# Optional EC2 build helper; it intentionally does not run seed.py.
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate
