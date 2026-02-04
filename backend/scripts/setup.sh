#!/usr/bin/env bash
set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

cd "$PROJECT_ROOT"

echo "[1/5] Creating virtual environment..."
python3 -m venv .venv

source .venv/bin/activate

pip install --upgrade pip

echo "[2/5] Installing dependencies..."
pip install -r requirements.txt

echo "[3/5] Running migrations..."
# Note: Migrations should be pre-generated and committed.
# Run 'python manage.py makemigrations' manually if creating new migrations.
python manage.py migrate

echo "[4/5] Collecting static files..."
python manage.py collectstatic --noinput

echo "[5/5] Setup complete."

echo "\nOptional: Create a superuser"
if [[ -n "$DJANGO_SUPERUSER_EMAIL" && -n "$DJANGO_SUPERUSER_USERNAME" && -n "$DJANGO_SUPERUSER_PASSWORD" ]]; then
  python manage.py createsuperuser --noinput || true
  echo "Superuser created: $DJANGO_SUPERUSER_USERNAME"
else
  echo "Set DJANGO_SUPERUSER_EMAIL, DJANGO_SUPERUSER_USERNAME, DJANGO_SUPERUSER_PASSWORD to auto-create a superuser."
fi

echo "\nOptional: Populate sample data"
read -p "Do you want to populate sample data? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
  python manage.py populate_sample_data --articles 20
  echo "Sample data created successfully."
fi

echo "\n✅ Setup complete! Next steps:"
echo "1. Create superuser: python manage.py createsuperuser"
echo "2. Run server: python manage.py runserver"
echo "3. Access admin: http://127.0.0.1:8000/admin/"
echo "4. Access API: http://127.0.0.1:8000/api/"
