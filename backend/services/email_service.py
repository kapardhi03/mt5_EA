"""
Email service for MT5 Copy Trading Platform
Handles email sending using SMTP with Nodemailer-like functionality
"""
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import Dict, List, Optional
from datetime import datetime
from backend.core.config import settings
import logging

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        self.smtp_server = settings.SMTP_SERVER
        self.smtp_port = settings.SMTP_PORT
        self.email_username = settings.EMAIL_USERNAME
        self.email_password = settings.EMAIL_PASSWORD
        self.email_from = settings.EMAIL_FROM or settings.EMAIL_USERNAME
        
    def _create_smtp_connection(self):
        """Create SMTP connection with proper security"""
        try:
            # Create SMTP connection
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            
            # Enable security
            if self.smtp_port == 587:
                server.starttls()  # Enable TLS encryption
            elif self.smtp_port == 465:
                # SSL connection for port 465
                context = ssl.create_default_context()
                server = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port, context=context)
            
            # Login to email account
            if self.email_username and self.email_password:
                server.login(self.email_username, self.email_password)
            
            return server
        except Exception as e:
            logger.error(f"Failed to create SMTP connection: {str(e)}")
            return None
    
    async def send_email(self, to_email: str, subject: str, body: str, 
                        html_body: str = None, attachments: List[Dict] = None) -> Dict:
        """Send email with optional HTML body and attachments"""
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = self.email_from
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Add text body
            text_part = MIMEText(body, 'plain', 'utf-8')
            msg.attach(text_part)
            
            # Add HTML body if provided
            if html_body:
                html_part = MIMEText(html_body, 'html', 'utf-8')
                msg.attach(html_part)
            
            # Add attachments if provided
            if attachments:
                for attachment in attachments:
                    self._add_attachment(msg, attachment)
            
            # Send email
            server = self._create_smtp_connection()
            if not server:
                return {"status": False, "message": "Failed to connect to email server"}
            
            text = msg.as_string()
            server.sendmail(self.email_from, to_email, text)
            server.quit()
            
            logger.info(f"Email sent successfully to {to_email}")
            return {"status": True, "message": "Email sent successfully"}
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return {"status": False, "message": f"Email sending failed: {str(e)}"}
    
    def _add_attachment(self, msg: MIMEMultipart, attachment: Dict):
        """Add attachment to email message"""
        try:
            filename = attachment.get('filename', 'attachment')
            content = attachment.get('content', '')
            content_type = attachment.get('content_type', 'application/octet-stream')
            
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(content)
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename= {filename}')
            msg.attach(part)
        except Exception as e:
            logger.error(f"Failed to add attachment: {str(e)}")
    
    async def send_otp_email(self, to_email: str, otp: str, purpose: str = "verification") -> Dict:
        """Send OTP verification email"""
        subject = f"MT5 Copy Trading - {purpose.title()} Code"
        
        # Plain text body
        text_body = f"""
Dear User,

Your MT5 Copy Trading {purpose} code is: {otp}

This code will expire in 5 minutes.
If you didn't request this code, please ignore this email.

Best regards,
MT5 Copy Trading Team
        """.strip()
        
        # HTML body
        html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MT5 Copy Trading - {purpose.title()} Code</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            text-align: center;
            border-radius: 8px 8px 0 0;
        }}
        .content {{
            background: #f8f9fa;
            padding: 30px;
            border-radius: 0 0 8px 8px;
        }}
        .otp-code {{
            background: #007bff;
            color: white;
            font-size: 32px;
            font-weight: bold;
            text-align: center;
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
            letter-spacing: 5px;
        }}
        .warning {{
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            color: #856404;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
        }}
        .footer {{
            text-align: center;
            margin-top: 30px;
            color: #666;
            font-size: 14px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>MT5 Copy Trading</h1>
        <p>{purpose.title()} Code</p>
    </div>
    <div class="content">
        <h2>Hello!</h2>
        <p>Your {purpose} code is:</p>
        <div class="otp-code">{otp}</div>
        <div class="warning">
            <strong>Important:</strong> This code will expire in 5 minutes. Do not share this code with anyone.
        </div>
        <p>If you didn't request this code, please ignore this email.</p>
    </div>
    <div class="footer">
        <p>Best regards,<br>MT5 Copy Trading Team</p>
        <p>This is an automated message. Please do not reply to this email.</p>
    </div>
</body>
</html>
        """.strip()
        
        return await self.send_email(to_email, subject, text_body, html_body)
    
    async def send_welcome_email(self, to_email: str, user_name: str) -> Dict:
        """Send welcome email to new user"""
        subject = "Welcome to MT5 Copy Trading Platform"
        
        text_body = f"""
Dear {user_name},

Welcome to MT5 Copy Trading Platform!

Your account has been created successfully. Here's what you can do next:

1. Complete your profile setup
2. Verify your trading account details
3. Join a trading group
4. Start copy trading

If you have any questions, please contact our support team.

Best regards,
MT5 Copy Trading Team
        """.strip()
        
        html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Welcome to MT5 Copy Trading</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
            border-radius: 8px 8px 0 0;
        }}
        .content {{
            background: #f8f9fa;
            padding: 30px;
            border-radius: 0 0 8px 8px;
        }}
        .welcome-message {{
            font-size: 24px;
            color: #007bff;
            margin-bottom: 20px;
        }}
        .steps {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
        }}
        .step {{
            margin: 15px 0;
            padding: 10px;
            border-left: 4px solid #007bff;
            background: #f8f9fa;
        }}
        .cta-button {{
            display: inline-block;
            background: #007bff;
            color: white;
            padding: 15px 30px;
            text-decoration: none;
            border-radius: 5px;
            margin: 20px 0;
        }}
        .footer {{
            text-align: center;
            margin-top: 30px;
            color: #666;
            font-size: 14px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Welcome to MT5 Copy Trading!</h1>
    </div>
    <div class="content">
        <div class="welcome-message">Hello {user_name}!</div>
        <p>Your account has been created successfully. We're excited to have you on board!</p>
        
        <div class="steps">
            <h3>Next Steps:</h3>
            <div class="step">
                <strong>1. Complete Profile Setup</strong><br>
                Add your trading account details and preferences
            </div>
            <div class="step">
                <strong>2. Verify Trading Account</strong><br>
                Verify your broker account details
            </div>
            <div class="step">
                <strong>3. Join Trading Group</strong><br>
                Choose a trading group that matches your strategy
            </div>
            <div class="step">
                <strong>4. Start Copy Trading</strong><br>
                Begin copying trades from master traders
            </div>
        </div>
        
        <p>If you have any questions, please don't hesitate to contact our support team.</p>
        
        <a href="#" class="cta-button">Get Started</a>
    </div>
    <div class="footer">
        <p>Best regards,<br>MT5 Copy Trading Team</p>
        <p>This is an automated message. Please do not reply to this email.</p>
    </div>
</body>
</html>
        """.strip()
        
        return await self.send_email(to_email, subject, text_body, html_body)
    
    async def send_ib_approval_email(self, to_email: str, user_name: str, status: str) -> Dict:
        """Send IB approval status email"""
        subject = f"MT5 Copy Trading - IB Change {status.title()}"
        
        if status == "approved":
            text_body = f"""
Dear {user_name},

Great news! Your IB change request has been approved.

Your account is now fully activated and you can start using all EA features.

Best regards,
MT5 Copy Trading Team
            """.strip()
        else:
            text_body = f"""
Dear {user_name},

Your IB change request has been {status}.

Please contact support for more information.

Best regards,
MT5 Copy Trading Team
            """.strip()
        
        return await self.send_email(to_email, subject, text_body)
    
    async def send_password_reset_email(self, to_email: str, reset_token: str, user_name: str) -> Dict:
        """Send password reset email"""
        subject = "MT5 Copy Trading - Password Reset"
        
        reset_url = f"https://mt5-copytrade.onrender.com/reset-password?token={reset_token}"
        
        text_body = f"""
Dear {user_name},

You requested a password reset for your MT5 Copy Trading account.

Click the link below to reset your password:
{reset_url}

This link will expire in 24 hours.

If you didn't request this reset, please ignore this email.

Best regards,
MT5 Copy Trading Team
        """.strip()
        
        html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Password Reset - MT5 Copy Trading</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            text-align: center;
            border-radius: 8px 8px 0 0;
        }}
        .content {{
            background: #f8f9fa;
            padding: 30px;
            border-radius: 0 0 8px 8px;
        }}
        .reset-button {{
            display: inline-block;
            background: #dc3545;
            color: white;
            padding: 15px 30px;
            text-decoration: none;
            border-radius: 5px;
            margin: 20px 0;
        }}
        .warning {{
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            color: #856404;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
        }}
        .footer {{
            text-align: center;
            margin-top: 30px;
            color: #666;
            font-size: 14px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Password Reset</h1>
    </div>
    <div class="content">
        <h2>Hello {user_name}!</h2>
        <p>You requested a password reset for your MT5 Copy Trading account.</p>
        
        <a href="{reset_url}" class="reset-button">Reset Password</a>
        
        <div class="warning">
            <strong>Important:</strong> This link will expire in 24 hours. If you didn't request this reset, please ignore this email.
        </div>
    </div>
    <div class="footer">
        <p>Best regards,<br>MT5 Copy Trading Team</p>
        <p>This is an automated message. Please do not reply to this email.</p>
    </div>
</body>
</html>
        """.strip()
        
        return await self.send_email(to_email, subject, text_body, html_body)

# Create singleton instance
email_service = EmailService()
