from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import EmployeeForm
from django.contrib.auth.decorators import login_required
from services.models import Service
from django.db import IntegrityError
from booking.models import Booking
from django.views.decorators.http import require_POST
from .models import Employee

def employee_home(request):
    employee_profile = getattr(request.user, 'employee_profile', None)
    if employee_profile:
        messages.info(request, "You are being redirected to your dashboard.")
        return redirect('employee_dashboard')
    return render(request, 'employee/employee_home.html', {'title': 'Employee Home'})

@login_required
def employee_dashboard(request):
    try:
        order_by = request.GET.get('order_by', '-created_at')
        employee_profile = request.user.employee_profile
        accepted_bookings = Booking.objects.filter(assigned_employee = employee_profile).order_by(order_by)
    except Employee.DoesNotExist:
        messages.info(request, "You need to apply for a job to access the dashboard.")
        return redirect('apply_for_job')

    return render(request, 'employee/employee_dashboard.html', {
        'employee': employee_profile,
        'title': 'Employee Dashboard',
        'accepted_bookings': accepted_bookings,
        'order_by': order_by
    })

def apply_for_job(request):
    skills = Service.objects.all() 

    if hasattr(request.user, 'employee_profile'):
        messages.info(request, "You have already applied for a job.")
        return redirect('employee_dashboard')

    if request.method == "POST":
        form = EmployeeForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                employee = form.save(commit=False)
                employee.user = request.user
                employee.save()
                form.save_m2m() 
                messages.success(request, "Your application has been applied successfully!")
                return redirect('employee_dashboard')
            except IntegrityError:
                form.add_error(None, "An employee record for this user already exists.")
    else:
        form = EmployeeForm()

    return render(request, 'employee/employee_registeration.html', {
        'form': form,
        'title': 'Apply for Job',
        'skills': skills
    })
    
@login_required
def employee_update_profile(request):
    try:
        employee = request.user.employee_profile
    except Employee.DoesNotExist:
        messages.error(request, "Employee profile not found. Please apply for a job first.")
        return redirect('apply_for_job')

    if request.method == 'POST':
        form = EmployeeForm(request.POST, request.FILES, instance=employee)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated successfully.")
            return redirect('employee_dashboard')
        else:
            print("Form errors:", form.errors)
            messages.error(request, "Please correct the errors in the form.")
    else:
        form = EmployeeForm(instance=employee)

    context = {
        'form': form,
        'employee': employee,
        'title': 'Update Profile',
    }

    return render(request, 'employee/employee_update_profile.html', context)

@login_required
@require_POST
def toggle_availability(request):
    employee = request.user.employee_profile
    employee.is_available = not employee.is_available
    employee.save()
    return redirect('employee_dashboard')