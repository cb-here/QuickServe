from django.shortcuts import render, redirect,get_object_or_404
from django.contrib import messages
from .forms import UserRegisterForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .models import Profile
import json
import random
import string
from django.core.mail import send_mail
from django.core.cache import cache

def generate_otp():
    """generting the 6 digit OTP"""
    return ''.join(random.choices(string.digits, k=6))

def send_otp_email(email, otp):
    """send OTP to user's email now"""
    subject = "Your QuickServe Login OTP"
    message = f"Your OTP for login is: {otp}. It is valid for 5 minutes."
    send_mail(subject, message, 'quickserve1997@gmail.com', [email])

def register(request):
    if request.method == 'POST':
        user_form = UserRegisterForm(request.POST)
        if user_form.is_valid():
            try:
                user = user_form.save()
                messages.success(request, 'Your account has been created successfully! You can now log in.')
                return redirect('login')
            except Exception as e:
                messages.error(request, f"Error creating account: {str(e)}")
        else:
            messages.error(request, "Please correct the errors below.")

    else:
        user_form = UserRegisterForm()

    return render(request, 'user/register.html', {'user_form': user_form, 'title': 'Register'})

def login_view(request):
    if request.method == 'POST':
        username_or_email = request.POST.get('username_or_email')
        
        user = User.objects.filter(username=username_or_email).first() or User.objects.filter(email=username_or_email).first()

        if user:
            otp = generate_otp()
            cache.set(f"otp_{user.email}", otp, timeout=300)
            send_otp_email(user.email, otp)
            request.session['otp_email'] = user.email
            messages.success(request, 'OTP sent to your email. Please verify.')
            return redirect('verify_otp')
        else:
            messages.error(request, 'User not found. Please check your email or username')

    return render(request, 'user/login.html', {'title': 'Login'})


def verify_otp_view(request):
    if request.method == "POST":
        email = request.session.get('otp_email')

        if not email:
            messages.error(request, "Session expired. Please request a new OTP.")
            return redirect('login')

        otp_entered = request.POST.get('otp')
        stored_otp = cache.get(f"otp_{email}")


        if stored_otp and stored_otp == otp_entered:
            user = User.objects.filter(email=email).first()
            if not user:
                messages.error(request, "User not found.")
                return redirect('login')

            login(request, user)
            cache.delete(f"otp_{email}")
            del request.session['otp_email']
            messages.success(request, 'You have been logged in successfully!')
            return redirect('home')
        else:
            messages.error(request, 'Invalid or expired OTP')
    return render(request, 'user/verify_otp.html', {'title': 'Verify OTP'})

@login_required
def profile(request):
    if request.method == "POST":
        user = request.user
        user.username = request.POST.get("username")
        user.email = request.POST.get("email")
        user.save()
        messages.success(request, "Profile updated successfully!")
        return redirect('home')
    
    return render(request, "user/profile.html", {'title' : 'Profile'})

def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('home')
