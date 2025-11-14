# Local hosting
```bash
# Create virtual environment
python -m venv .venv
# Install necessary modules 
pip install -r backend/requirements.txt
cd backend
python manage.py runserver # runs the development server locally
```

# For secure deployment 
Set the .env variables according to [env file](.env.example).

```bash
cp .env.example .env
# Generate key:
python -c "from django.core.management.utils import get_random_secret_key as g; print(g())"
# Put into .env DJANGO_SECRET_KEY=...
```