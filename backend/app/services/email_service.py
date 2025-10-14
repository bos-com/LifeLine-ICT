"""Email notification service using SMTP."""

from __future__ import annotations

import asyncio
import json
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any, Dict, Optional

import aiosmtplib
from jinja2 import Template

from ..core.config import settings

logger = logging.getLogger(__name__)


class EmailService:
    """Handle email notifications via SMTP."""

    def __init__(self):
        self.smtp_host = getattr(settings, 'smtp_host', 'localhost')
        self.smtp_port = getattr(settings, 'smtp_port', 587)
        self.smtp_username = getattr(settings, 'smtp_username', '')
        self.smtp_password = getattr(settings, 'smtp_password', '')
        self.smtp_use_tls = getattr(settings, 'smtp_use_tls', True)
        self.from_email = getattr(settings, 'from_email', settings.contact_email)
        self.from_name = getattr(settings, 'from_name', 'LifeLine-ICT')

    async def send_email(
        self,
        to_email: str,
        subject: str,
        message: str,
        html_message: Optional[str] = None,
        from_email: Optional[str] = None,
        from_name: Optional[str] = None
    ) -> bool:
        """
        Send an email notification.
        
        Args:
            to_email: Recipient email address
            subject: Email subject line
            message: Plain text message content
            html_message: HTML message content (optional)
            from_email: Sender email (uses default if not provided)
            from_name: Sender name (uses default if not provided)
            
        Returns:
            bool: True if email was sent successfully, False otherwise
        """
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{from_name or self.from_name} <{from_email or self.from_email}>"
            msg['To'] = to_email

            # Add plain text part
            text_part = MIMEText(message, 'plain', 'utf-8')
            msg.attach(text_part)

            # Add HTML part if provided
            if html_message:
                html_part = MIMEText(html_message, 'html', 'utf-8')
                msg.attach(html_part)

            # Send email
            await self._send_smtp_email(msg, to_email)
            logger.info(f"Email sent successfully to {to_email}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return False

    async def send_templated_email(
        self,
        to_email: str,
        template_name: str,
        subject: str,
        context: Dict[str, Any],
        from_email: Optional[str] = None,
        from_name: Optional[str] = None
    ) -> bool:
        """
        Send an email using a template.
        
        Args:
            to_email: Recipient email address
            template_name: Name of the email template
            subject: Email subject line
            context: Template context data
            from_email: Sender email (uses default if not provided)
            from_name: Sender name (uses default if not provided)
            
        Returns:
            bool: True if email was sent successfully, False otherwise
        """
        try:
            # Get template
            template = await self._get_template(template_name)
            if not template:
                logger.error(f"Template '{template_name}' not found")
                return False

            # Render template
            rendered_template = template.render(**context)
            
            # Parse rendered content (assuming it contains both text and HTML)
            parts = rendered_template.split('---HTML---')
            text_content = parts[0].strip()
            html_content = parts[1].strip() if len(parts) > 1 else None

            return await self.send_email(
                to_email=to_email,
                subject=subject,
                message=text_content,
                html_message=html_content,
                from_email=from_email,
                from_name=from_name
            )

        except Exception as e:
            logger.error(f"Failed to send templated email to {to_email}: {str(e)}")
            return False

    async def _send_smtp_email(self, msg: MIMEMultipart, to_email: str) -> None:
        """Send email via SMTP."""
        try:
            # Connect to SMTP server
            smtp = aiosmtplib.SMTP(
                hostname=self.smtp_host,
                port=self.smtp_port,
                use_tls=self.smtp_use_tls
            )
            
            await smtp.connect()
            
            # Authenticate if credentials provided
            if self.smtp_username and self.smtp_password:
                await smtp.login(self.smtp_username, self.smtp_password)
            
            # Send email
            await smtp.send_message(msg)
            await smtp.quit()
            
        except Exception as e:
            logger.error(f"SMTP error sending email to {to_email}: {str(e)}")
            raise

    async def _get_template(self, template_name: str) -> Optional[Template]:
        """Get email template by name."""
        # This is a simplified template system
        # In a real implementation, you might load templates from files or database
        templates = {
            'welcome': Template("""
Welcome to LifeLine-ICT!

Hello {{ user_name }},

Thank you for registering with LifeLine-ICT. Your account has been created successfully.

Your account details:
- Email: {{ user_email }}
- Registration Date: {{ registration_date }}

Please keep your login credentials secure.

Best regards,
The LifeLine-ICT Team

---HTML---
<html>
<body>
    <h2>Welcome to LifeLine-ICT!</h2>
    <p>Hello {{ user_name }},</p>
    <p>Thank you for registering with LifeLine-ICT. Your account has been created successfully.</p>
    <h3>Your account details:</h3>
    <ul>
        <li>Email: {{ user_email }}</li>
        <li>Registration Date: {{ registration_date }}</li>
    </ul>
    <p>Please keep your login credentials secure.</p>
    <p>Best regards,<br>The LifeLine-ICT Team</p>
</body>
</html>
            """),
            
            'password_reset': Template("""
Password Reset Request

Hello {{ user_name }},

You have requested to reset your password for your LifeLine-ICT account.

To reset your password, please click the link below:
{{ reset_link }}

This link will expire in {{ expiry_hours }} hours.

If you did not request this password reset, please ignore this email.

Best regards,
The LifeLine-ICT Team

---HTML---
<html>
<body>
    <h2>Password Reset Request</h2>
    <p>Hello {{ user_name }},</p>
    <p>You have requested to reset your password for your LifeLine-ICT account.</p>
    <p>To reset your password, please click the link below:</p>
    <p><a href="{{ reset_link }}" style="background-color: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Reset Password</a></p>
    <p>This link will expire in {{ expiry_hours }} hours.</p>
    <p>If you did not request this password reset, please ignore this email.</p>
    <p>Best regards,<br>The LifeLine-ICT Team</p>
</body>
</html>
            """),
            
            'alert_notification': Template("""
Alert Notification

Hello {{ user_name }},

An alert has been triggered in the LifeLine-ICT system.

Alert Details:
- Alert Type: {{ alert_type }}
- Severity: {{ severity }}
- Location: {{ location }}
- Time: {{ alert_time }}
- Description: {{ description }}

Please check the system for more details and take appropriate action.

Best regards,
The LifeLine-ICT Team

---HTML---
<html>
<body>
    <h2>Alert Notification</h2>
    <p>Hello {{ user_name }},</p>
    <p>An alert has been triggered in the LifeLine-ICT system.</p>
    <h3>Alert Details:</h3>
    <ul>
        <li><strong>Alert Type:</strong> {{ alert_type }}</li>
        <li><strong>Severity:</strong> {{ severity }}</li>
        <li><strong>Location:</strong> {{ location }}</li>
        <li><strong>Time:</strong> {{ alert_time }}</li>
        <li><strong>Description:</strong> {{ description }}</li>
    </ul>
    <p>Please check the system for more details and take appropriate action.</p>
    <p>Best regards,<br>The LifeLine-ICT Team</p>
</body>
</html>
            """),
            
            'maintenance_reminder': Template("""
Maintenance Reminder

Hello {{ user_name }},

This is a reminder about an upcoming maintenance activity.

Maintenance Details:
- Resource: {{ resource_name }}
- Location: {{ location }}
- Scheduled Date: {{ scheduled_date }}
- Description: {{ description }}

Please plan accordingly for this maintenance window.

Best regards,
The LifeLine-ICT Team

---HTML---
<html>
<body>
    <h2>Maintenance Reminder</h2>
    <p>Hello {{ user_name }},</p>
    <p>This is a reminder about an upcoming maintenance activity.</p>
    <h3>Maintenance Details:</h3>
    <ul>
        <li><strong>Resource:</strong> {{ resource_name }}</li>
        <li><strong>Location:</strong> {{ location }}</li>
        <li><strong>Scheduled Date:</strong> {{ scheduled_date }}</li>
        <li><strong>Description:</strong> {{ description }}</li>
    </ul>
    <p>Please plan accordingly for this maintenance window.</p>
    <p>Best regards,<br>The LifeLine-ICT Team</p>
</body>
</html>
            """)
        }
        
        return templates.get(template_name)

    async def validate_email(self, email: str) -> bool:
        """Validate email address format."""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

    async def test_connection(self) -> bool:
        """Test SMTP connection."""
        try:
            smtp = aiosmtplib.SMTP(
                hostname=self.smtp_host,
                port=self.smtp_port,
                use_tls=self.smtp_use_tls
            )
            await smtp.connect()
            await smtp.quit()
            return True
        except Exception as e:
            logger.error(f"SMTP connection test failed: {str(e)}")
            return False
