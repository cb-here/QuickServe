from django.urls import path
from . import views

urlpatterns = [
    path('employee_home/', views.employee_home, name='employee_home'),
    path('apply_for_job/', views.apply_for_job, name='apply_for_job'),
    path('employee_dashboard/', views.employee_dashboard, name='employee_dashboard'),
    path('employee_update_profile/', views.employee_update_profile, name="employee_update_profile"),
    path('toggle-availability/', views.toggle_availability, name='toggle_availability'),
]