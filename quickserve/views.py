from django.shortcuts import render, get_object_or_404, redirect
from services.models import Service, SubService
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from decimal import Decimal
from user.models import Profile
from .utils import get_address_from_coordinates
from employee.models import Employee
import json
from django.core.mail import send_mail
from django.contrib import messages
from django.utils.timezone import now, timedelta, datetime
from booking.models import Booking
from django.db.models import Q
from decimal import Decimal, InvalidOperation

@csrf_exempt
@login_required
def save_profile_location(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))

            try:
                lat = Decimal(str(data.get('latitude')))
                lon = Decimal(str(data.get('longitude')))
            except (InvalidOperation, TypeError):
                return JsonResponse({'error': 'Invalid latitude or longitude format.'}, status=400)

            profile, created = Profile.objects.get_or_create(user=request.user)

            if (
                profile.location_lat is not None and
                profile.location_long is not None and
                Decimal(str(profile.location_lat)) == lat and 
                Decimal(str(profile.location_long)) == lon and 
                profile.address
            ):
                return JsonResponse({'address': profile.address, 'message': 'Location unchanged'}, status=200)

            address = get_address_from_coordinates(lat, lon)
            if not address:
                return JsonResponse({'error': 'Could not find an address for the given coordinates.'}, status=404)

            profile.location_lat = float(lat)
            profile.location_long = float(lon)
            profile.address = address
            profile.save()

            return JsonResponse({'address': address, 'message': 'Location updated successfully'}, status=200)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data.'}, status=400)
        except Exception as e:
            return JsonResponse({'error': f'An error occurred: {str(e)}'}, status=500)

    return JsonResponse({'error': 'Invalid request method.'}, status=405)


@csrf_exempt
@login_required
def save_employee_location(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method.'}, status=405)

    try:
        data = json.loads(request.body.decode('utf-8'))
        lat = data.get('latitude')
        lon = data.get('longitude')

        if lat is None or lon is None:
            return JsonResponse({'error': 'Latitude and longitude are required.'}, status=400)

        try:
            lat = Decimal(str(lat))
            lon = Decimal(str(lon))
        except InvalidOperation:
            return JsonResponse({'error': 'Invalid latitude or longitude format.'}, status=400)

        employee = Employee.objects.filter(user=request.user).first()
        if not employee:
            return JsonResponse({'error': 'Employee profile not found.'}, status=404)

        if (
            employee.location_lat is not None and
            employee.location_long is not None and
            Decimal(str(employee.location_lat)) == lat and
            Decimal(str(employee.location_long)) == lon and
            employee.address
        ):
            return JsonResponse({'address': employee.address, 'message': 'Location unchanged'}, status=200)

        address = get_address_from_coordinates(lat, lon)
        if not address:
            return JsonResponse({'error': 'Could not find an address for the given coordinates.'}, status=404)

        employee.location_lat = lat
        employee.location_long = lon
        employee.address = address
        employee.save()

        return JsonResponse({'address': address, 'message': 'Location updated successfully'}, status=200)

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON data.'}, status=400)
    except Exception as e:
        return JsonResponse({'error': f'An error occurred: {str(e)}'}, status=500)

def home(request):
    query = request.GET.get('serviceName', '')
    servicesData = Service.objects.filter(service_name__icontains = query) if query else Service.objects.all()
    subservices = SubService.objects.filter(sub_service_name__icontains = query) if query else SubService.objects.all()
    services = Service.objects.prefetch_related('subservices').all()
    data = {
        'title' : 'Home',
        'servicesData': servicesData,
        'subservices': subservices,
        'services': services,
        'value': query,
        'testimonials': ["Akash Yadav", "Suresh Thakur", "Sanjeev Kumar"]
    }
    
    return render(request, 'pages/index.html', data)

def subservices(request, service_slug):
    service = get_object_or_404(Service, slug = service_slug) 
    subservices = SubService.objects.filter(services=service) 
    data = {
        'service': service,
        'subservices': subservices,
        'title' : service_slug
    }
    return render(request, 'pages/subservices.html', data)


def about(request):
    data = {
        'title' : 'About Us',
    }
    return render(request, 'pages/about.html', data)

def contact(request):
    if request.method == 'POST':
        message = request.POST.get('message')
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        
        send_mail(
            subject=f'Contact Form: {subject}',
            message=f"Name: {name}\nEmail: {email}\n\nMessage:{message}",
            from_email=email,
            recipient_list=["quickserve1997@gmail.com"]
        )
        messages.success(request, "Your message has been sent successfully!")
        return redirect("home")
    data = {
        'title' : 'Contact Us',
    }
    return render(request, 'pages/contact.html', data)

@login_required
def check_user_role(request):
    """Check if the logged in user is an employee or not"""
    user = request.user
    is_employee = hasattr(user, 'employee_profile')
    return JsonResponse({"is_employee": is_employee})
    
@csrf_exempt
def update_fcm_token(request):
    if request.method == "POST":
        data = json.loads(request.body)
        user = request.user
        fcm_token = data.get("fcm_token")

        if user and hasattr(user, 'employee_profile'):
            user.employee_profile.fcm_token = fcm_token
            user.employee_profile.save()
            return JsonResponse({"message": "FCM token updated successfully"})
        
    return JsonResponse({"error": "Invalid request"}, status=400)

def get_location(request):
    user = request.user
    try:
        address = user.profile.address
        return JsonResponse({"address": address, 'success':True})
    except AttributeError:
        return JsonResponse({"success": False, "message": "Address not found"}, status=404)
    
@login_required
def get_employee_location(request):
    employee = req.user
    
    if not employee.location_lat and not employee.location_long:
        return JsonResponse({'error': 'Location not available'}, status = 404)

    return JsonResponse(
        {
            'latitude': employee.location_lat,
            'longitude': employee.location_long,
            'address': employee.address
        }, status = 200
    )

@login_required
def track_employee(request, employee_id):
    employee = get_object_or_404(Employee, id=employee_id)

    # Get the latest accepted booking for today
    booking = Booking.objects.filter(
        assigned_employee=employee,
        status="accepted",
        booking_date=now().date(),
    ).order_by("time_slot").first()

    if not booking:
        messages.error(request, "No active booking found for tracking.")
        return redirect('bookings')

    print(f"Booking time_slot (Raw): '{booking.time_slot}'")

    try:
        # Convert `time_slot` from string to time object
        booking_time = datetime.strptime(booking.time_slot, "%H:%M").time()
        print(f"Converted Booking Time: {booking_time}")

        # Calculate 30 minutes before the booking time
        tracking_allowed_time = datetime.combine(booking.booking_date, booking_time) - timedelta(minutes=30)
        tracking_allowed_time = tracking_allowed_time.replace(tzinfo=now().tzinfo)  # Make it timezone-aware

        print(f"Tracking Allowed Time: {tracking_allowed_time}")
        print(f"Current Time: {now()}")

        # Ensure tracking is only available 30 minutes before the booking
        if now() < tracking_allowed_time:
            messages.error(request, "Tracking is only available 30 minutes before the booking.")
            return redirect('bookings')

        return render(request, 'pages/track.html', {'employee': employee})

    except ValueError:
        messages.error(request, "Invalid time format in booking.")
        return redirect("bookings")
    
def search_sub_services(request):
    query = request.GET.get('serviceName', '')
    results = []
    if query:
        results = SubService.objects.filter(
            Q(sub_service_name__icontains=query)
        )
    return render(request, 'pages/search.html', {'results': results, 'query': query})
