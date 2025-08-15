import os
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
import redis
from twilio.rest import Client
import logging

logger = logging.getLogger(__name__)

class OTPService:
    def __init__(self):
        # Redis for OTP storage
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        try:
            self.redis_client = redis.from_url(redis_url, decode_responses=True)
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}. Using in-memory storage.")
            self.redis_client = None
            self._memory_store = {}

        # Twilio for SMS
        self.twilio_client = None
        if os.getenv("TWILIO_ACCOUNT_SID") and os.getenv("TWILIO_AUTH_TOKEN"):
            self.twilio_client = Client(
                os.getenv("TWILIO_ACCOUNT_SID"),
                os.getenv("TWILIO_AUTH_TOKEN")
            )
            self.twilio_phone = os.getenv("TWILIO_PHONE_NUMBER")

        # SMTP for email
        self.smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_username = os.getenv("SMTP_USERNAME")
        self.smtp_password = os.getenv("SMTP_PASSWORD")

    def generate_otp(self) -> str:
        """Generate a 6-digit OTP"""
        return str(random.randint(100000, 999999))

    def store_otp(self, key: str, otp: str, expiry: int = 300) -> bool:
        """Store OTP with expiry (default 5 minutes)"""
        try:
            if self.redis_client:
                self.redis_client.setex(key, expiry, otp)
            else:
                # Fallback to in-memory storage (not recommended for production)
                self._memory_store[key] = otp
            return True
        except Exception as e:
            logger.error(f"Failed to store OTP: {e}")
            return False

    def verify_otp(self, key: str, provided_otp: str) -> bool:
        """Verify OTP"""
        try:
            if self.redis_client:
                stored_otp = self.redis_client.get(key)
            else:
                stored_otp = self._memory_store.get(key)
            
            if stored_otp and stored_otp == provided_otp:
                # Delete OTP after successful verification
                if self.redis_client:
                    self.redis_client.delete(key)
                else:
                    self._memory_store.pop(key, None)
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to verify OTP: {e}")
            return False

    def send_email_otp(self, email: str, otp: str) -> bool:
        """Send OTP via email"""
        if not self.smtp_username or not self.smtp_password:
            logger.warning("SMTP credentials not configured")
            return False

        try:
            msg = MIMEMultipart()
            msg['From'] = self.smtp_username
            msg['To'] = email
            msg['Subject'] = "Your E-Commerce Verification Code"

            body = f"""
            Your verification code is: {otp}
            
            This code will expire in 5 minutes.
            If you didn't request this code, please ignore this email.
            
            Best regards,
            E-Commerce Team
            """
            
            msg.attach(MIMEText(body, 'plain'))

            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                text = msg.as_string()
                server.sendmail(self.smtp_username, email, text)
            
            logger.info(f"OTP sent successfully to {email}")
            return True
        except Exception as e:
            logger.error(f"Failed to send email OTP: {e}")
            return False

    def send_sms_otp(self, phone: str, otp: str) -> bool:
        """Send OTP via SMS"""
        if not self.twilio_client:
            logger.warning("Twilio not configured")
            return False

        try:
            message = self.twilio_client.messages.create(
                body=f"Your E-Commerce verification code is: {otp}. Valid for 5 minutes.",
                from_=self.twilio_phone,
                to=phone
            )
            logger.info(f"SMS OTP sent successfully to {phone}: {message.sid}")
            return True
        except Exception as e:
            logger.error(f"Failed to send SMS OTP: {e}")
            return False

    def send_otp(self, contact: str, method: str = "email") -> Optional[str]:
        """Send OTP via specified method"""
        otp = self.generate_otp()
        
        # Store OTP
        key = f"otp:{method}:{contact}"
        if not self.store_otp(key, otp):
            return None

        # Send OTP
        if method == "email":
            success = self.send_email_otp(contact, otp)
        elif method == "sms":
            success = self.send_sms_otp(contact, otp)
        else:
            logger.error(f"Unsupported OTP method: {method}")
            return None

        return otp if success else None

    def verify_contact_otp(self, contact: str, method: str, provided_otp: str) -> bool:
        """Verify OTP for a contact using specified method"""
        key = f"otp:{method}:{contact}"
        return self.verify_otp(key, provided_otp)

# Global OTP service instance
otp_service = OTPService()