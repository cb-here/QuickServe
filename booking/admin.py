from django.contrib import admin
from .models import Booking

class BookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'sub_service', 'booking_date', 'time_slot', 'status', 'get_assigned_employee')
    list_filter = ('status', 'booking_date', 'time_slot')

    def get_assigned_employee(self, obj):
        return obj.assigned_employee if obj.assigned_employee else "Not Assigned"
    get_assigned_employee.short_description = 'Assigned Employee'
    
    fields = ('user', 'service', 'sub_service', 'booking_date', 'time_slot', 'address', 'status', 'assigned_employee', 'feedback')
    readonly_fields = ('created_at',)

admin.site.register(Booking, BookingAdmin)

