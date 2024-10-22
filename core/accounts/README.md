## Accounts App - README

### **Overview**
This `accounts` app extends Django’s default user authentication system to handle user registration, login, logout, and profile management in a modular and portable way.

### **Extended Models**

- **CustomUser (models.py)**:
  - Extends `AbstractUser` from Django to allow for future customization (e.g., adding fields like email, bio, etc.).
  - Currently, it includes:
    - `username`: The unique username for each user.
    - `email`: The user’s email, which is set to be unique.

### **URL Configuration**

The `accounts` app includes the following URLs:

- **/accounts/register/**: User registration page.
- **/accounts/login/**: User login page.
- **/accounts/logout/**: Logs the user out (via POST).

To include these URLs in your project, add the following to your main `urls.py`:

```python
from django.urls import path, include

urlpatterns = [
    path('accounts/', include('accounts.urls')),  # Include accounts URLs
]
```

### **Functions (Views)**

1. **Register** (`register` in `views.py`):
   - Handles user registration.
   - Redirects the user to the home page after successful registration and login.
   - Template: `accounts/register.html`.
   
2. **Login/Logout**:
   - Uses Django’s built-in `LoginView` and `LogoutView` for handling user authentication.
   - **Login**: Redirects to the homepage after successful login.
   - **Logout**: Logs out the user using a POST request and redirects to the homepage.

### **Admin Integration**

- **CustomUser Registration**:
  The `CustomUser` model is registered in the Django admin, allowing user management in the admin interface. To customize the user admin interface, the `CustomUserAdmin` class is used, extending Django’s default `UserAdmin` to control the fields displayed and managed.

  In `accounts/admin.py`, the `CustomUser` model is registered like this:

  ```python
  from django.contrib import admin
  from django.contrib.auth.admin import UserAdmin
  from .models import CustomUser

  admin.site.register(CustomUser, UserAdmin)
  ```

  This setup enables user management (add, edit, delete users) in the admin panel.

### **Additional Configuration**

- **LOGIN_REDIRECT_URL**: Set to `'/'` in `settings.py` to redirect users to the home page after login.
- **Custom Context Processor**: The project name (`PROJECT_NAME`) is passed to all templates globally for dynamic use in templates like "Welcome to ProjectName."

This `accounts` app is designed to be modular and reusable across different projects. You can extend the `CustomUser` model further if needed, and the URLs can easily be integrated into any project.

### Password Reset and Email Verification

For more details on how email verification and password reset are implemented, see [Email Verification and Password Reset](docs/accounts_verification_password_reset.md).
