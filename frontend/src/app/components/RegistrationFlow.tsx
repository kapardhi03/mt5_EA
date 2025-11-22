"use client";
import React, { useState } from 'react';

interface RegistrationFlowProps {
  onAuthSuccess: () => void;
}

type Step = 'registration' | 'otp' | 'ib-requirement' | 'review';

export default function RegistrationFlow({ onAuthSuccess }: RegistrationFlowProps) {
  const [currentStep, setCurrentStep] = useState<Step>('registration');
  const [formData, setFormData] = useState({
    fullName: '',
    mobile: '',
    email: '',
    country: '',
    state: '',
    city: '',
    zipCode: '',
    password: '',
    mobileOtp: '',
    emailOtp: '',
    broker: '',
    accountNumber: '',
    tradingPassword: '',
    referralCode: '',
    ibProofImage: null as File | null
  });
  const [errors, setErrors] = useState<{[key: string]: string}>({});
  const [loading, setLoading] = useState(false);
  const [otpSent, setOtpSent] = useState(false);
  const [otpVerified, setOtpVerified] = useState(false);
  // store API responses for showing test OTPs in the UI
  const [mobileResult, setMobileResult] = useState<any | null>(null);
  const [emailResult, setEmailResult] = useState<any | null>(null);

  const updateFormData = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      // Validate file type
      if (!file.type.startsWith('image/')) {
        setErrors({ ibProofImage: 'Please select a valid image file' });
        return;
      }
      
      // Validate file size (max 5MB)
      if (file.size > 5 * 1024 * 1024) {
        setErrors({ ibProofImage: 'File size must be less than 5MB' });
        return;
      }
      
      setFormData(prev => ({ ...prev, ibProofImage: file }));
      setErrors(prev => ({ ...prev, ibProofImage: '' }));
    }
  };

  const convertFileToBase64 = (file: File): Promise<string> => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.readAsDataURL(file);
      reader.onload = () => {
        const result = reader.result as string;
        // Remove the data:image/...;base64, prefix
        const base64 = result.split(',')[1];
        resolve(base64);
      };
      reader.onerror = error => reject(error);
    });
  };

  const validateRegistrationFields = () => {
    const newErrors: {[key: string]: string} = {};

    if (!formData.fullName.trim()) newErrors.fullName = 'Full name is required';
    if (!formData.mobile.trim()) newErrors.mobile = 'Mobile number is required';
    if (!formData.email.trim()) newErrors.email = 'Email is required';
    if (!formData.country.trim()) newErrors.country = 'Country is required';
    if (!formData.state.trim()) newErrors.state = 'State is required';
    if (!formData.city.trim()) newErrors.city = 'City is required';
    if (!formData.zipCode.trim()) newErrors.zipCode = 'ZIP/PIN code is required';
    if (!formData.password || formData.password.length < 8) newErrors.password = 'Password must be at least 8 characters';
    if (!formData.broker) newErrors.broker = 'Broker selection is required';
    if (!formData.accountNumber.trim()) newErrors.accountNumber = 'Trading account number is required';
    if (!formData.tradingPassword.trim()) newErrors.tradingPassword = 'Trading password is required';

    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = 'Please enter a valid email address';
    }

    if (!/^\+?[1-9]\d{1,14}$/.test(formData.mobile.replace(/\s/g, ''))) {
      newErrors.mobile = 'Please enter a valid mobile number';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const validateOtpFields = () => {
    const newErrors: {[key: string]: string} = {};

    if (!formData.mobileOtp || formData.mobileOtp.length !== 6) {
      newErrors.mobileOtp = 'Please enter 6-digit mobile OTP';
    }
    if (!formData.emailOtp || formData.emailOtp.length !== 6) {
      newErrors.emailOtp = 'Please enter 6-digit email OTP';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const sendOtpCodes = async () => {
    if (!validateRegistrationFields()) {
      return;
    }

    setLoading(true);
    try {
      // Send mobile OTP
      const mobileResponse = await fetch('http://localhost:8000/api/v1/auth/send-otp', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          mobile_or_email: formData.mobile,
          otp_type: 'mobile'
        })
      });

  const mobileResult = await mobileResponse.json();
  setMobileResult(mobileResult);

      // Send email OTP
      const emailResponse = await fetch('http://localhost:8000/api/v1/auth/send-otp', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          mobile_or_email: formData.email,
          otp_type: 'email'
        })
      });

  const emailResult = await emailResponse.json();
  setEmailResult(emailResult);

      if (mobileResult.success && emailResult.success) {
        setOtpSent(true);
        setCurrentStep('otp');
      } else {
        const errors = [];
        if (!mobileResult.success) errors.push(`Mobile OTP: ${mobileResult.detail || mobileResult.message}`);
        if (!emailResult.success) errors.push(`Email OTP: ${emailResult.detail || emailResult.message}`);
        setErrors({ general: errors.join('. ') });
      }
    } catch (error) {
      setErrors({ general: 'Network error. Please try again.' });
    } finally {
      setLoading(false);
    }
  };

  const verifyOtpCodes = async () => {
    if (!validateOtpFields()) {
      return;
    }

    setLoading(true);
    try {
      // Verify mobile OTP
      const mobileResponse = await fetch('http://localhost:8000/api/v1/auth/verify-otp', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          mobile_or_email: formData.mobile,
          otp: formData.mobileOtp,
          otp_type: 'mobile'
        })
      });

  const mobileResult = await mobileResponse.json();
  setMobileResult(mobileResult);

      // Verify email OTP
      const emailResponse = await fetch('http://localhost:8000/api/v1/auth/verify-otp', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          mobile_or_email: formData.email,
          otp: formData.emailOtp,
          otp_type: 'email'
        })
      });

  const emailResult = await emailResponse.json();
  setEmailResult(emailResult);

      if (mobileResult.success && emailResult.success) {
        setOtpVerified(true);
        setCurrentStep('ib-requirement');
      } else {
        const errors = [];
        if (!mobileResult.success) errors.push(`Mobile OTP: ${mobileResult.detail || mobileResult.message}`);
        if (!emailResult.success) errors.push(`Email OTP: ${emailResult.detail || emailResult.message}`);
        setErrors({ general: errors.join('. ') });
      }
    } catch (error) {
      setErrors({ general: 'Network error. Please try again.' });
    } finally {
      setLoading(false);
    }
  };

  const submitRegistration = async () => {
    if (!otpVerified) {
      setErrors({ general: 'OTP verification is required before proceeding' });
      return;
    }

    if (!formData.ibProofImage) {
      setErrors({ general: 'Please upload IB proof image before proceeding' });
      return;
    }

    setLoading(true);
    try {
      // First register the user
      const registerResponse = await fetch('http://localhost:8000/api/v1/auth/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: formData.fullName,
          email: formData.email,
          mobile: formData.mobile,
          password: formData.password,
          country: formData.country,
          state: formData.state,
          city: formData.city,
          pin_code: formData.zipCode,
          broker: formData.broker,
          account_no: formData.accountNumber,
          trading_password: formData.tradingPassword,
          referral_code: formData.referralCode || null
        })
      });

      let registerResult: any = null;
      try {
        registerResult = await registerResponse.json();
      } catch (e) {
        registerResult = null;
      }

      if (!registerResponse.ok) {
        // Show validation errors from server (FastAPI returns detail)
        const detail = registerResult?.detail || registerResult?.message || 'Registration failed';
        setErrors({ general: Array.isArray(detail) ? detail.map(d=>d.msg).join('. ') : String(detail) });
        setLoading(false);
        return;
      }

      if (registerResult.success) {
        // If registration successful, upload IB proof
        const base64Image = await convertFileToBase64(formData.ibProofImage);
        
        const ibResponse = await fetch('http://localhost:8000/api/v1/auth/upload-ib-proof', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${registerResult.data.access_token}`
          },
          body: JSON.stringify({
            proof_image: base64Image,
            proof_filename: formData.ibProofImage?.name || null,
            broker: formData.broker,
            account_number: formData.accountNumber,
            trading_password: formData.tradingPassword
          })
        });

        const ibResult = await ibResponse.json();

        if (ibResult.success) {
          // If IB approved immediately, show success and redirect to login
          if (ibResult.data && ibResult.data.ib_status === 'approved') {
            alert('Registration complete and IB approved. You can now login.');
            // reset form and redirect to login
            setFormData({
              fullName: '',
              mobile: '',
              email: '',
              country: '',
              state: '',
              city: '',
              zipCode: '',
              password: '',
              mobileOtp: '',
              emailOtp: '',
              broker: '',
              accountNumber: '',
              tradingPassword: '',
              referralCode: '',
              ibProofImage: null
            });
            onAuthSuccess();
            return;
          }

          setCurrentStep('review');
        } else {
          setErrors({ general: ibResult.message || 'IB proof upload failed' });
        }
      } else {
        setErrors({ general: registerResult.message || 'Registration failed' });
      }
    } catch (error) {
      setErrors({ general: 'Network error. Please try again.' });
    } finally {
      setLoading(false);
    }
  };

  const renderProgressSteps = () => {
    const steps: Step[] = ['registration', 'otp', 'ib-requirement', 'review'];
    const currentIndex = steps.indexOf(currentStep);

    return (
      <div className="progress-steps">
        <div className={`step ${currentIndex === 0 ? 'active' : (currentIndex > 0 ? 'completed' : '')}`}>
          <div className="step-circle">{currentIndex === 0 ? '1' : '✓'}</div>
          Personal Info
        </div>
        <div className="step-divider"></div>
        <div className={`step ${currentIndex === 1 ? 'active' : (currentIndex > 1 ? 'completed' : '')}`}>
          <div className="step-circle">{currentIndex === 1 ? '2' : (currentIndex > 1 ? '✓' : '2')}</div>
          Verification
        </div>
        <div className="step-divider"></div>
        <div className={`step ${currentIndex === 2 ? 'active' : (currentIndex > 2 ? 'completed' : '')}`}>
          <div className="step-circle">{currentIndex === 2 ? '3' : (currentIndex > 2 ? '✓' : '3')}</div>
          IB Setup
        </div>
      </div>
    );
  };

  const renderRegistrationStep = () => (
    <div className="registration-container">
      <div className="auth-header">
        <h2>Create Account</h2>
        <p>Join our EA trading platform</p>
      </div>

      {renderProgressSteps()}

      <div className="form-container">
        {errors.general && (
          <div className="alert alert-error" style={{ marginBottom: '20px' }}>
            {errors.general}
          </div>
        )}

        <div className="form-group">
          <label>Full Name *</label>
          <input
            type="text"
            placeholder="Enter your full name"
            value={formData.fullName ?? ''}
            onChange={(e) => updateFormData('fullName', e.target.value)}
            className={errors.fullName ? 'error' : ''}
          />
          {errors.fullName && <div className="error-text">{errors.fullName}</div>}
        </div>

        <div className="form-group">
          <label>Mobile Number *</label>
          <input
            type="tel"
            placeholder="Enter mobile number with country code (+1234567890)"
            value={formData.mobile ?? ''}
            onChange={(e) => updateFormData('mobile', e.target.value)}
            className={errors.mobile ? 'error' : ''}
          />
          {errors.mobile && <div className="error-text">{errors.mobile}</div>}
        </div>

        <div className="form-group">
          <label>Email Address *</label>
          <input
            type="email"
            placeholder="Enter email address"
            value={formData.email ?? ''}
            onChange={(e) => updateFormData('email', e.target.value)}
            className={errors.email ? 'error' : ''}
          />
          {errors.email && <div className="error-text">{errors.email}</div>}
        </div>

        <div className="form-group">
          <label>Country *</label>
          <select value={formData.country ?? ''} onChange={(e) => updateFormData('country', e.target.value)}>
            <option value="">Select your country</option>
            <option value="United States">United States</option>
            <option value="United Kingdom">United Kingdom</option>
            <option value="India">India</option>
            <option value="Canada">Canada</option>
            <option value="Australia">Australia</option>
            <option value="Germany">Germany</option>
            <option value="France">France</option>
            <option value="Singapore">Singapore</option>
            <option value="UAE">United Arab Emirates</option>
            <option value="Other">Other</option>
          </select>
          {errors.country && <div className="error-text">{errors.country}</div>}
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '15px' }}>
          <div className="form-group">
            <label>State *</label>
            <input
              type="text"
              placeholder="State"
              value={formData.state ?? ''}
              onChange={(e) => updateFormData('state', e.target.value)}
              className={errors.state ? 'error' : ''}
            />
            {errors.state && <div className="error-text">{errors.state}</div>}
          </div>
          <div className="form-group">
            <label>City *</label>
            <input
              type="text"
              placeholder="City"
              value={formData.city ?? ''}
              onChange={(e) => updateFormData('city', e.target.value)}
              className={errors.city ? 'error' : ''}
            />
            {errors.city && <div className="error-text">{errors.city}</div>}
          </div>
        </div>

        <div className="form-group">
          <label>ZIP/PIN Code *</label>
          <input
            type="text"
            placeholder="ZIP/PIN Code"
            value={formData.zipCode ?? ''}
            onChange={(e) => updateFormData('zipCode', e.target.value)}
            className={errors.zipCode ? 'error' : ''}
          />
          {errors.zipCode && <div className="error-text">{errors.zipCode}</div>}
        </div>

        <div className="form-group">
          <label>Password *</label>
          <input
            type="password"
            placeholder="Create a password (min 8 characters)"
            value={formData.password ?? ''}
            onChange={(e) => updateFormData('password', e.target.value)}
            className={errors.password ? 'error' : ''}
          />
          {errors.password && <div className="error-text">{errors.password}</div>}
        </div>

        <div className="form-group">
          <label>Broker *</label>
          <select value={formData.broker ?? ''} onChange={(e) => updateFormData('broker', e.target.value)} className={errors.broker ? 'error' : ''}>
            <option value="">Select Your Broker</option>
            <option value="Vantage">Vantage</option>
            <option value="Exness">Exness</option>
            <option value="XM">XM</option>
            <option value="IC Markets">IC Markets</option>
            <option value="Pepperstone">Pepperstone</option>
            <option value="FXCM">FXCM</option>
            <option value="IG">IG</option>
            <option value="Other">Other</option>
          </select>
          {errors.broker && <div className="error-text">{errors.broker}</div>}
        </div>

        <div className="form-group">
          <label>Trading Account Number *</label>
          <input
            type="text"
            placeholder="Enter your trading account number"
            value={formData.accountNumber ?? ''}
            onChange={(e) => updateFormData('accountNumber', e.target.value)}
            className={errors.accountNumber ? 'error' : ''}
          />
          {errors.accountNumber && <div className="error-text">{errors.accountNumber}</div>}
        </div>

        <div className="form-group">
          <label>Trading Password *</label>
          <input
            type="password"
            placeholder="Enter your trading account password"
            value={formData.tradingPassword ?? ''}
            onChange={(e) => updateFormData('tradingPassword', e.target.value)}
            className={errors.tradingPassword ? 'error' : ''}
          />
          {errors.tradingPassword && <div className="error-text">{errors.tradingPassword}</div>}
        </div>

        <div className="form-group">
          <label>Referral Code (Optional)</label>
          <input
            type="text"
            placeholder="Enter group referral code if you have one"
            value={formData.referralCode ?? ''}
            onChange={(e) => updateFormData('referralCode', e.target.value)}
          />
          <small style={{ color: '#6b7280', fontSize: '12px' }}>
            Leave empty if you don&apos;t have a referral code. You&apos;ll be able to join a group later.
          </small>
        </div>

        <button
          className="btn btn-primary"
          onClick={sendOtpCodes}
          disabled={loading}
        >
          {loading ? 'Sending...' : 'Send Verification Code'}
        </button>
      </div>
    </div>
  );

  const renderOtpStep = () => (
    <div className="registration-container">
      <div className="auth-header">
        <h2>Verify Your Account</h2>
        <p>Enter the verification codes sent to your mobile and email</p>
      </div>

      {renderProgressSteps()}

      <div className="form-container">

        {otpSent && (
          <div className="alert alert-info">
            OTP sent to {formData.mobile} and {formData.email}
            {mobileResult?.data?.otp && (
              <div style={{marginTop: '10px', padding: '10px', background: '#e0f2fe', borderRadius: '5px'}}>
                <strong>Mobile OTP (for testing):</strong> {mobileResult.data.otp}
              </div>
            )}
            {emailResult?.data?.otp && (
              <div style={{marginTop: '10px', padding: '10px', background: '#e8f5e8', borderRadius: '5px'}}>
                <strong>Email OTP (for testing):</strong> {emailResult.data.otp}
              </div>
            )}
          </div>
        )}

        {errors.general && (
          <div className="alert alert-error" style={{ marginBottom: '20px' }}>
            {errors.general}
          </div>
        )}

        <div className="form-group">
          <label>Mobile OTP *</label>
          <input
            type="text"
            className={`otp-input ${errors.mobileOtp ? 'error' : ''}`}
            placeholder="- - - - - -"
            maxLength={6}
            value={formData.mobileOtp ?? ''}
            onChange={(e) => updateFormData('mobileOtp', e.target.value.replace(/\D/g, ''))}
          />
          {errors.mobileOtp && <div className="error-text">{errors.mobileOtp}</div>}
        </div>

        <div className="form-group">
          <label>Email OTP *</label>
          <input
            type="text"
            className={`otp-input ${errors.emailOtp ? 'error' : ''}`}
            placeholder="- - - - - -"
            maxLength={6}
            value={formData.emailOtp ?? ''}
            onChange={(e) => updateFormData('emailOtp', e.target.value.replace(/\D/g, ''))}
          />
          {errors.emailOtp && <div className="error-text">{errors.emailOtp}</div>}
        </div>

        <button
          className="btn btn-primary"
          onClick={verifyOtpCodes}
          disabled={loading || !otpSent}
        >
          {loading ? 'Verifying...' : 'Verify & Continue'}
        </button>
        <button className="btn btn-secondary" onClick={sendOtpCodes} disabled={loading}>
          Resend OTP
        </button>
      </div>
    </div>
  );

  const renderIBRequirementStep = () => (
    <div className="registration-container">
      <div className="auth-header">
        <h2>IB Change Required</h2>
        <p>To use EA services, you must change your IB (Introducing Broker) number to ours</p>
      </div>

      {renderProgressSteps()}

      <div className="form-container">
        <div className="alert alert-warning">
          <strong>Important:</strong> EA features cannot be enabled until you change to our IB number and provide proof.
        </div>

        <div style={{ background: '#f8fafc', padding: '20px', borderRadius: '8px', margin: '20px 0' }}>
          <h4 style={{ marginBottom: '15px', color: '#1f2937' }}>How to Change Your IB Number</h4>

          <div style={{ marginBottom: '15px' }}>
            <button
              className="btn btn-outline"
              style={{ marginBottom: '10px' }}
              onClick={() => alert('Demo: This would show step-by-step images for changing IB')}
            >
              📸 Show Steps with Images
            </button>
          </div>

          <div style={{ fontSize: '14px', lineHeight: '1.6' }}>
            <p><strong>Our IB Number:</strong> <span style={{ color: '#dc2626', fontWeight: 'bold' }}>IB123456789</span></p>
            <p><strong>Steps:</strong></p>
            <ol style={{ paddingLeft: '20px' }}>
              <li>Log into your {formData.broker} client portal</li>
              <li>Navigate to Account Settings → IB Settings</li>
              <li>Change IB number to: <strong>IB123456789</strong></li>
              <li>Save changes and take a screenshot</li>
              <li>Upload the screenshot as proof below</li>
            </ol>
          </div>
        </div>

        <div className="form-group">
          <label>Upload IB Change Proof *</label>
          <input
            type="file"
            accept="image/*"
            onChange={handleFileUpload}
            style={{
              width: '100%',
              padding: '12px',
              border: '2px dashed #d1d5db',
              borderRadius: '8px',
              textAlign: 'center'
            }}
          />
          {formData.ibProofImage && (
            <div style={{ marginTop: '10px', padding: '10px', background: '#f0f9ff', borderRadius: '8px' }}>
              <p style={{ margin: 0, color: '#0369a1' }}>
                ✓ Selected: {formData.ibProofImage.name} ({(formData.ibProofImage.size / 1024 / 1024).toFixed(2)} MB)
              </p>
            </div>
          )}
          {errors.ibProofImage && <div className="error-text">{errors.ibProofImage}</div>}
          <small style={{ color: '#6b7280', fontSize: '12px' }}>
            Upload a screenshot showing your IB number has been changed to ours (Max 5MB)
          </small>
        </div>

        <div className="alert alert-info">
          <strong>Status:</strong> Pending IB change proof. EA features will be enabled after admin approval.
        </div>

        <button
          className="btn btn-primary"
          onClick={submitRegistration}
          disabled={loading || !otpVerified}
        >
          {loading ? 'Submitting...' : 'Submit for Review'}
        </button>

        {!otpVerified && (
          <div className="alert alert-warning" style={{ marginTop: '10px' }}>
            OTP verification must be completed before proceeding
          </div>
        )}
      </div>
    </div>
  );

  const renderReviewStep = () => (
    <div className="registration-container">
      <div className="auth-header">
        <h2>Account Under Review</h2>
        <p>Your account is being verified by our team</p>
      </div>

      <div className="form-container" style={{ textAlign: 'center' }}>
        <div style={{ fontSize: '48px', marginBottom: '20px' }}>⏳</div>

        <div className="alert alert-warning">
          <strong>IB proof is under review.</strong> Approval may take up to 24 hours. EA features will be enabled after approval.
        </div>

        <div style={{ background: '#f8fafc', padding: '20px', borderRadius: '8px', margin: '20px 0' }}>
          <h4 style={{ marginBottom: '10px' }}>Registration Details:</h4>
          <p><strong>Broker:</strong> {formData.broker}</p>
          <p><strong>Account:</strong> {formData.accountNumber}</p>
          <p><strong>IB Status:</strong> Pending Review</p>
          <p><strong>Submitted:</strong> Just now</p>
        </div>

        <p style={{ marginBottom: '20px', color: '#6b7280' }}>
          For support, contact: <a href="#" style={{ color: '#10b981' }}>@EATradingSupport</a>
        </p>

        <button className="btn btn-primary" onClick={() => onAuthSuccess()}>
          Continue to Login
        </button>
      </div>
    </div>
  );

  const renderCurrentStep = () => {
    switch (currentStep) {
      case 'registration':
        return renderRegistrationStep();
      case 'otp':
        return renderOtpStep();
      case 'ib-requirement':
        return renderIBRequirementStep();
      case 'review':
        return renderReviewStep();
      default:
        return renderRegistrationStep();
    }
  };

  return renderCurrentStep();
}