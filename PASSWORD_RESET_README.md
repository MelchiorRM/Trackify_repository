# Password Reset Functionality

## Overview

The Trackify application now includes a complete password reset system that allows users to securely reset their passwords via email. This feature includes:

- **Secure token generation** with 1-hour expiration
- **Email-based password reset** with HTML and plain text templates
- **User-friendly interface** with proper error handling
- **Security best practices** including token expiration and validation

## Features

### 🔐 Security Features
- **Secure token generation** using `secrets` module
- **1-hour token expiration** for security
- **Token validation** with expiry checking
- **Automatic token cleanup** after use
- **Email confirmation** when password is changed

### 📧 Email System
- **HTML and plain text** email templates
- **Professional styling** with Trackify branding
- **Clear instructions** and security warnings
- **Responsive design** for mobile devices

### 🎨 User Interface
- **Modern Bootstrap styling** consistent with the app
- **Clear error messages** and validation feedback
- **Intuitive navigation** with proper links
- **Accessibility features** with proper labels and structure

## Database Changes

### New Columns Added to `users` Table
```sql
ALTER TABLE users ADD COLUMN reset_token VARCHAR(100);
ALTER TABLE users ADD COLUMN reset_token_expiry DATETIME;
CREATE INDEX idx_users_reset_token ON users(reset_token);
```

### User Model Methods
```python
def generate_reset_token(self):
    """Generate a secure reset token with 1-hour expiry"""
    
def verify_reset_token(self, token):
    """Verify if the reset token is valid and not expired"""
    
def clear_reset_token(self):
    """Clear the reset token after use"""
```

## Routes Added

### 1. Request Password Reset
- **URL**: `/request_password_reset`
- **Methods**: GET, POST
- **Template**: `request_password_reset.html`
- **Function**: Sends password reset email

### 2. Reset Password
- **URL**: `/reset_password/<token>`
- **Methods**: GET, POST
- **Template**: `reset_password.html`
- **Function**: Allows user to set new password

## Email Templates

### Password Reset Request Email
- **HTML**: `templates/emails/password_reset.html`
- **Plain Text**: `templates/emails/password_reset.txt`
- **Features**: Professional styling, clear instructions, security warnings

### Password Changed Confirmation Email
- **HTML**: `templates/emails/password_changed.html`
- **Plain Text**: `templates/emails/password_changed.txt`
- **Features**: Confirmation message, security notice

## Configuration

### Email Settings (config.py)
```python
# Email config
MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.gmail.com'
MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() == 'true'
MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL', 'false').lower() == 'true'
MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER') or 'noreply@trackify.com'
```

### Environment Variables Required
```bash
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=noreply@trackify.com
```

## Installation & Setup

### 1. Install Dependencies
```bash
pip install Flask-Mail==0.9.1
```

### 2. Run Database Migration
```bash
python migrate_password_reset.py
```

### 3. Configure Email Settings
Set the required environment variables for your email provider.

### 4. Test the Functionality
```bash
python test_password_reset_simple.py
```

## Usage Flow

### 1. User Requests Password Reset
1. User clicks "Forgot Password?" on login page
2. User enters email address
3. System validates email exists
4. System generates secure token
5. System sends email with reset link

### 2. User Resets Password
1. User clicks link in email
2. System validates token and expiry
3. User enters new password
4. System updates password and clears token
5. System sends confirmation email
6. User can now login with new password

## Security Considerations

### ✅ Implemented Security Features
- **Secure token generation** using `secrets` module
- **Token expiration** (1 hour)
- **Token validation** before password reset
- **Automatic token cleanup** after use
- **Email confirmation** for password changes
- **CSRF protection** on all forms
- **Input validation** and sanitization

### 🔒 Additional Security Recommendations
- **Rate limiting** on password reset requests
- **Email verification** for new accounts
- **Two-factor authentication** for sensitive operations
- **Password strength requirements**
- **Account lockout** after failed attempts

## Troubleshooting

### Common Issues

#### 1. Email Not Sending
- Check email configuration in `config.py`
- Verify SMTP settings with your email provider
- Check firewall/network restrictions
- Use app passwords for Gmail

#### 2. Token Expired
- Tokens expire after 1 hour
- User must request new reset link
- Check server time synchronization

#### 3. Database Migration Issues
- Run `python migrate_password_reset.py`
- Check database file permissions
- Verify SQLite installation

### Debug Mode
Set `DEBUG = True` in `config.py` for detailed error messages.

## Files Added/Modified

### New Files
- `utils/email_utils.py` - Email functionality
- `templates/request_password_reset.html` - Reset request page
- `templates/reset_password.html` - Password reset page
- `templates/emails/password_reset.html` - Reset email template
- `templates/emails/password_reset.txt` - Plain text email
- `templates/emails/password_changed.html` - Confirmation email
- `templates/emails/password_changed.txt` - Plain text confirmation
- `migrate_password_reset.py` - Database migration script
- `test_password_reset_simple.py` - Test script

### Modified Files
- `models/user_model.py` - Added password reset fields and methods
- `forms/forms.py` - Added password reset forms
- `routes/user_routes.py` - Added password reset routes
- `config.py` - Added email configuration
- `app.py` - Added Flask-Mail initialization
- `requirements.txt` - Added Flask-Mail dependency
- `templates/login.html` - Added "Forgot Password?" link

## Testing

### Manual Testing
1. Start the application
2. Go to login page
3. Click "Forgot Password?"
4. Enter a valid email address
5. Check email for reset link
6. Click link and set new password
7. Verify login works with new password

### Automated Testing
```bash
python test_password_reset_simple.py
```

## Future Enhancements

### Potential Improvements
- **Rate limiting** for password reset requests
- **SMS-based reset** as alternative to email
- **Security questions** for additional verification
- **Password strength meter** in reset form
- **Account recovery** with multiple methods
- **Audit logging** for password changes

## Support

For issues or questions about the password reset functionality:
1. Check the troubleshooting section above
2. Verify email configuration
3. Test with the provided test scripts
4. Check application logs for detailed error messages
