import os
from flask import current_app, render_template
from flask_mail import Mail, Message

mail = Mail()

def send_password_reset_email(user, reset_url):
    """Send password reset email to user"""
    try:
        msg = Message(
            'Password Reset Request - Trackify',
            sender=current_app.config.get('MAIL_DEFAULT_SENDER', 'noreply@trackify.com'),
            recipients=[user.email]
        )
        
        msg.html = render_template(
            'emails/password_reset.html',
            user=user,
            reset_url=reset_url
        )
        
        msg.body = render_template(
            'emails/password_reset.txt',
            user=user,
            reset_url=reset_url
        )
        
        mail.send(msg)
        return True
    except Exception as e:
        current_app.logger.error(f"Failed to send password reset email: {e}")
        return False

def send_password_changed_email(user):
    """Send confirmation email when password is changed"""
    try:
        msg = Message(
            'Password Changed - Trackify',
            sender=current_app.config.get('MAIL_DEFAULT_SENDER', 'noreply@trackify.com'),
            recipients=[user.email]
        )
        
        msg.html = render_template('emails/password_changed.html', user=user)
        msg.body = render_template('emails/password_changed.txt', user=user)
        
        mail.send(msg)
        return True
    except Exception as e:
        current_app.logger.error(f"Failed to send password changed email: {e}")
        return False
