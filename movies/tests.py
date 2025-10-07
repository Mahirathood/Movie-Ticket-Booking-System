from datetime import timedelta
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Movie, Show, Booking
class BookingApiTests(APITestCase):
    def setUp(self):
        # Create a movie and an upcoming show for testing
        self.movie = Movie.objects.create(title="Inception", duration_minutes=148)
        self.show = Show.objects.create(
            movie=self.movie,
            screen_name="Screen 1",
            date_time=timezone.now() + timedelta(hours=2),
            total_seats=3,
        )
    def signup_and_login(self, username: str = "demo", password: str = "Passw0rd!") -> str:
        # Signup
        resp = self.client.post(
            reverse("signup"), {"username": username, "password": password}, format="json"
        )
        self.assertIn(resp.status_code, (status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST))
        # Login
        resp = self.client.post(
            reverse("login"), {"username": username, "password": password}, format="json"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn("access", resp.data)
        return resp.data["access"]
    def auth_headers(self, access: str) -> dict:
        return {"HTTP_AUTHORIZATION": f"Bearer {access}"}
    def test_list_movies_and_shows(self):
        # List movies
        resp = self.client.get(reverse("movie-list"))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(resp.data), 1)
        # List shows for movie
        resp = self.client.get(reverse("movie-shows", kwargs={"movie_id": self.movie.id}))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(resp.data), 1)
    def test_booking_flow_and_constraints(self):
        access = self.signup_and_login()
        # Book seat 1
        resp = self.client.post(
            reverse("book-seat", kwargs={"show_id": self.show.id}),
            {"seat_number": 1},
            format="json",
            **self.auth_headers(access),
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        booking_id = resp.data["id"]
        # Seat already booked (same seat)
        resp = self.client.post(
            reverse("book-seat", kwargs={"show_id": self.show.id}),
            {"seat_number": 1},
            format="json",
            **self.auth_headers(access),
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Seat already booked", str(resp.data))
        # Book remaining seats 2 and 3
        for seat in (2, 3):
            r = self.client.post(
                reverse("book-seat", kwargs={"show_id": self.show.id}),
                {"seat_number": seat},
                format="json",
                **self.auth_headers(access),
            )
            self.assertEqual(r.status_code, status.HTTP_201_CREATED)
        # Show is fully booked now; attempting to book an already booked seat returns seat already booked
        resp = self.client.post(
            reverse("book-seat", kwargs={"show_id": self.show.id}),
            {"seat_number": 2},
            format="json",
            **self.auth_headers(access),
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("seat already booked", str(resp.data).lower())

        # My bookings returns at least 3 entries
        resp = self.client.get(reverse("my-bookings"), **self.auth_headers(access))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(resp.data), 3)

        # Cancel a booking
        resp = self.client.post(
            reverse("cancel-booking", kwargs={"booking_id": booking_id}),
            **self.auth_headers(access),
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["status"], Booking.STATUS_CANCELLED)

        # Cancel again should be 400
        resp = self.client.post(
            reverse("cancel-booking", kwargs={"booking_id": booking_id}),
            **self.auth_headers(access),
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_seat_number_out_of_range(self):
        access = self.signup_and_login("user2")
        # Seat 0 invalid
        resp = self.client.post(
            reverse("book-seat", kwargs={"show_id": self.show.id}),
            {"seat_number": 0},
            format="json",
            **self.auth_headers(access),
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

        # Seat greater than total_seats invalid
        resp = self.client.post(
            reverse("book-seat", kwargs={"show_id": self.show.id}),
            {"seat_number": 999},
            format="json",
            **self.auth_headers(access),
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

