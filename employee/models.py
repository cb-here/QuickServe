from django.db import models
from django.db.models import Avg, Count
from django.contrib.auth.models import User
from services.models import Service
from django.core.validators import MinValueValidator, MaxValueValidator

class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="employee_profile",null=True, blank=True)
    role = models.CharField(max_length=100, null=True)
    skills = models.ManyToManyField(Service, related_name="employees", blank=True)
    is_available = models.BooleanField(default=True)
    working_hours_start = models.TimeField(null=True, blank=True)
    working_hours_end = models.TimeField(null=True, blank=True)
    average_rating = models.FloatField(default=0.0, validators=[MinValueValidator(0.0), MaxValueValidator(5.0)])
    total_reviews = models.PositiveIntegerField(default=0)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    profile_picture = models.ImageField(upload_to='employee_profiles/', null=True, blank=True)
    experience_years = models.PositiveIntegerField(default=0)
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, default=100,null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    location_lat = models.FloatField(null=True, blank=True)
    location_long = models.FloatField(null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    fcm_token = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def employee_name(self):
        return self.user.username
    
    def update_employee_rating(self): 
        from booking.models import Booking
        booking_with_rating = Booking.objects.filter(assigned_employee = self, rating__isnull = False)
        
        average_rating = booking_with_rating.aggregate(Avg('rating'))['rating__avg'] or 0.0
        total_reviews = booking_with_rating.count()
        
        self.average_rating = average_rating
        self.total_reviews = total_reviews
        self.save()
        
    def __str__(self):
        return f'{self.user.username}, {self.role}'