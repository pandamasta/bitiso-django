# accounts/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

# Register the CustomUser model with the Django admin
admin.site.register(CustomUser, UserAdmin)
