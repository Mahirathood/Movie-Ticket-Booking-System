# Movie Ticket Booking API (Django + DRF + JWT)

A simple movie ticket booking backend implementing signup/login (JWT), movies and shows listing, seat booking and cancellation, and Swagger docs.

## Tech
- Django 4.2
- Django REST Framework
- SimpleJWT (JWT auth)
- drf-spectacular (Swagger/OpenAPI)

## Setup
```bash
# Windows PowerShell
python -m venv .venv
.\.venv\Scripts\python -m pip install --upgrade pip
.\.venv\Scripts\python -m pip install -r requirements.txt
.\.venv\Scripts\python manage.py migrate
.\.venv\Scripts\python manage.py runserver
```

App runs at `http://127.0.0.1:8000/`. Swagger at `http://127.0.0.1:8000/swagger/`.

## Endpoints
- POST `/signup` → create user `{ username, password }`
- POST `/login` → JWT pair `{ access, refresh }`
- POST `/token/refresh` → refresh access token
- GET `/movies/` → list movies
- GET `/movies/<id>/shows/` → list shows for movie
- POST `/shows/<id>/book/` → book seat `{ seat_number }` (JWT required)
- POST `/bookings/<id>/cancel/` → cancel booking (JWT required)
- GET `/my-bookings/` → list my bookings (JWT required)

## JWT Usage
1) Register: POST `/signup` with JSON body `{ "username": "u", "password": "p" }`
2) Login: POST `/login` → copy `access`
3) Call protected APIs with header: `Authorization: Bearer <access>`

## Notes
- Prevents double-booking and overbooking using transactional checks.
- Cancelling a booking frees the seat.

## Admin (optional)
```bash
.\.venv\Scripts\python manage.py createsuperuser
```
