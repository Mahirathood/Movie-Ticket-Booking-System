from django.conf import settings
from django.db import models
class Movie(models.Model):
    title = models.CharField(max_length=255)
    duration_minutes = models.PositiveIntegerField()
    def __str__(self) -> str:
        return self.title
class Show(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name="shows")
    screen_name = models.CharField(max_length=100)
    date_time = models.DateTimeField()
    total_seats = models.PositiveIntegerField()
    def __str__(self) -> str:
        return f"{self.movie.title} @ {self.screen_name} ({self.date_time:%Y-%m-%d %H:%M})"
class Booking(models.Model):
    STATUS_BOOKED = "booked"
    STATUS_CANCELLED = "cancelled"
    STATUS_CHOICES = [
        (STATUS_BOOKED, "Booked"),
        (STATUS_CANCELLED, "Cancelled"),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="bookings")
    show = models.ForeignKey(Show, on_delete=models.CASCADE, related_name="bookings")
    seat_number = models.PositiveIntegerField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_BOOKED)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        indexes = [
            models.Index(fields=["show", "seat_number", "status"]),
        ]
    def __str__(self) -> str:
        return f"{self.user} - {self.show} - Seat {self.seat_number} ({self.status})"

