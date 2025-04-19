from django.urls import path
from . import views

urlpatterns = [
    path('book/<slug:subservice_slug>/', views.book_service, name='book_service'),
    path('confirm-booking/<slug:subservice_slug>/', views.confirm_booking, name='confirm_booking'),
    path('bookings/', views.bookings, name='bookings'),
    path('cancel_booking/<int:booking_id>', views.cancel_booking, name="cancel_booking"),
    path('leave-feedback/<int:booking_id>/', views.leave_feedback, name='leave_feedback'),
    path('accept_booking/<int:booking_id>', views.accept_booking, name="accept_booking"),
    path('ignore_booking/', views.ignore_booking, name="ignore_booking"),
    path('complete_booking/<int:booking_id>', views.complete_booking, name="complete_booking"),
    path('rate_booking/<int:booking_id>', views.rate_booking, name="rate_booking"),
    path("emergency-booking/<slug:subservice_slug>/", views.emergency_booking, name = 'emergency_booking')
]
