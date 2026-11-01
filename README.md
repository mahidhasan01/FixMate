# FixMate

FixMate is a home service booking site. Customers can find electricians, plumbers and
other technicians, book them, pay, and leave a review. Workers list their services and
get verified by an admin before they can take jobs.

We built it for our CSE 302 (Object Oriented Programming II Lab) project at the
University of Asia Pacific.

## What it does

- Customers and workers sign up with separate accounts
- Workers get a verified badge after staff check their documents
- Customers verify their identity with their NID, and only approved customers can book
- Workers post service listings with prices and photos
- Customers search listings by category, price or keyword
- Workers accept or reject bookings, and customers can cancel while a booking is pending
- Workers upload a photo when a job is done, and the customer confirms it
- Customers rate the worker after the job, and the ratings show on the worker's profile
- Customers pay by bKash, Nagad or Rocket (staff check the TrxID) or in cash, and get a printable receipt
- Staff can mark a paid payment as refunded, for example after a disputed job
- Simple rules flag suspicious activity with a risk score: a rejected job photo, 3+ cancellations,
  3+ one-star reviews or possible fake 5-star reviews within 30 days
- Customers and workers get their own dashboard, and staff get an overview with the verification
  queue, payment queue and fraud flags

## Apps

| App | What's in it |
| --- | --- |
| accounts_app | Users, customer and worker profiles, ID and worker verification |
| services_app | Service categories and worker listings |
| booking_app | Bookings, reviews, job completion photos, fraud flags, dashboards |
| payment_app | Payments, receipts, refunds and the staff overview |

## Running it locally

You need Python 3.12 or newer.

```
git clone https://github.com/mahidhasan01/FixMate.git
cd FixMate
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
