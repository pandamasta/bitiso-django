# views/user_views.py

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from ..forms import CustomAuthenticationForm, RegisterForm

def login_view(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome, {username}!")
                return redirect('manage:dashboard')
            else:
                messages.error(request, "Invalid username or password.")
    else:
        form = CustomAuthenticationForm()
    return render(request, 'user/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('login')

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful.")
            return redirect('dashboard')
        else:
            messages.error(request, "Unsuccessful registration. Invalid information.")
    else:
        form = RegisterForm()
    return render(request, 'user/register.html', {'form': form})

# @login_required
# def dashboard(request):
#     user_torrents = Torrent.objects.filter(uploader=request.user).order_by('-creation')
#     torrent_count = user_torrents.count()
#     # Handle POST actions like delete, activate, deactivate
#     if request.method == 'POST':
#         action = request.POST.get('action')
#         torrent_ids = request.POST.getlist('torrent_ids')
#         if action == 'delete':
#             Torrent.objects.filter(id__in=torrent_ids, uploader=request.user).delete()
#             messages.success(request, "Selected torrents have been deleted.")
#         elif action == 'activate':
#             Torrent.objects.filter(id__in=torrent_ids, uploader=request.user).update(is_active=True)
#             messages.success(request, "Selected torrents have been activated.")
#         elif action == 'deactivate':
#             Torrent.objects.filter(id__in=torrent_ids, uploader=request.user).update(is_active=False)
#             messages.success(request, "Selected torrents have been deactivated.")
#         return redirect('dashboard')
#     return render(request, 'user/dashboard.html', {
#         'torrents': user_torrents,
#         'torrent_count': torrent_count,
#     })
