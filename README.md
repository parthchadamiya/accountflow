# AccountFlow — Finance Management System

A full-stack account management web application built with **Python Django** and a modern dark glassmorphism UI.

## Tech Stack

- **Backend:** Django 5.2, Django REST Framework, SimpleJWT
- **Database:** PostgreSQL (via psycopg2)
- **Frontend:** Tailwind CSS (Play CDN), Alpine.js, Lucide Icons, Chart.js
- **Auth:** Django session-based authentication with custom User model

## Project Structure

```
account-app/
├── config/                  ← Django settings & root URLs
│   ├── settings.py
│   └── urls.py
├── authentication/          ← Login / Logout / Custom User model
├── clients/                 ← Client CRUD
├── transactions/            ← Money transfers between clients
├── dashboard/               ← Overview stats & charts
├── reports/                 ← Trial Balance & Party Ledger
├── templates/               ← All HTML templates
├── static/                  ← Static files
├── .env                     ← Environment variables (DB credentials)
├── requirements.txt
└── manage.py
```

## Main Features

- Login with user code and password
- Dashboard with client count, debit/credit totals, balance, chart, and recent transactions
- Client create, list, view, update, and delete (with search)
- Transaction creation between sender and receiver clients
- Automatic balance update on sender and receiver (overdraft allowed — balance can go negative)
- Transaction list and transaction detail
- **Trial Balance report** — negative balances on DR (left), positive on CR (right), side-by-side with totals
- **Party Ledger report** — per-client statement with opening balance, transactions in date range, and closing balance

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure environment variables

Create a `.env` file in the project root:

```env
DATABASE_NAME=account
DATABASE_USER=postgres
DATABASE_PASSWORD=postgres
DATABASE_HOST=127.0.0.1
```

### 3. Run migrations

```bash
python manage.py migrate
```

### 4. Seed default admin and sample data

```bash
python manage.py seed
```

### 5. Start the development server

```bash
python manage.py runserver
```

The app runs at:

```
http://localhost:8000
```

## Default Login

```
Code:     ADMIN001
Password: Admin@123
```

## Database Models

### User
| Field | Type | Notes |
|-------|------|-------|
| id | Auto | Primary key |
| name | CharField | Full name |
| code | CharField | Unique — used as login username |
| email | EmailField | Optional |
| password | CharField | Hashed by Django |
| role | CharField | `ADMIN` or `STAFF` |
| created_at | DateTimeField | Auto |

### Client
| Field | Type | Notes |
|-------|------|-------|
| id | Auto | Primary key |
| client_name | CharField | |
| code | CharField | Unique |
| mobile | CharField | Optional |
| email | EmailField | Optional |
| address | TextField | Optional |
| opening_balance | DecimalField | Set on creation |
| current_balance | DecimalField | Updated on every transaction |
| status | CharField | `ACTIVE` or `INACTIVE` |
| created_by / updated_by | FK → User | |

### Transaction
| Field | Type | Notes |
|-------|------|-------|
| id | Auto | Primary key |
| amount | DecimalField | |
| type | CharField | Always `DEBIT` |
| description | TextField | Optional |
| transaction_date | DateField | |
| sender_client | FK → Client | Balance decremented |
| receiver_client | FK → Client | Balance incremented |
| created_by | FK → User | |

## Frontend Routes

| Route | Auth | Description |
|-------|------|-------------|
| `/login/` | No | Login page |
| `/dashboard/` | Yes | Dashboard overview |
| `/clients/` | Yes | Client list with search |
| `/clients/create/` | Yes | Add new client |
| `/clients/<id>/` | Yes | Client detail + transactions |
| `/clients/<id>/update/` | Yes | Edit client |
| `/clients/<id>/delete/` | Yes | Delete client |
| `/transactions/` | Yes | All transactions |
| `/transactions/create/` | Yes | New transfer |
| `/transactions/<id>/` | Yes | Transaction detail |
| `/reports/trial-balance/` | Yes | Trial balance (CR / DR) |
| `/reports/party-ledger/` | Yes | Party ledger by date range |
| `/admin/` | Staff | Django admin panel |

## Reports

### Trial Balance (`/reports/trial-balance/`)
Lists all clients side-by-side:
- **DR (left):** clients with **negative** current balance
- **CR (right):** clients with **positive** current balance
- Totals shown separately at the bottom

### Party Ledger (`/reports/party-ledger/`)
Parameters: **Client Code**, **Start Date**, **End Date**
- Shows **opening balance** (balance before start date)
- Lists all transactions in the date range with credit, debit, and running balance columns
- Shows **closing balance** at the bottom

## Transaction Balance Rules

- Sender's `current_balance` is **decreased** by the amount
- Receiver's `current_balance` is **increased** by the amount
- **Overdraft is allowed** — if a sender's balance goes negative, they appear on the **DR side** of the Trial Balance

## Development Checklist

1. Start PostgreSQL server
2. Create the database (`account`) and user in PostgreSQL
3. Configure `.env` with DB credentials
4. Run `python manage.py migrate`
5. Run `python manage.py seed`
6. Start server with `python manage.py runserver`
7. Login at `http://localhost:8000` with `ADMIN001` / `Admin@123`
