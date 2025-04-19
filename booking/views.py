from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import BookingForm
from .models import Booking
from services.models import SubService
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.utils.timezone import now
from django.core.mail import send_mail
from django.views.decorators.csrf import csrf_exempt
from decimal import Decimal

@login_required
def book_service(request, subservice_slug):
    sub_service = get_object_or_404(SubService, slug=subservice_slug)
    
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking_date = form.cleaned_data['booking_date'].isoformat()
            total_price = str(form.cleaned_data.get('total_price'))

            request.session['booking_details'] = {
                'sub_service_id': sub_service.id,
                'booking_date': booking_date,
                'time_slot': form.cleaned_data['time_slot'],
                'address': form.cleaned_data['address'],
                'duration': form.cleaned_data['duration'],
                'total_price': total_price
            }
            messages.success(request, "Confirm your booking now!")
            return redirect('confirm_booking', subservice_slug=subservice_slug)
        else:
            messages.error(request, "Please correctly fill the form.")
    else:
        form = BookingForm()

    context = {
        'subservice': sub_service,
        'form': form,
        'title': 'Booking'
    }
    return render(request, 'booking/service_booking.html', context)

@login_required
def confirm_booking(request, subservice_slug):
    subservice = get_object_or_404(SubService, slug=subservice_slug)
    booking_details = request.session.get('booking_details')
    
    if not booking_details:
        messages.error(request, 'No booking details found. Please start the booking process again.')
        return redirect('book_service', subservice_slug=subservice_slug)

    if request.method == 'POST':
        try:
            total_price = Decimal(booking_details.get('total_price'))
        except (TypeError, ValueError):
            messages.error(request, "Invalid total price. Please try again.")
            return redirect('book_service', subservice_slug=subservice_slug)
        
        required_fields = ["booking_date", "time_slot", "address", "duration"]
        if not all(field in booking_details for field in  required_fields):
            messages.error(request, "Missing booking details. Please try again")
            return redirect("book_service", subservice_slug = subservice_slug)

        """temp booking to make the nearby employee function work """
        temp_booking = Booking(
            user = request.user,
            sub_service = subservice,
            booking_date = booking_details['booking_date'],
            time_slot = booking_details['time_slot'],
            address = booking_details['address'],
            duration = booking_details['duration'],
            total_price = total_price,
        )
        temp_booking.save()
        print(f"Temp Booking: {temp_booking}")
        nearby_employees = temp_booking.get_nearby_employees()
        print(f"Nearby employees: {nearby_employees}")
        if not nearby_employees:
            messages.error(request, "No available specialists nearby. Please try again later.")
            return redirect("book_service", subservice_slug=subservice_slug)
        
        """actual booking here now"""
        booking = Booking.objects.create(
            user = request.user,
            service = subservice.services,
            sub_service = subservice,
            booking_date = booking_details['booking_date'],
            time_slot = booking_details['time_slot'],
            address = booking_details['address'],
            duration = booking_details['duration'],
            total_price = total_price,
            status ='confirmed'
        )
        
        messages.success(request, "Thank you for confirming your booking! We look forward to serving you.")
        del request.session['booking_details']
        return redirect('bookings')
    context = {
        'subservice': subservice,
        'booking_details': booking_details,
        'title': 'Confirm Booking'
    }
    return render(request, 'booking/confirm_booking.html', context)

@login_required
def bookings(request):
    order_by = request.GET.get('order_by', '-created_at')
    bookings = Booking.objects.filter(user=request.user).exclude(status = 'canceled').order_by(order_by)
    context = {
        'bookings':bookings,
        'title': 'Your Bookings'
    }
    return render(request, 'user/bookings.html', context)

@login_required
def leave_feedback(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    if booking.status != 'completed':
        messages.warning(request, "You could leave feedback for the completed booking only!")
        return redirect('bookings')
    if request.method == 'POST':
        feedback = request.POST.get('feedback')
        booking.feedback = feedback
        booking.save()
        messages.success(request, "Thanks for your feedback!!")
        return redirect('bookings')
    return render(request, 'user/leave_feedback.html', {'booking':booking, 'title': 'Leave Feedback'})

@login_required
def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)

    if booking.status == "confirmed":
        booking.status = "canceled"
        booking.save()
        messages.success(request, "Booking canceled successfully.")
    else:
        messages.error(request, "You can only cancel confirmed bookings.")
    return redirect("bookings")

