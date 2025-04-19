from django.contrib import admin
from .models import Employee

class EmployeeAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'role',
        'profile_picture',
        'address',
        'is_available',
        'is_verified',
        'total_reviews',
        'phone_number',
        'email',
    )
    list_filter = ('is_available', 'is_verified')
    search_fields = ('user__username', 'role', 'email')

admin.site.register(Employee, EmployeeAdmin)
