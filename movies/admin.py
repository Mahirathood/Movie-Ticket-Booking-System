from django.contrib import admin
from .models import Movie, Show, Booking
@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "duration_minutes")
    search_fields = ("title",)
@admin.register(Show)
class ShowAdmin(admin.ModelAdmin):
    list_display = ("id", "movie", "screen_name", "date_time", "total_seats")
    list_filter = ("screen_name", "movie")
    search_fields = ("movie__title", "screen_name")
@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "show", "seat_number", "status", "created_at")
    list_filter = ("status", "show")
    search_fields = ("user__username",)

