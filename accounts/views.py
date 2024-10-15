# accounts/views.py

from django.shortcuts import render, redirect
from django.contrib.auth import login, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib import messages
from django.conf import settings
from django.urls import reverse

from .forms import CustomUserCreationForm, CustomUserChangeForm

User = get_user_model()  # Use the custom user model


def register(request):
    """Handles user registration and sends a verification email."""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # Set the user to inactive until email is verified
            user.save()

            # Send the verification email
            send_verification_email(user, request)
            messages.success(request, "Registration successful! Please check your email to verify your account.")
            return redirect('home')  # Do not log the user in at this point
    else:
        form = CustomUserCreationForm()

    return render(request, 'accounts/register.html', {'form': form})


def send_verification_email(user, request):
    """Sends an email with a verification link to the user."""
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    print(f"Generated token: {token}")  # Print the generated token for debugging
    verification_link = request.build_absolute_uri(reverse('verify_email', args=[uid, token]))

    subject = "Verify your email address"
    message = f"Click the link below to verify your email:\n{verification_link}"

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email]
    )


from accounts.tokens import custom_token_generator

def verify_email(request, uidb64, token):
    """Verifies the user's email using the custom token generator."""
    try:
        # Decode the user ID from the URL
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    # Conditional debugging print statements based on the DEBUG setting
    if settings.DEBUG:
        if user:
            print(f"User found: {user.username}")
            print(f"User is active: {user.is_active}")
            print(f"User's last login: {user.last_login}")
            print(f"User's password hash: {user.password}")
            print(f"Generated token for user: {default_token_generator.make_token(user)}")
            print(f"Token in URL: {token}")
        else:
            print("User not found during email verification.")

    # Check if the user exists and the token is valid
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "Your email has been verified. You can now log in.")
        if settings.DEBUG:
            print("Email verification successful.")
        return redirect('home')
    else:
        messages.error(request, "The verification link is invalid or has expired.")
        if settings.DEBUG:
            print("Token validation failed or user not found.")
        return redirect('home')

    
@login_required
def profile(request):
    """Displays and allows the user to update their profile."""
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated.")
            return redirect('profile')
    else:
        form = CustomUserChangeForm(instance=request.user)

    return render(request, 'accounts/profile.html', {'form': form})
