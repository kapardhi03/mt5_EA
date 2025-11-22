// SMS/OTP Service for EA Trading Platform
// This service handles SMS sending and OTP verification

class SMSService {
  constructor() {
    this.apiKey = process.env.NEXT_PUBLIC_SMS_API_KEY || 'demo-key';
    this.baseURL = process.env.NEXT_PUBLIC_SMS_API_URL || 'https://api.twilio.com/2010-04-01';
    this.isDemoMode = process.env.NODE_ENV === 'development' || !process.env.NEXT_PUBLIC_SMS_API_KEY;

    // Store OTPs in memory for demo (in production, use database)
    this.otpStore = new Map();
  }

  // Generate 6-digit OTP
  generateOTP() {
    return Math.floor(100000 + Math.random() * 900000).toString();
  }

  // Send SMS with OTP
  async sendOTP(phoneNumber, userType = 'user') {
    try {
      const otp = this.generateOTP();
      const expiryTime = Date.now() + (5 * 60 * 1000); // 5 minutes expiry

      // Store OTP with expiry
      this.otpStore.set(phoneNumber, {
        otp,
        expiryTime,
        userType,
        attempts: 0,
        maxAttempts: 3
      });

      if (this.isDemoMode) {
        // Demo mode - just log and return success
        console.log(`📱 Demo SMS Service:`);
        console.log(`To: ${phoneNumber}`);
        console.log(`OTP: ${otp}`);
        console.log(`User Type: ${userType}`);
        console.log(`Expires: ${new Date(expiryTime).toLocaleTimeString()}`);

        // Show user-friendly notification
        this.showDemoNotification(phoneNumber, otp, userType);

        return {
          success: true,
          message: `OTP sent to ${phoneNumber}`,
          messageId: `demo-${Date.now()}`,
          otp: otp // Only in demo mode
        };
      } else {
        // Production mode - integrate with real SMS provider
        return await this.sendRealSMS(phoneNumber, otp, userType);
      }
    } catch (error) {
      console.error('SMS Service Error:', error);
      throw new Error('Failed to send OTP. Please try again.');
    }
  }

  // Show demo notification
  showDemoNotification(phoneNumber, otp, userType) {
    const message = `SMS Demo Mode Active\n\nPhone: ${phoneNumber}\nOTP: ${otp}\nType: ${userType.toUpperCase()}\n\nUse this OTP in the app!`;

    // Create a temporary notification
    const notification = document.createElement('div');
    notification.style.cssText = `
      position: fixed;
      top: 20px;
      left: 50%;
      transform: translateX(-50%);
      background: #1e293b;
      color: white;
      padding: 15px 20px;
      border-radius: 8px;
      z-index: 10000;
      font-family: monospace;
      font-size: 14px;
      white-space: pre-line;
      box-shadow: 0 4px 12px rgba(0,0,0,0.3);
      border: 2px solid #10b981;
    `;
    notification.textContent = message;

    document.body.appendChild(notification);

    // Auto-remove after 10 seconds
    setTimeout(() => {
      if (notification.parentNode) {
        document.body.removeChild(notification);
      }
    }, 10000);
  }

  // Send real SMS (Twilio, AWS SNS, etc.)
  async sendRealSMS(phoneNumber, otp, userType) {
    // Example Twilio integration
    const accountSid = process.env.NEXT_PUBLIC_TWILIO_ACCOUNT_SID;
    const authToken = process.env.NEXT_PUBLIC_TWILIO_AUTH_TOKEN;
    const fromNumber = process.env.NEXT_PUBLIC_TWILIO_PHONE_NUMBER;

    if (!accountSid || !authToken || !fromNumber) {
      throw new Error('SMS service not configured properly');
    }

    const message = `Your EA Trading ${userType.toUpperCase()} login OTP is: ${otp}. Valid for 5 minutes. Do not share this code.`;

    try {
      const response = await fetch(`https://api.twilio.com/2010-04-01/Accounts/${accountSid}/Messages.json`, {
        method: 'POST',
        headers: {
          'Authorization': 'Basic ' + btoa(accountSid + ':' + authToken),
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
          To: phoneNumber,
          From: fromNumber,
          Body: message
        })
      });

      const data = await response.json();

      if (response.ok) {
        return {
          success: true,
          message: `OTP sent to ${phoneNumber}`,
          messageId: data.sid
        };
      } else {
        throw new Error(data.message || 'Failed to send SMS');
      }
    } catch (error) {
      console.error('Real SMS Error:', error);
      throw error;
    }
  }

  // Verify OTP
  async verifyOTP(phoneNumber, enteredOTP, userType = 'user') {
    try {
      const storedData = this.otpStore.get(phoneNumber);

      if (!storedData) {
        throw new Error('OTP not found or expired. Please request a new OTP.');
      }

      // Check if OTP is expired
      if (Date.now() > storedData.expiryTime) {
        this.otpStore.delete(phoneNumber);
        throw new Error('OTP has expired. Please request a new OTP.');
      }

      // Check if max attempts exceeded
      if (storedData.attempts >= storedData.maxAttempts) {
        this.otpStore.delete(phoneNumber);
        throw new Error('Maximum verification attempts exceeded. Please request a new OTP.');
      }

      // Increment attempt count
      storedData.attempts++;

      // Verify OTP
      if (storedData.otp === enteredOTP && storedData.userType === userType) {
        // Success - remove OTP from store
        this.otpStore.delete(phoneNumber);

        console.log(`✅ OTP Verified successfully for ${phoneNumber} (${userType})`);

        return {
          success: true,
          message: 'OTP verified successfully',
          userType: storedData.userType
        };
      } else {
        // Wrong OTP
        const attemptsLeft = storedData.maxAttempts - storedData.attempts;
        const errorMessage = attemptsLeft > 0
          ? `Invalid OTP. ${attemptsLeft} attempts remaining.`
          : 'Invalid OTP. Maximum attempts exceeded.';

        if (attemptsLeft === 0) {
          this.otpStore.delete(phoneNumber);
        }

        throw new Error(errorMessage);
      }
    } catch (error) {
      console.error('OTP Verification Error:', error);
      throw error;
    }
  }

  // Resend OTP
  async resendOTP(phoneNumber, userType = 'user') {
    try {
      // Delete existing OTP
      this.otpStore.delete(phoneNumber);

      // Send new OTP
      return await this.sendOTP(phoneNumber, userType);
    } catch (error) {
      console.error('Resend OTP Error:', error);
      throw error;
    }
  }

  // Get demo OTP for testing (only in demo mode)
  getDemoOTP(phoneNumber) {
    if (!this.isDemoMode) {
      return null;
    }

    const storedData = this.otpStore.get(phoneNumber);
    return storedData ? storedData.otp : null;
  }

  // Clean up expired OTPs (call periodically)
  cleanupExpiredOTPs() {
    const now = Date.now();
    for (const [phoneNumber, data] of this.otpStore.entries()) {
      if (now > data.expiryTime) {
        this.otpStore.delete(phoneNumber);
      }
    }
  }

  // Get service status
  getServiceStatus() {
    return {
      isDemo: this.isDemoMode,
      activeOTPs: this.otpStore.size,
      provider: this.isDemoMode ? 'Demo Mode' : 'Production SMS'
    };
  }
}

// Export singleton instance
export const smsService = new SMSService();

// Clean up expired OTPs every 5 minutes
if (typeof window !== 'undefined') {
  setInterval(() => {
    smsService.cleanupExpiredOTPs();
  }, 5 * 60 * 1000);
}

export default smsService;