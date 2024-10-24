# Core User Profiles

This README provides guidance on how to use and extend the `core.user_profiles` app in a Django project.

## Overview

The `core.user_profiles` app provides a generic framework for managing user profiles, which can be extended by individual projects for specific use cases. The app defines an abstract `AbstractUserProfile` model that should be inherited and extended in a project-specific app.

The core app handles generic profile operations like storing a profile picture, a bio, and ensuring that profiles are properly associated with Django’s user model (`AUTH_USER_MODEL`).

## Features

- **Abstract UserProfile Model**: Contains fields for profile picture and bio, with support for validation and file management.
- **Automatic Profile Creation**: When a new user is created, the associated profile is automatically created.
- **Profile Management**: Generic views for displaying and editing user profiles, easily extended by the project-specific app.
- **Signal-based Profile Management**: Signals to automatically create or update the user profile upon user creation or update.

## How to Extend in Your Project

To use the core `user_profiles` app in your project, you need to create a new app that extends the `AbstractUserProfile` model and provides any project-specific functionality. Here is how you can set it up.

### 1. Install `core.user_profiles`

In your `settings.py`, add `core.user_profiles` to the `INSTALLED_APPS`:

```
INSTALLED_APPS = [
    ...
    'core.user_profiles',
    ...
]
```

### 2. Create a Project-Specific App

Create a new app (e.g., `my_project_user_profiles`) that will extend the core `AbstractUserProfile` model:

```
python manage.py startapp my_project_user_profiles
```

### 3. Extend `AbstractUserProfile`

In the `models.py` file of your project-specific app, inherit from `AbstractUserProfile`:

```
from core.user_profiles.models import AbstractUserProfile

class MyProjectUserProfile(AbstractUserProfile):
    # You can add project-specific fields here
    pass
```

### 4. Add Profile Signals

In your project-specific app (e.g., `my_project_user_profiles`), create `signals.py` to handle profile creation and updating:

```
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import MyProjectUserProfile

User = settings.AUTH_USER_MODEL

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        MyProjectUserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'myprojectuserprofile'):
        instance.myprojectuserprofile.save()
```

### 5. Register Signals

In your project-specific app's `apps.py`, ensure the signals are imported when the app is ready:

```
from django.apps import AppConfig

class MyProjectUserProfilesConfig(AppConfig):
    name = 'my_project_user_profiles'

    def ready(self):
        import my_project_user_profiles.signals
```

### 6. Add URLs for Profiles

Create URLs in your project-specific app (`urls.py`), and ensure you include them in the main project’s URL configuration.

For example, in `urls.py` of your project-specific app:

```
from django.urls import path
from .views import MyProjectUserProfileView, MyProjectUserProfileEditView

urlpatterns = [
    path('<uuid:uuid>/', MyProjectUserProfileView.as_view(), name='profile_view'),
    path('<uuid:uuid>/edit/', MyProjectUserProfileEditView.as_view(), name='profile_edit'),
]
```

And in the main project’s `urls.py`:

```
urlpatterns = [
    path('profiles/', include('my_project_user_profiles.urls')),
    ...
]
```

### 7. Override Views if Needed

If you need to modify the profile views, inherit from the core views (`ProfileView` and `ProfileEditView`) and override them in your project-specific app:

```
from core.user_profiles.views import ProfileView, ProfileEditView
from .models import MyProjectUserProfile

class MyProjectUserProfileView(ProfileView):
    def get_profile_model(self):
        return MyProjectUserProfile

class MyProjectUserProfileEditView(ProfileEditView):
    def get_profile_model(self):
        return MyProjectUserProfile
```

### 8. Templates

You can use the generic templates from the core app or override them in your project-specific app by creating your own `templates/user_profiles/` folder and placing templates like `profile_detail.html` and `profile_edit.html` there.

For example, you might create a `profile_detail.html`:

```
{% extends 'base.html' %}

{% block content %}
<h2>{{ profile_user.username }}'s Profile</h2>

{% if profile.profile_picture %}
    <img src="{{ profile.profile_picture.url }}" alt="{{ profile_user.username }}">
{% endif %}

<p><strong>Bio:</strong> {{ profile.bio }}</p>
{% endblock %}
```

## Conclusion

By following this guide, you will be able to create user profiles that inherit from a generic core system and extend them with project-specific functionality. The abstract nature of `core.user_profiles` ensures flexibility and reusability across different projects.


This `README.md` file outlines how to consume the core user profile logic in different Django projects by creating project-specific apps and extending the core logic. It explains how to use the abstract model, signals, views, and templates to manage profiles while keeping the core app reusable.