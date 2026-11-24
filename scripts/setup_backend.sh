#!/usr/bin/env bash
# LegalBridge Informal — Backend Setup (macOS/Linux)
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$SCRIPT_DIR/../backend"

echo "============================================================"
echo " LegalBridge Informal — Backend Setup"
echo "============================================================"

cd "$BACKEND_DIR"

echo ""
echo "[1/6] Creating virtual environment..."
python3 -m venv venv

echo ""
echo "[2/6] Activating virtual environment..."
source venv/bin/activate

echo ""
echo "[3/6] Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "[4/6] Copying .env file..."
if [ ! -f .env ]; then
    cp ../.env.example .env
    echo ".env created — please edit it with your credentials."
else
    echo ".env already exists — skipping."
fi

echo ""
echo "[5/6] Running database migrations..."
python manage.py migrate

echo ""
echo "[6/6] Seeding sample legal data..."
python manage.py seed_legal_data || echo "WARNING: Seed data failed — run manually later."

echo ""
echo "============================================================"
echo " Setup complete!"
echo ""
echo " Next steps:"
echo " 1. Edit backend/.env with your API keys"
echo " 2. Run: python manage.py createsuperuser"
echo " 3. Run: python manage.py runserver"
echo " 4. Open: http://127.0.0.1:8000/admin/"
echo "============================================================"
