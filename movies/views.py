from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.db import transaction
from django.db.models import Count, Q
from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from drf_spectacular.utils import extend_schema, OpenApiParameter
from .models import Movie, Show, Booking
from .serializers import (
    SignupSerializer,
    MovieSerializer,
    ShowSerializer,
    BookingSerializer,
    BookSeatSerializer,
)
class SignupView(generics.CreateAPIView):
    serializer_class = SignupSerializer
    permission_classes = [permissions.AllowAny]
class LoginView(TokenObtainPairView):
    permission_classes = [permissions.AllowAny]
class MovieListView(generics.ListAPIView):
    queryset = Movie.objects.all().order_by('id')
    serializer_class = MovieSerializer
    permission_classes = [permissions.AllowAny]
class MovieShowsListView(generics.ListAPIView):
    serializer_class = ShowSerializer
    permission_classes = [permissions.AllowAny]
    def get_queryset(self):
        return Show.objects.filter(movie_id=self.kwargs['movie_id']).order_by('date_time')
class MyBookingsView(generics.ListAPIView):
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user).order_by('-created_at')
class CancelBookingView(generics.UpdateAPIView):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request, *args, **kwargs):
        booking_id = kwargs.get('booking_id')
        try:
            booking = Booking.objects.select_related('show', 'user').get(id=booking_id, user=request.user)
        except Booking.DoesNotExist:
            return Response({'detail': 'Booking not found or not yours.'}, status=status.HTTP_404_NOT_FOUND)
        if booking.status == Booking.STATUS_CANCELLED:
            return Response({'detail': 'Booking already cancelled.'}, status=status.HTTP_400_BAD_REQUEST)
        booking.status = Booking.STATUS_CANCELLED
        booking.save(update_fields=['status'])
        return Response(BookingSerializer(booking).data)
class BookSeatView(generics.CreateAPIView):
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        show_id = kwargs.get('show_id')
        serializer = BookSeatSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        seat_number = serializer.validated_data['seat_number']
        try:
            show = Show.objects.select_for_update().get(id=show_id)
        except Show.DoesNotExist:
            return Response({'detail': 'Show not found.'}, status=status.HTTP_404_NOT_FOUND)

        if seat_number < 1 or seat_number > show.total_seats:
            return Response({'detail': 'Seat number out of range.'}, status=status.HTTP_400_BAD_REQUEST)

        existing = Booking.objects.select_for_update().filter(
            show=show, seat_number=seat_number, status=Booking.STATUS_BOOKED
        ).exists()
        if existing:
            return Response({'detail': 'Seat already booked.'}, status=status.HTTP_400_BAD_REQUEST)

        active_bookings_count = Booking.objects.select_for_update().filter(
            show=show, status=Booking.STATUS_BOOKED
        ).count()
        if active_bookings_count >= show.total_seats:
            return Response({'detail': 'Show is fully booked.'}, status=status.HTTP_400_BAD_REQUEST)

        booking = Booking.objects.create(
            user=request.user,
            show=show,
            seat_number=seat_number,
            status=Booking.STATUS_BOOKED,
        )
        return Response(BookingSerializer(booking).data, status=status.HTTP_201_CREATED)

