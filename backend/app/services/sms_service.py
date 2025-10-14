"""SMS notification service using Twilio."""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

try:
    from twilio.rest import Client
    from twilio.base.exceptions import TwilioException
    TWILIO_AVAILABLE = True
except ImportError:
    TWILIO_AVAILABLE = False
    Client = None
    TwilioException = Exception

from ..core.config import settings

logger = logging.getLogger(__name__)


class SMSService:
    """Handle SMS notifications via Twilio."""

    def __init__(self):
        if not TWILIO_AVAILABLE:
            logger.warning("Twilio not available. SMS functionality will be disabled.")
            self.client = None
            return
            
        self.account_sid = getattr(settings, 'twilio_account_sid', '')
        self.auth_token = getattr(settings, 'twilio_auth_token', '')
        self.from_number = getattr(settings, 'twilio_from_number', '')
        
        if self.account_sid and self.auth_token:
            try:
                self.client = Client(self.account_sid, self.auth_token)
                logger.info("Twilio SMS service initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Twilio client: {str(e)}")
                self.client = None
        else:
            logger.warning("Twilio credentials not configured. SMS functionality disabled.")
            self.client = None

    async def send_sms(
        self,
        to_number: str,
        message: str,
        from_number: Optional[str] = None
    ) -> bool:
        """
        Send an SMS notification.
        
        Args:
            to_number: Recipient phone number (E.164 format)
            message: SMS message content
            from_number: Sender phone number (uses default if not provided)
            
        Returns:
            bool: True if SMS was sent successfully, False otherwise
        """
        if not self.client:
            logger.error("SMS service not available - Twilio not configured")
            return False
            
        try:
            # Clean and validate phone number
            to_number = self._clean_phone_number(to_number)
            if not to_number:
                logger.error(f"Invalid phone number format: {to_number}")
                return False

            # Send SMS
            message_obj = self.client.messages.create(
                body=message,
                from_=from_number or self.from_number,
                to=to_number
            )
            
            logger.info(f"SMS sent successfully to {to_number}, SID: {message_obj.sid}")
            return True

        except TwilioException as e:
            logger.error(f"Twilio error sending SMS to {to_number}: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Failed to send SMS to {to_number}: {str(e)}")
            return False

    async def send_templated_sms(
        self,
        to_number: str,
        template_name: str,
        context: Dict[str, Any],
        from_number: Optional[str] = None
    ) -> bool:
        """
        Send an SMS using a template.
        
        Args:
            to_number: Recipient phone number (E.164 format)
            template_name: Name of the SMS template
            context: Template context data
            from_number: Sender phone number (uses default if not provided)
            
        Returns:
            bool: True if SMS was sent successfully, False otherwise
        """
        try:
            # Get template
            template = await self._get_template(template_name)
            if not template:
                logger.error(f"SMS template '{template_name}' not found")
                return False

            # Render template
            message = template.render(**context)
            
            # Ensure message is within SMS limits (160 chars for single SMS)
            if len(message) > 160:
                logger.warning(f"SMS message length ({len(message)}) exceeds 160 characters")

            return await self.send_sms(
                to_number=to_number,
                message=message,
                from_number=from_number
            )

        except Exception as e:
            logger.error(f"Failed to send templated SMS to {to_number}: {str(e)}")
            return False

    def _clean_phone_number(self, phone_number: str) -> Optional[str]:
        """Clean and format phone number to E.164 format."""
        import re
        
        # Remove all non-digit characters
        cleaned = re.sub(r'\D', '', phone_number)
        
        # Handle different formats
        if cleaned.startswith('0'):
            # Remove leading 0 and assume it's a local number
            cleaned = cleaned[1:]
        elif not cleaned.startswith('+'):
            # Assume it's a local number without country code
            pass
        
        # Add country code if not present (assuming Uganda +256)
        if not cleaned.startswith('256') and len(cleaned) == 9:
            cleaned = '256' + cleaned
        
        # Format as E.164
        if len(cleaned) >= 10:
            return '+' + cleaned
        
        return None

    async def _get_template(self, template_name: str) -> Optional[str]:
        """Get SMS template by name."""
        # SMS templates (plain text only, no HTML)
        templates = {
            'welcome': """
Welcome to LifeLine-ICT! Your account has been created successfully. 
Email: {{ user_email }}
Keep your credentials secure.
            """.strip(),
            
            'password_reset': """
Password reset requested for LifeLine-ICT account.
Reset link: {{ reset_link }}
Expires in {{ expiry_hours }} hours.
If you didn't request this, please ignore.
            """.strip(),
            
            'alert_notification': """
ALERT: {{ alert_type }} at {{ location }}
Severity: {{ severity }}
Time: {{ alert_time }}
Description: {{ description }}
Please check system for details.
            """.strip(),
            
            'maintenance_reminder': """
Maintenance Reminder: {{ resource_name }}
Location: {{ location }}
Date: {{ scheduled_date }}
Description: {{ description }}
Plan accordingly.
            """.strip(),
            
            'verification_code': """
Your LifeLine-ICT verification code is: {{ verification_code }}
This code expires in {{ expiry_minutes }} minutes.
Do not share this code with anyone.
            """.strip(),
            
            'ticket_update': """
Ticket Update: {{ ticket_id }}
Status: {{ status }}
{{ message }}
Check system for details.
            """.strip()
        }
        
        template_content = templates.get(template_name)
        if template_content:
            from jinja2 import Template
            return Template(template_content)
        
        return None

    async def validate_phone_number(self, phone_number: str) -> bool:
        """Validate phone number format."""
        cleaned = self._clean_phone_number(phone_number)
        return cleaned is not None

    async def get_message_status(self, message_sid: str) -> Optional[Dict[str, Any]]:
        """Get delivery status of a sent message."""
        if not self.client:
            return None
            
        try:
            message = self.client.messages(message_sid).fetch()
            return {
                'sid': message.sid,
                'status': message.status,
                'error_code': message.error_code,
                'error_message': message.error_message,
                'date_created': message.date_created,
                'date_sent': message.date_sent,
                'date_updated': message.date_updated
            }
        except TwilioException as e:
            logger.error(f"Failed to get message status for {message_sid}: {str(e)}")
            return None

    async def test_connection(self) -> bool:
        """Test Twilio connection."""
        if not self.client:
            return False
            
        try:
            # Try to fetch account info to test connection
            account = self.client.api.accounts(self.account_sid).fetch()
            return account.status == 'active'
        except Exception as e:
            logger.error(f"Twilio connection test failed: {str(e)}")
            return False

    async def get_account_balance(self) -> Optional[float]:
        """Get Twilio account balance."""
        if not self.client:
            return None
            
        try:
            balance = self.client.balance.fetch()
            return float(balance.balance)
        except Exception as e:
            logger.error(f"Failed to get account balance: {str(e)}")
            return None
