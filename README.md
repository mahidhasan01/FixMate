# FixMate

FixMate is a home service booking site. Customers can find electricians, plumbers and
other technicians, book them, pay, and leave a review. Workers list their services and
get verified by an admin before they can take jobs.

We built it for our CSE 302 (Object Oriented Programming II Lab) project at the
University of Asia Pacific.

## What it does

- Customers and workers sign up with separate accounts
- Workers get a verified badge after an admin checks their documents
- Customers verify their identity with their NID before booking
- Workers post service listings with prices and photos
- Customers search listings by category, price or keyword
- Bookings go from pending to accepted to completed
- Workers upload a photo when a job is done, and the customer confirms it
- Customers rate the worker after the job, and the ratings show on the worker's profile
- Payments are recorded for each booking, with refunds for cancelled ones
- Simple rules flag suspicious activity, like repeated cancellations or payment mismatches

## Apps

| App | What's in it |
| --- | --- |
| accounts_app | Users, customer and worker profiles, ID and worker verification |
| services_app | Service categories and worker listings |
| booking_app | Bookings, reviews, job completion photos, fraud flags |
| payment_app | Payments and refunds |

## Running it locally

You need Python 3.12 or newer.

```
git clone <repo-url>
cd fixmate
python -m venv venv
venv\Scripts\activate          (on Mac/Linux: source venv/bin/activate)
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and put any long random string in `SECRET_KEY`.

```
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Open http://127.0.0.1:8000. The admin panel is at /admin.

The database is SQLite, so there is nothing else to install. `db.sqlite3` is not in the
repo; `migrate` creates it on your machine.

## Team

| Name | Reg ID |
| --- | --- |
| Mahfuza Noor Mim | 24101010 |
| Afroj Jahan Bushra | 24101015 |
| MD. Mahid Hasan Dewan | 24101017 |
| Taohedul Islam | 24101025 |
