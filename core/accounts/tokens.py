# accounts/tokens.py

from django.contrib.auth.tokens import PasswordResetTokenGenerator

class CustomTokenGenerator(PasswordResetTokenGenerator):
    pass

custom_token_generator = CustomTokenGenerator()
