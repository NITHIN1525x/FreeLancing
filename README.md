# FreeLance Marketplace

A full-stack freelance marketplace with a database-backed escrow workflow. Payments and balances are stored and managed by Django; no blockchain, cryptocurrency wallet, or MetaMask account is required.

## Features

- Role-based client and freelancer accounts
- Job posting, browsing, and proposal acceptance
- Database-backed project escrow
- Work submission, revision requests, and approval
- Freelancer balance credit when the client approves completed work
- Project chat, disputes, and admin resolution

## Payment workflow

1. A client accepts a proposal, creating a project with a pending payment.
2. The client locks the project amount in the platform escrow.
3. The freelancer submits work.
4. The client approves the submission; the project is marked complete and the freelancer balance is credited in the database.

The API validates each transition and uses database transactions for locking and releasing payments, preventing duplicate releases.

## Setup

### Backend

```bash
cd backend
python -m venv venv
# macOS/Linux
source venv/bin/activate
# Windows
# venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python seed.py
python manage.py runserver
```

The backend runs at `http://127.0.0.1:8000`.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The frontend runs at `http://localhost:5173`.

## Project payment endpoints

- `GET /api/projects/`
- `GET /api/projects/{id}/`
- `POST /api/projects/{id}/lock-payment/`
- `POST /api/projects/{id}/submit-work/`
- `POST /api/projects/{id}/request-revision/`
- `POST /api/projects/{id}/approve/`
