# Quick Start Guide

Get NewsHub backend running in 5 minutes.

## Prerequisites
- Python 3.11+
- pip

## Steps

### 1. Clone and Navigate
```bash
cd backend
```

### 2. Create Virtual Environment
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Setup Environment
```bash
cp .env.example .env
```

### 5. Run Migrations
```bash
python manage.py migrate
```

### 6. Create Superuser
```bash
python manage.py createsuperuser
```

### 7. (Optional) Load Sample Data
```bash
python manage.py populate_sample_data --articles 20
```

### 8. Start Server
```bash
python manage.py runserver
```

## Access Points
- **API:** http://127.0.0.1:8000/api/
- **Admin:** http://127.0.0.1:8000/admin/
- **API Docs:** See `docs/API.md`

## Next Steps
- Explore API endpoints in Postman (import `docs/NewsHub.postman_collection.json`)
- Create articles via Django Admin
- Test frontend integration
