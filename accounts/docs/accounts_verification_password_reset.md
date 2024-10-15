# Email Verification and Password Reset

This document provides details on how email verification and password reset are implemented in the `accounts` app.

## Overview

The `accounts` app includes:
- **Email Verification**: Ensures that users verify their email addresses before logging in.
- **Password Reset**: Allows users to securely reset their password via email.

### Email Verification Workflow

1. **User Registration**:
   - When a user registers, their account is created with `is_active=False`.
   - A verification email with a unique link is sent to the user's email address.

2. **Verification Link**:
   - The link contains a token generated using Django's `default_token_generator`.
   - Example URL: `/accounts/verify/<uid>/<token>/`.

3. **Token Validation**:
   - Upon clicking the link, the system verifies the token.
   - If the token is valid, the user's account is activated (`is_active=True`), and they can log in.

### Password Reset Workflow

1. **Password Reset Request**:
   - Users can request a password reset link, which is sent to their email.

2. **Reset Link**:
   - The link contains the user's ID and a token.
   - Example URL: `/accounts/reset/<uid>/<token>/`.

3. **Token Validation**:
   - When the user clicks the link, Django validates the token.
   - If the token is valid, the user is prompted to set a new password.

### Token Generation and Validation

Django's token generator creates a token based on:
- **User's primary key**
- **Password hash**
- **Timestamp**
- **`is_active` status**

Tokens are not stored in the database but are generated dynamically. Token validation ensures the integrity of the request and verifies the user’s state.

### Debugging

To enable debugging for token validation, set `DEBUG = True` in `settings.py`. This will log detailed information about the token generation and validation process.

---

### Step 3: Update the Main README to Reference the New Documentation

Add a reference to the new file in the main README:

```markdown
