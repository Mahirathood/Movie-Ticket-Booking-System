from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from .models import Movie, Show, Booking
class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    class Meta:
        model = get_user_model()
        fields = ("username", "password")
    def validate_password(self, value: str) -> str:
        validate_password(value)
        return value
    def create(self, validated_data):
        user_model = get_user_model()
        user = user_model(username=validated_data["username"])
        user.set_password(validated_data["password"])
        user.save()
        return user
class MovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = ("id", "title", "duration_minutes")
class ShowSerializer(serializers.ModelSerializer):
    movie = MovieSerializer(read_only=True)
    class Meta:
        model = Show
        fields = ("id", "movie", "screen_name", "date_time", "total_seats")
class BookingSerializer(serializers.ModelSerializer):
    show = ShowSerializer(read_only=True)
    class Meta:
        model = Booking
        fields = ("id", "show", "seat_number", "status", "created_at")
class BookSeatSerializer(serializers.Serializer):
    seat_number = serializers.IntegerField(min_value=1)


