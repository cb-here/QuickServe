from django.db import models
from services.models import SubService,Service
from django.contrib.auth.models import User
from employee.models import Employee
from geopy.distance import geodesic
from firebase_admin import messaging
import firebase_admin

class Booking(models.Model):
    DURTION_CHOICES = [
        ('0.5', '30 Minutes'),
        ('1', '1 Hour'),
        ('2', '2 Hours'),
        ('3', '3 Hours'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('canceled', 'Canceled'),
        ('completed', 'Completed')
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE, null=True)
    sub_service = models.ForeignKey(SubService, on_delete=models.CASCADE)
    booking_date = models.DateField()
    time_slot = models.CharField(max_length=100)
    address = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    duration = models.CharField(max_length=3, choices=DURTION_CHOICES, default = '0.5')
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    assigned_employee = models.ForeignKey(Employee, on_delete=models.CASCADE, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    feedback = models.TextField(blank=True, null=True)
    rating = models.PositiveSmallIntegerField(
        null=True, blank=True,
        choices=[(i, f"{i} Star{'s' if i > 1 else ''}") for i in range(1, 6)],
        help_text="Rate the service from 1 to 5 stars"
    )
    is_emergency = models.BooleanField(default=False)
    
    def calculate_total_price(self):
        """Calculate total price"""
        hourly_rate = 100
        sub_service_price = self.sub_service.price if self.sub_service else 0
    
        self.total_price = (hourly_rate * float(self.duration)) + sub_service_price
        return self.total_price

        
    def __str__(self):
        return f"Booking {self.id} - {self.status}"

    def get_nearby_employees(self):
        """get the nearby employees"""
        user_location = (self.user.profile.location_lat, self.user.profile.location_long)
        print(f"User location: {user_location}")

        neary_employees = set()
        
        for employee in Employee.objects.filter(
            is_available = True,
            location_lat__isnull = False,
            location_long__isnull = False,
            is_verified = True,
            skills__in = [self.sub_service.services]
        ).distinct():
            employee_location = (employee.location_lat, employee.location_long)
            distance = geodesic(user_location, employee_location).km
            
            print(f"Checking Employee {employee.id}: {employee_location}, Distance: {distance} km") 
            if distance <= 5:
                neary_employees.add(employee)
        return list(neary_employees)
    
    def notify_nearby_employees(self):
        """Send notifications to nearby employees."""
        nearby_employees = self.get_nearby_employees()
    
        if not nearby_employees:
            return
        message = (
        f"📅 New Booking Alert! \n\n"
        f"🛠 Service: {self.sub_service.sub_service_name} \n"
        f"👤 Customer: {self.user.get_full_name()} (@{self.user.username}) \n"
        f"📅 Date: {self.booking_date} \n"
        f"⏰ Time: {self.time_slot} \n"
        f"📍 Location: {self.address} \n\n"
        f"🔔 Tap to accept this job!"
    )
        notified_employees = set()
        
        for employee in nearby_employees:
            if employee.id not in notified_employees:
                self.send_notification(employee, message)
                notified_employees.add(employee.id)

    def notify_assigned_employee(self):
        """notify the assigned employee that they are booked in case of emergency"""
        if not self.assigned_employee:
            print("No employee assigned to this booking.")
            return
        message = (
        f"🚨 *Booking Alert!* 🚨\n\n"
        f"🛠 **Service:** {self.sub_service.sub_service_name} \n"
        f"👤 **Customer:** {self.user.get_full_name()} (@{self.user.username}) \n"
        f"📅 **Date:** {self.booking_date} \n"
        f"⏰ **Time:** {self.time_slot} \n"
        f"📍 **Location:** {self.address} \n\n"
        f"⚡ Please respond *ASAP*! Tap to view details."
)

        self.send_notification(self.assigned_employee, message)

    def send_notification(self, employee, message):
        """Send a notification to an employee using Firebase."""
        if employee.fcm_token:
            data = {
                "click_action":f"http://localhost:8000/booking/accept_booking/{self.id}",
            }
            notification = messaging.Notification(
                title="New Booking Assignment",
                body=message
            )
            message = messaging.Message(
                notification=notification,
                token=employee.fcm_token,
                data = data
            )
            try:
                response = messaging.send(message)
                print(f"Notification sent to {employee.user.username}: {response}")
            except firebase_admin.exceptions.FirebaseError as e:
                print(f"Firebase Error: {e}")
            except Exception as e:
                print(f"General Error: {e}")
        else:
            print(f"No FCM token found for {employee.user.username}")

    def save(self, *args, **kwargs):
        """Override save method to notify nearby employees."""
        is_new_booking = self._state.adding
        
        if self.total_price is None:
            self.calculate_total_price()
            
        super().save(*args, **kwargs)
    
        if is_new_booking:
            self.notify_nearby_employees()
        
        if self.assigned_employee:
            self.notify_assigned_employee()
        
        if self.assigned_employee and self.rating:
            self.assigned_employee.update_employee_rating()