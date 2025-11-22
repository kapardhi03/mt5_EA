"use client";
import React, { useState } from 'react';
import API_BASE_URL from '@/config/api';

interface TempUserManagerProps {
  onClose: () => void;
}

export default function TempUserManager({ onClose }: TempUserManagerProps) {
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  const activateUser = async () => {
    if (!email.trim()) {
      setMessage('Please enter an email address');
      return;
    }

    setLoading(true);
    setMessage('');

    try {
      const token = localStorage.getItem('authToken');
      if (!token) {
        setMessage('❌ Authentication token not found. Please login as admin first.');
        setLoading(false);
        return;
      }

  const response = await fetch(`${API_BASE_URL}/api/v1/admin-simple/activate-user`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({ email: email.trim() })
      });

      const result = await response.json();

      if (result.success) {
        setMessage(`✅ User ${email} has been activated successfully!`);
        setEmail('');
      } else {
        setMessage(`❌ Error: ${result.message || result.detail || 'Failed to activate user'}`);
      }
    } catch (error) {
      setMessage('❌ Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const updateUserRole = async (role: string) => {
    if (!email.trim()) {
      setMessage('Please enter an email address');
      return;
    }

    setLoading(true);
    setMessage('');

    try {
      const token = localStorage.getItem('authToken');
      if (!token) {
        setMessage('❌ Authentication token not found. Please login as admin first.');
        setLoading(false);
        return;
      }

  const response = await fetch(`${API_BASE_URL}/api/v1/admin-simple/update-user-role`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          email: email.trim(),
          role: role
        })
      });

      const result = await response.json();

      if (result.success) {
        setMessage(`✅ User ${email} role updated to ${role} successfully!`);
        setEmail('');
      } else {
        setMessage(`❌ Error: ${result.message || result.detail || 'Failed to update user role'}`);
      }
    } catch (error) {
      setMessage('❌ Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      background: 'rgba(0,0,0,0.5)',
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      zIndex: 1000
    }}>
      <div style={{
        background: 'white',
        padding: '30px',
        borderRadius: '12px',
        width: '90%',
        maxWidth: '500px',
        boxShadow: '0 4px 20px rgba(0,0,0,0.1)'
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
          <h2 style={{ margin: 0, color: '#1f2937' }}>👥 User Management</h2>
          <button
            onClick={onClose}
            style={{
              background: 'none',
              border: 'none',
              fontSize: '24px',
              cursor: 'pointer',
              color: '#6b7280'
            }}
          >
            ×
          </button>
        </div>

        <div className="form-group" style={{ marginBottom: '20px' }}>
          <label style={{ display: 'block', marginBottom: '8px', fontWeight: '500' }}>
            User Email
          </label>
          <input
            type="email"
            placeholder="Enter user email address"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            style={{
              width: '100%',
              padding: '12px',
              border: '2px solid #e5e7eb',
              borderRadius: '8px',
              fontSize: '14px'
            }}
          />
        </div>

        {message && (
          <div style={{
            padding: '12px',
            marginBottom: '20px',
            borderRadius: '8px',
            backgroundColor: message.includes('✅') ? '#f0f9ff' : '#fef2f2',
            color: message.includes('✅') ? '#1e40af' : '#dc2626',
            fontSize: '14px'
          }}>
            {message}
          </div>
        )}

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px', marginBottom: '20px' }}>
          <button
            onClick={activateUser}
            disabled={loading}
            className="btn btn-primary"
            style={{
              padding: '12px',
              backgroundColor: loading ? '#9ca3af' : '#10b981',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              cursor: loading ? 'not-allowed' : 'pointer'
            }}
          >
            {loading ? 'Processing...' : '✅ Activate User'}
          </button>

          <button
            onClick={() => updateUserRole('admin')}
            disabled={loading}
            className="btn btn-secondary"
            style={{
              padding: '12px',
              backgroundColor: loading ? '#9ca3af' : '#6b7280',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              cursor: loading ? 'not-allowed' : 'pointer'
            }}
          >
            {loading ? 'Processing...' : '🔑 Make Admin'}
          </button>
        </div>

        <div style={{ fontSize: '12px', color: '#6b7280', lineHeight: '1.5' }}>
          <strong>Instructions:</strong><br/>
          1. Enter the email address of the user you want to manage<br/>
          2. Click "Activate User" to change status from pending to active<br/>
          3. Click "Make Admin" to give user admin privileges<br/>
          <br/>
          <strong>Note:</strong> This is a temporary solution while the main admin panel is being fixed.
        </div>
      </div>
    </div>
  );
}