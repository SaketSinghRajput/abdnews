# Authentication System Documentation

## Overview

NewsHub now has a complete JWT-based authentication system with subscription management, user profiles, and role-based access control.

## Features Implemented

### 1. Authentication (JWT-based)
- **Login**: Supports username or email login
- **Signup**: New user registration with password validation
- **Profile Management**: View and edit user profile
- **Password Change**: Secure password reset endpoint
- **Logout**: Token blacklisting and session cleanup
- **Token Refresh**: Automatic token rotation

### 2. Subscription System
- **Free Plan**: Limited access, basic features
- **Premium Plans**: Paid subscriptions with additional features
- **Subscription Tracking**: Automatic expiry tracking
- **Email Notifications**: Based on subscription level
- **Newsletter**: Enabled for premium users

### 3. User Pages
- **Dashboard** (`/pages/dashboard.html`): Main user hub with stats and quick links
- **Account** (`/pages/account.html`): Complete profile management and settings
- **Login** (`/pages/login.html`): Secure login page
- **Signup** (`/pages/signup.html`): User registration

### 4. Role-Based Access
- **Admin**: Full system access
- **Editor**: Content management
- **Journalist**: Content creation
- **Subscriber**: Standard user access

## API Endpoints

### Authentication Endpoints

#### User Registration
```
POST /api/users/auth/signup/
```
**Body:**
```json
{
    "username": "newuser",
    "email": "user@example.com",
    "password": "securepass123",
    "password_confirm": "securepass123",
    "first_name": "John",
    "last_name": "Doe",
    "phone_number": "+1234567890"
}
```

**Response:**
```json
{
    "message": "User created successfully",
    "user": {
        "id": 1,
        "username": "newuser",
        "email": "user@example.com",
        ...
    },
    "tokens": {
        "refresh": "refresh_token_here",
        "access": "access_token_here"
    }
}
```

#### User Login
```
POST /api/users/auth/login/
```
**Body:**
```json
{
    "username": "testuser",
    "password": "testpass123"
}
```

**Response:**
```json
{
    "message": "Login successful",
    "user": {
        "id": 1,
        "username": "testuser",
        "email": "testuser@example.com",
        "has_active_subscription": false,
        ...
    },
    "tokens": {
        "refresh": "refresh_token_here",
        "access": "access_token_here"
    }
}
```

#### Get User Profile
```
GET /api/users/auth/profile/
Authorization: Bearer {access_token}
```

#### Update User Profile
```
PUT /api/users/auth/profile/
Authorization: Bearer {access_token}

{
    "first_name": "John",
    "last_name": "Doe",
    "email": "newemail@example.com",
    "email_notifications": true,
    "newsletter_subscription": false
}
```

#### Change Password
```
POST /api/users/change-password/
Authorization: Bearer {access_token}

{
    "current_password": "oldpass123",
    "new_password": "newpass456"
}
```

#### Refresh Access Token
```
POST /api/users/auth/token/refresh/

{
    "refresh": "refresh_token_here"
}
```

#### Logout
```
POST /api/users/auth/logout/
Authorization: Bearer {access_token}

{
    "refresh_token": "refresh_token_here"
}
```

### Subscription Endpoints

#### Get Subscription Plans
```
GET /api/users/subscription-plans/
```

#### Get User Subscriptions
```
GET /api/users/subscriptions/
Authorization: Bearer {access_token}
```

#### Subscribe to Plan
```
POST /api/users/subscribe/
Authorization: Bearer {access_token}

{
    "plan_id": 2
}
```

## Frontend Usage

### Check if User is Authenticated
```javascript
if (isAuthenticated()) {
    console.log('User is logged in');
}
```

### Get Current User
```javascript
const user = getCurrentUser();
console.log(user.username);
console.log(user.has_active_subscription);
```

### Login
```javascript
const result = await login('testuser', 'testpass123');
if (result.success) {
    console.log('Login successful');
    console.log(result.user);
}
```

### Signup
```javascript
const result = await signup({
    username: 'newuser',
    email: 'user@example.com',
    password: 'securepass123',
    password_confirm: 'securepass123',
    first_name: 'John',
    last_name: 'Doe'
});
if (result.success) {
    console.log('Signup successful');
}
```

### Logout
```javascript
logout(); // Redirects to login page
```

### Make Authenticated Requests
```javascript
const response = await fetchWithAuth('/api/protected-endpoint/', {
    method: 'GET'
});
```

### Get Subscription Plans
```javascript
const plans = await getSubscriptionPlans();
console.log(plans);
```

### Subscribe to Plan
```javascript
const result = await subscribeToPlan(planId);
if (result.success) {
    console.log('Subscription activated');
}
```

## Test Credentials

For testing, a test user has been created:

```
Username: testuser
Email: testuser@example.com
Password: testpass123
Role: subscriber
```

Login at: `http://127.0.0.1:8000/pages/login.html`

## File Structure

### Backend
```
backend/apps/users/
├── models.py                 # CustomUser, SubscriptionPlan, UserSubscription
├── serializers.py            # API serializers for all models
├── auth_views.py            # Authentication views (Login, Signup, Profile, etc)
├── permissions.py           # Custom permission classes
├── urls.py                  # API URL routing
└── email_utils.py           # Email sending functions
```

### Frontend
```
frontend/
├── pages/
│   ├── login.html           # Login page
│   ├── signup.html          # Signup page
│   ├── dashboard.html       # User dashboard
│   └── account.html         # Account management
├── assets/js/
│   ├── auth.js              # Authentication functions
│   ├── api.js               # API helper functions
│   └── app.js               # Main app logic
└── components/
    └── header.html          # Dynamic header with auth buttons
```

## Security Features

1. **JWT Tokens**: Secure token-based authentication
2. **Token Refresh**: Automatic token rotation with refresh tokens
3. **CSRF Protection**: Exempt for API endpoints, enabled for forms
4. **Password Hashing**: Django's built-in password hashing
5. **Token Blacklisting**: Logout blacklists refresh tokens
6. **Session Security**: Secure session configuration
7. **Permission Classes**: Role-based access control

## Email Notifications

### Triggers
- **Welcome Email**: Sent on signup
- **Subscription Confirmation**: Sent when subscribing to a plan
- **Newsletter**: Weekly digest for premium subscribers
- **Subscription Expiry**: Reminder before subscription ends

### Configuration
Email backend is configured in `config/settings.py`:

```python
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'  # Console in dev
EMAIL_HOST = 'smtp.gmail.com'  # Gmail in production
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'
DEFAULT_FROM_EMAIL = 'NewsHub <noreply@newshub.com>'
```

## Troubleshooting

### Issue: Login button doesn't work
**Solution**: Check browser console for errors. Ensure backend is running at `http://127.0.0.1:8000/`

### Issue: Tokens not persisting
**Solution**: Clear browser localStorage and try again. Check if cookies are enabled.

### Issue: Getting "Unauthorized" on profile page
**Solution**: Token might be expired. Refresh the page or logout and login again.

### Issue: Email not sending
**Solution**: Check email configuration in settings.py. For Gmail, use app-specific password.

## Next Steps

1. Configure email with production SMTP
2. Add two-factor authentication (2FA)
3. Implement password reset via email
4. Add social login (Google, Facebook, etc)
5. Implement payment gateway for subscriptions
6. Add user preferences and settings
7. Implement activity logs

## Support

For issues or questions, refer to the Django REST Framework documentation:
- https://www.django-rest-framework.org/
- https://django-rest-framework-simplejwt.readthedocs.io/
