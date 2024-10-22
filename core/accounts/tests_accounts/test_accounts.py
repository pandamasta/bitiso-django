from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core import mail
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator

from django.contrib.auth import get_user_model

User = get_user_model()  # Use the custom user model

class EmailVerificationTest(TestCase):
    def setUp(self):
        # Create a user for testing
        self.user = User.objects.create_user(
            username='testuser', email='testuser@example.com', password='password123'
        )
        self.user.is_active = False  # Simulate user needing email verification
        self.user.save()

    def test_send_verification_email(self):
        # Simulate sending the verification email
        response = self.client.post(reverse('register'), {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password1': 'password123',
            'password2': 'password123',
        })

        # Check that one email has been sent
        self.assertEqual(len(mail.outbox), 1)

        # Verify the content of the email
        email = mail.outbox[0]
        self.assertIn('Verify your email address', email.subject)
        self.assertIn('testuser@example.com', email.to)

    def verify_email(request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)  # Use the custom user model
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            messages.success(request, "Your email has been verified.")
            return redirect('home')
        else:
            messages.error(request, "The verification link is invalid.")
            return redirect('home')

class PasswordResetTest(TestCase):
    def setUp(self):
        # Create a user for testing
        self.user = User.objects.create_user(
            username='testuser', email='testuser@example.com', password='password123'
        )

    def test_password_reset_email(self):
        # Request a password reset
        response = self.client.post(reverse('password_reset'), {
            'email': 'testuser@example.com',
        })

        # Check that one email has been sent
        self.assertEqual(len(mail.outbox), 1)

        # Verify the email content
        email = mail.outbox[0]
        self.assertIn('Password reset', email.subject)
        self.assertIn('testuser@example.com', email.to)

    def test_password_reset_confirm(self):
        # Generate token and user ID for the password reset link
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = default_token_generator.make_token(self.user)
        reset_url = reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token})

        # Simulate accessing the password reset link
        response = self.client.get(reset_url)
        self.assertEqual(response.status_code, 200)

        # Simulate setting a new password
        response = self.client.post(reset_url, {
            'new_password1': 'newpassword123',
            'new_password2': 'newpassword123',
        })

        # Check that the response is a 302 redirect (indicating success)
        self.assertEqual(response.status_code, 302)

        # Reload the user from the database
        self.user.refresh_from_db()

        # Check that the password was updated
        self.assertTrue(self.user.check_password('newpassword123'))
        self.assertRedirects(response, reverse('password_reset_complete'))