def send_booking_acceptance_email(booking):
    subject = "Your QuickServe Booking Has Been Accepted!"
    user_email = booking.user.email
    
    employee_name = booking.assigned_employee.user.get_full_name() or booking.assigned_employee.user.username
    sub_service_name = booking.sub_service.sub_service_name
    date = booking.booking_date
    time = booking.time_slot
    
    message = f"""
    Hello {booking.user.get_full_name()},
    
    Great news! Your booking for "{sub_service_name}" on **{date}** at **{time}** has been accepted by **{employee_name}**.
    
    You can track your booking details in your orders.
    
    Thank you for using QuickServe!
    
    Best regards,  
    QuickServe Team
    """
    
    send_mail(
        subject,
        message,
        'quickserve1997@gmail.com', 
        [user_email],
        fail_silently=False
    )
    
@login_required
def accept_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    if booking.status != 'confirmed':
        messages.warning(request, "This booking has already been accepted or completed.")
        return redirect("employee_dashboard")
    
    if request.method == "POST":
        booking.status = 'accepted'
        booking.assigned_employee = request.user.employee_profile
        booking.save()
        send_booking_acceptance_email(booking)
        messages.success(request, "You have successfully accepted the booking!")
        return redirect("employee_dashboard")

    context = {
        "title": "Accept Booking",
        "booking": booking
    }
    return render(request, 'booking/accept_booking.html', context)

@login_required
def ignore_booking(request):
    messages.info(request, "Thanks for your response!")
    return redirect("employee_dashboard")

@login_required
def complete_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, assigned_employee = request.user.employee_profile)
    if now().date() == booking.booking_date and booking.status == 'accepted' and now().time() >= booking.time_slot:
        booking.status = 'completed'
        booking.save()
        messages.success(request, "The booking has been marked as completed!")
    else:
        messages.error(request, 'You can only mark the booking as completed after the time slot.')
    return redirect('employee_dashboard')


@login_required
def rate_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    
    if booking.status == 'completed':
        if request.method == 'POST':
            rating = request.POST.get('rating')
            if rating and rating.isdigit() and 1 <= int(rating) <= 5:
                booking.rating = rating
                booking.save()
                messages.success(request, "Thanks for rating the service!")
            else:
                messages.error(request, "Invalid rating value.")
    else:
        messages.error(request, "You could only rate the completed bookings.")
    
    return redirect('bookings')

@login_required
@csrf_exempt
@require_POST
def emergency_booking(request, subservice_slug):
    user = request.user
    sub_service = get_object_or_404(SubService, slug=subservice_slug)

    if not hasattr(user, 'profile') or not user.profile.address:
        messages.error(request, "Your profile or address is missing. Please update your profile.")
        return redirect("book_service", subservice_slug=subservice_slug)

    service_address = user.profile.address
    emergency_fee = 100
    employee_hourly_rate = 100
    
    try:
        duration = Decimal(request.POST.get("duration", 0.5))
        
        service_cost = (employee_hourly_rate * duration) * sub_service.price
        total_price = service_cost + emergency_fee
        
        booking = Booking(
            user=user,
            sub_service=sub_service,
            booking_date=now().date(),
            time_slot=now().time(),
            address=service_address,
            is_emergency=True,
            duration = duration,
            total_price = total_price
        )
        nearby_employees = booking.get_nearby_employees()

        if not nearby_employees:
            messages.error(request, "Extremely sorry but no available specialists nearby. Please try again later.")
            return redirect("book_service", subservice_slug=subservice_slug)

        booking.assigned_employee = nearby_employees[0]
        booking.status = 'accepted'
        booking.save()

        messages.success(
            request,
            f"Emergency {sub_service.sub_service_name} booked! " +
            f"Specialist {booking.assigned_employee.user.get_full_name()} is on the way."
        )
        send_booking_acceptance_email(booking)

    except Exception as e:
        print(f"Error creating emergency booking: {str(e)}")
        messages.error(request, f"An error occurred while processing your request. Please try again.")
        return redirect("book_service", subservice_slug=subservice_slug)

    return redirect("bookings")

