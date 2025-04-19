from django.contrib import admin
from .models import Service, SubService

class ServicesAdmin(admin.ModelAdmin):
    list_display = ("service_name",)
admin.site.register(Service, ServicesAdmin)

class SubServicesAdmin(admin.ModelAdmin):
    list_display = ('sub_service_name', 'sub_service_img', 'sub_service_description', 'service_name')
admin.site.register(SubService)
