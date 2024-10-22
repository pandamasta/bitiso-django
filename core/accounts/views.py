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
from core.accounts.tokens import custom_token_generator


User = get_user_model()  # Use the custom user model


def register(request):
    """Handles user registration and sends a verification email if required."""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)

            if settings.EMAIL_VERIFICATION_REQUIRED:
                user.is_active = False  # Set the user to inactive until email is verified
                user.save()

                # Send the verification email
                send_verification_email(user, request)
                messages.success(request, "Registration successful! Please check your email to verify your account.")
            else:
                # If email verification is not required, activate the user and log them in
                user.is_active = True
                user.save()
                login(request, user)
                messages.success(request, "Registration successful! You are now logged in.")

            return redirect('home')
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


def verify_email(request, uidb64, token):
    """Verifies the user's email using the custom token generator."""
    if not settings.EMAIL_VERIFICATION_REQUIRED:
        # Redirect if email verification is not required
        return redirect('home')

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


def profile_view(request, uuid=None, username=None):
    """Displays a user's profile based on UUID or username."""
    if settings.USE_UUID_FOR_PROFILE_URL:
        user = get_object_or_404(CustomUser, uuid=uuid)
    else:
        user = get_object_or_404(CustomUser, username=username)
    
    return render(request, 'accounts/profile.html', {'profile_user': user})


    
@login_required
def profile(request):
    """Displays and allows the user to update their profile."""
    user = request.user
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, instance=user)
        if form.is_valid():
            new_username = form.cleaned_data.get('username')
            if new_username != user.username:
                # Check if the user has changed the username within the limit
                time_since_last_change = timezone.now() - user.username_last_changed
                if time_since_last_change < timedelta(days=settings.USERNAME_CHANGE_LIMIT_DAYS):
                    messages.error(request, "You can only change your username once per week.")
                else:
                    # Update the username and record the change time
                    user.username = new_username
                    user.username_last_changed = timezone.now()
                    user.save()
                    messages.success(request, "Your username has been updated.")
            else:
                form.save()
                messages.success(request, "Your profile has been updated.")
            return redirect('profile')
    else:
        form = CustomUserChangeForm(instance=user)
    return render(request, 'accounts/profile.html', {'form': form})

