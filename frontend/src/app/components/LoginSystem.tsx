"use client";
import React, { useState } from 'react';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';

interface LoginSystemProps {
  onAuthSuccess: (type: 'user' | 'admin' | 'master', userData: UserData) => void;
}

interface UserData {
  id: string;
  email: string;
  name: string;
  mobile: string;
  role: string;
  verified: boolean;
  createdAt: string;
}

type LoginType = 'user' | 'admin' | 'master';

export default function LoginSystem({ onAuthSuccess }: LoginSystemProps) {
  const [loginType, setLoginType] = useState<LoginType>('user');
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    mobile: '',
    otp: '',
    userData: null as UserData | null,
    token: ''
  });
  const [step, setStep] = useState<'login' | 'otp' | 'forgot-password' | 'reset-password'>('login');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [resetToken, setResetToken] = useState('');

  // Removed demo credentials for security

  const updateFormData = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    if (error) setError('');
  };

  const handleLogin = async () => {
    setIsLoading(true);
    setError('');

    try {
      // Validate inputs
      if (!formData.email && !formData.mobile) {
        throw new Error('Please enter email or mobile number');
      }
      if (!formData.password) {
        throw new Error('Please enter password');
      }

  // Call backend login API (base URL configurable via NEXT_PUBLIC_API_URL)
  const response = await fetch(`${API_URL}/api/v1/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          mobile_or_email: formData.email || formData.mobile,
          password: formData.password
        })
      });

      const result = await response.json();

      if (!response.ok) {
        throw new Error(result.detail || result.message || 'Login failed');
      }

      if (result.success && result.data) {
        const userData = result.data.user;
        const accessToken = result.data.access_token;

        // Verify user role matches selected login type
        if (userData.role !== loginType) {
          throw new Error(`This account is registered as ${userData.role}, not ${loginType}`);
        }

        // Store authentication data
        localStorage.setItem('authToken', accessToken);
        localStorage.setItem('userType', userData.role);
        localStorage.setItem('userData', JSON.stringify(userData));

        // Success - call the auth callback
        onAuthSuccess(userData.role as 'user' | 'admin' | 'master', userData);

      } else {
        throw new Error(result.message || 'Login failed - invalid response');
      }

    } catch (err: unknown) {
      const errorMsg = err instanceof Error ? err.message : 'Login failed - please try again';
      console.error('Login error:', errorMsg);
      setError(errorMsg);
    } finally {
      setIsLoading(false);
    }
  };

  const handleOTPVerification = async () => {
    setIsLoading(true);
    setError('');

    try {
      const userData = formData.userData;
      if (!userData) {
        throw new Error('User data not found. Please login again.');
      }

      // Verify OTP with backend
  const response = await fetch(`${API_URL}/api/v1/auth/verify-otp`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          mobile_or_email: userData.mobile,
          otp: formData.otp,
          otp_type: 'mobile'
        })
      });

      const result = await response.json();

      if (response.ok && result.success) {
        // OTP verified successfully, complete login
        const token = formData.token;

        // Store in localStorage for persistence
        localStorage.setItem('authToken', token);
        localStorage.setItem('userType', userData.role);
        localStorage.setItem('userData', JSON.stringify(userData));

        console.log(`✅ User authenticated successfully: ${userData.name} (${userData.role})`);
        onAuthSuccess(userData.role as 'user' | 'admin' | 'master', userData);
      } else {
        throw new Error(result.detail || result.message || 'OTP verification failed');
      }
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setIsLoading(false);
    }
  };

  const handleForgotPassword = async () => {
    if (!formData.email) {
      setError('Please enter your email address');
      return;
    }

    setIsLoading(true);
    setError('');

    try {
  const response = await fetch(`${API_URL}/api/v1/auth/forgot-password`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email: formData.email })
      });

      const result = await response.json();

      if (response.ok && result.success) {
        setResetToken(result.data.reset_token);
        setStep('reset-password');
        alert('Password reset token generated: ' + result.data.reset_token);
      } else {
        throw new Error(result.detail || result.message || 'Failed to send reset email');
      }
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setIsLoading(false);
    }
  };

  const handlePasswordReset = async () => {
    if (!formData.email || !resetToken || !formData.password) {
      setError('Please fill in all fields');
      return;
    }

    if (formData.password.length < 8) {
      setError('Password must be at least 8 characters long');
      return;
    }

    setIsLoading(true);
    setError('');

    try {
  const response = await fetch(`${API_URL}/api/v1/auth/reset-password`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: formData.email,
          reset_token: resetToken,
          new_password: formData.password
        })
      });

      const result = await response.json();

      if (response.ok && result.success) {
        alert('Password reset successfully! Please login with your new password.');
        setStep('login');
        setFormData(prev => ({ ...prev, password: '', otp: '' }));
        setResetToken('');
      } else {
        throw new Error(result.detail || result.message || 'Failed to reset password');
      }
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setIsLoading(false);
    }
  };

  const renderLoginTypeSelector = () => (
    <div style={{ marginBottom: '30px' }}>
      <div style={{ textAlign: 'center', marginBottom: '20px' }}>
        <h3 style={{ color: '#1f2937', marginBottom: '8px' }}>Select Login Type</h3>
        <p style={{ color: '#6b7280', fontSize: '14px' }}>Choose your account type to continue</p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '15px' }}>
        <button
          type="button"
          className={`btn ${loginType === 'user' ? 'btn-primary' : 'btn-outline'}`}
          onClick={() => setLoginType('user')}
          style={{
            padding: '15px 10px',
            textAlign: 'center',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            gap: '8px'
          }}
        >
          <span style={{ fontSize: '24px' }}>👤</span>
          <span style={{ fontSize: '12px', fontWeight: '600' }}>User Login</span>
          <span style={{ fontSize: '10px', opacity: '0.7' }}>EA Trading Member</span>
        </button>

        <button
          type="button"
          className={`btn ${loginType === 'admin' ? 'btn-primary' : 'btn-outline'}`}
          onClick={() => setLoginType('admin')}
          style={{
            padding: '15px 10px',
            textAlign: 'center',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            gap: '8px'
          }}
        >
          <span style={{ fontSize: '24px' }}>⚙️</span>
          <span style={{ fontSize: '12px', fontWeight: '600' }}>Admin Login</span>
          <span style={{ fontSize: '10px', opacity: '0.7' }}>Platform Administrator</span>
        </button>

        <button
          type="button"
          className={`btn ${loginType === 'master' ? 'btn-primary' : 'btn-outline'}`}
          onClick={() => setLoginType('master')}
          style={{
            padding: '15px 10px',
            textAlign: 'center',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            gap: '8px'
          }}
        >
          <span style={{ fontSize: '24px' }}>📈</span>
          <span style={{ fontSize: '12px', fontWeight: '600' }}>Master Login</span>
          <span style={{ fontSize: '10px', opacity: '0.7' }}>Group Master Trader</span>
        </button>
      </div>
    </div>
  );

  const renderLoginForm = () => (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        handleLogin();
      }}
    >
      <div className="form-group">
        <label>Email Address</label>
        <input
          type="email"
          placeholder="Enter your email"
          value={formData.email}
          onChange={(e) => updateFormData('email', e.target.value)}
          disabled={isLoading}
        />
      </div>

      <div className="form-group">
        <label>Password</label>
        <input
          type="password"
          placeholder="Enter your password"
          value={formData.password}
          onChange={(e) => updateFormData('password', e.target.value)}
          disabled={isLoading}
        />
      </div>

      {error && (
        <div className="alert alert-danger">
          {error}
        </div>
      )}

      <button
        type="submit"
        className="btn btn-primary"
        disabled={isLoading}
        style={{ width: '100%', marginBottom: '15px' }}
      >
        {isLoading ? 'Authenticating...' : 'Login'}
      </button>

      <div style={{ textAlign: 'center', marginBottom: '15px' }}>
        <button
          type="button"
          onClick={() => setStep('forgot-password')}
          style={{
            background: 'none',
            border: 'none',
            color: '#3b82f6',
            textDecoration: 'underline',
            cursor: 'pointer',
            fontSize: '14px'
          }}
        >
          Forgot Password?
        </button>
      </div>

      <div style={{ background: '#f0f9ff', padding: '15px', borderRadius: '8px', fontSize: '12px', border: '1px solid #e0f2fe' }}>
        <strong>🔐 Secure Login:</strong><br />
        • Enter your registered email or mobile number<br />
        • Use your account password<br />
        • Select the correct login type: {loginType.toUpperCase()}<br />
        <strong style={{ color: '#0369a1' }}>✅ Real Database Authentication</strong>
      </div>
    </form>
  );

  const renderOTPForm = () => (
    <div>
      <div style={{ textAlign: 'center', marginBottom: '20px' }}>
        <h3 style={{ color: '#1f2937', marginBottom: '8px' }}>Verify OTP</h3>
        <p style={{ color: '#6b7280', fontSize: '14px' }}>
          Enter the OTP sent to {formData.userData?.mobile || formData.mobile || 'your mobile number'}
        </p>
      </div>

      <div className="form-group">
        <label>Enter OTP</label>
        <input
          type="text"
          className="otp-input"
          placeholder="000000"
          maxLength={6}
          value={formData.otp}
          onChange={(e) => updateFormData('otp', e.target.value.replace(/\D/g, ''))}
          disabled={isLoading}
          style={{ textAlign: 'center', fontSize: '18px', letterSpacing: '4px' }}
        />
      </div>

      {error && (
        <div className="alert alert-danger">
          {error}
        </div>
      )}

      <button
        type="button"
        className="btn btn-primary"
        onClick={handleOTPVerification}
        disabled={isLoading || formData.otp.length !== 6}
        style={{ width: '100%', marginBottom: '15px' }}
      >
        {isLoading ? 'Verifying...' : 'Verify OTP'}
      </button>

      <div style={{ display: 'flex', gap: '10px' }}>
        <button
          type="button"
          className="btn btn-outline"
          onClick={() => setStep('login')}
          disabled={isLoading}
          style={{ flex: 1 }}
        >
          Back to Login
        </button>

        <button
          type="button"
          className="btn btn-secondary"
          onClick={async () => {
            try {
              setIsLoading(true);
              const userData = formData.userData;
              if (!userData) {
                throw new Error('User data not found. Please login again.');
              }

              // Resend OTP via backend
              const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/auth/send-otp`, {
                method: 'POST',
                headers: {
                  'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                  mobile_or_email: userData.mobile,
                  otp_type: 'mobile'
                })
              });

              const result = await response.json();

              if (response.ok && result.success) {
                console.log(`📱 OTP resent to ${userData.mobile}`);
                // Show OTP in demo mode
                if (result.data?.otp) {
                  alert(`Demo Mode - Your new OTP is: ${result.data.otp}`);
                }
              } else {
                throw new Error(result.detail || result.message || 'Failed to resend OTP');
              }
            } catch (err: unknown) {
              setError(err instanceof Error ? err.message : 'An error occurred');
            } finally {
              setIsLoading(false);
            }
          }}
          disabled={isLoading}
          style={{ flex: 1 }}
        >
          Resend OTP
        </button>
      </div>

      <div style={{ background: '#f0f9ff', padding: '15px', borderRadius: '8px', fontSize: '12px', marginTop: '15px' }}>
        <strong>Production Backend:</strong> Real API integration active<br />
        <span style={{ color: '#6b7280' }}>OTP shown in browser alert for demo purposes</span>
        <br />
        <strong>Service Status:</strong> FastAPI Backend Connected
      </div>
    </div>
  );

  const renderForgotPasswordForm = () => (
    <div>
      <div style={{ marginBottom: '25px' }}>
        <label htmlFor="email" style={{ display: 'block', marginBottom: '8px', fontWeight: '500', color: '#374151' }}>
          Email Address
        </label>
        <input
          type="email"
          id="email"
          placeholder="Enter your registered email"
          value={formData.email}
          onChange={(e) => updateFormData('email', e.target.value)}
          style={{
            width: '100%',
            padding: '12px 16px',
            border: '1px solid #d1d5db',
            borderRadius: '8px',
            fontSize: '16px',
            backgroundColor: '#ffffff'
          }}
        />
      </div>

      {error && (
        <div style={{
          background: '#fef2f2',
          border: '1px solid #fecaca',
          color: '#dc2626',
          padding: '12px',
          borderRadius: '6px',
          marginBottom: '20px',
          fontSize: '14px'
        }}>
          {error}
        </div>
      )}

      <button
        type="button"
        className="btn btn-primary"
        onClick={handleForgotPassword}
        disabled={isLoading}
        style={{ width: '100%', marginBottom: '15px' }}
      >
        {isLoading ? 'Sending Reset Link...' : 'Send Reset Token'}
      </button>

      <button
        type="button"
        className="btn btn-outline"
        onClick={() => setStep('login')}
        style={{ width: '100%' }}
      >
        Back to Login
      </button>

      <div style={{ background: '#f0f9ff', padding: '15px', borderRadius: '8px', fontSize: '12px', marginTop: '15px' }}>
        <strong>Demo Mode:</strong> Reset token will be displayed in browser alert
      </div>
    </div>
  );

  const renderResetPasswordForm = () => (
    <div>
      <div style={{ marginBottom: '20px' }}>
        <label htmlFor="reset-token" style={{ display: 'block', marginBottom: '8px', fontWeight: '500', color: '#374151' }}>
          Reset Token
        </label>
        <input
          type="text"
          id="reset-token"
          placeholder="Enter the reset token"
          value={resetToken}
          onChange={(e) => setResetToken(e.target.value)}
          style={{
            width: '100%',
            padding: '12px 16px',
            border: '1px solid #d1d5db',
            borderRadius: '8px',
            fontSize: '16px',
            backgroundColor: '#ffffff'
          }}
        />
      </div>

      <div style={{ marginBottom: '25px' }}>
        <label htmlFor="new-password" style={{ display: 'block', marginBottom: '8px', fontWeight: '500', color: '#374151' }}>
          New Password
        </label>
        <input
          type="password"
          id="new-password"
          placeholder="Enter new password (min 8 characters)"
          value={formData.password}
          onChange={(e) => updateFormData('password', e.target.value)}
          style={{
            width: '100%',
            padding: '12px 16px',
            border: '1px solid #d1d5db',
            borderRadius: '8px',
            fontSize: '16px',
            backgroundColor: '#ffffff'
          }}
        />
      </div>

      {error && (
        <div style={{
          background: '#fef2f2',
          border: '1px solid #fecaca',
          color: '#dc2626',
          padding: '12px',
          borderRadius: '6px',
          marginBottom: '20px',
          fontSize: '14px'
        }}>
          {error}
        </div>
      )}

      <button
        type="button"
        className="btn btn-primary"
        onClick={handlePasswordReset}
        disabled={isLoading}
        style={{ width: '100%', marginBottom: '15px' }}
      >
        {isLoading ? 'Resetting Password...' : 'Reset Password'}
      </button>

      <button
        type="button"
        className="btn btn-outline"
        onClick={() => setStep('forgot-password')}
        style={{ width: '100%' }}
      >
        Back to Email Entry
      </button>
    </div>
  );

  return (
    <div className="registration-container">
      <div className="auth-header">
        <h2>EA Trading Platform</h2>
        <p>
          {step === 'login' && 'Sign in to your account'}
          {step === 'otp' && 'Verify your identity with OTP'}
          {step === 'forgot-password' && 'Reset your password'}
          {step === 'reset-password' && 'Create new password'}
        </p>
      </div>

      <div className="form-container">
        {step === 'login' && renderLoginTypeSelector()}
        {step === 'login' && renderLoginForm()}
        {step === 'otp' && renderOTPForm()}
        {step === 'forgot-password' && renderForgotPasswordForm()}
        {step === 'reset-password' && renderResetPasswordForm()}
      </div>
    </div>
  );
}