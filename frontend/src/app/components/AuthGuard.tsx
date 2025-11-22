"use client";
import React, { useEffect, useState } from 'react';
import API_BASE_URL from '@/config/api';

interface AuthGuardProps {
  children: React.ReactNode;
  requiredRole: 'user' | 'admin' | 'master' | 'group_manager';
  onUnauthorized: () => void;
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

export default function AuthGuard({ children, requiredRole, onUnauthorized }: AuthGuardProps) {
  const [isAuthorized, setIsAuthorized] = useState<boolean | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const validateAccess = async () => {
      setIsLoading(true);

      try {
        const token = localStorage.getItem('authToken');
        const userType = localStorage.getItem('userType');
        const storedUserData = localStorage.getItem('userData');

        // Check if all required auth data exists
        if (!token || !userType || !storedUserData) {
          console.warn('Missing authentication data');
          setIsAuthorized(false);
          onUnauthorized();
          return;
        }

        // Check if user role matches required role
        if (userType !== requiredRole) {
          console.warn(`Role mismatch: required ${requiredRole}, got ${userType}`);
          setIsAuthorized(false);
          onUnauthorized();
          return;
        }

        // Validate token with backend
  const response = await fetch(`${API_BASE_URL}/api/v1/auth/me`, {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        });

        if (!response.ok) {
          console.warn('Token validation failed');
          setIsAuthorized(false);
          onUnauthorized();
          return;
        }

        const result = await response.json();

        if (!result.success || !result.data) {
          console.warn('Invalid token response');
          setIsAuthorized(false);
          onUnauthorized();
          return;
        }

        // Final role verification with backend data
        if (result.data.role !== requiredRole) {
          console.warn(`Backend role mismatch: required ${requiredRole}, got ${result.data.role}`);
          setIsAuthorized(false);
          onUnauthorized();
          return;
        }

        // Update stored user data if needed
        const currentUserData = JSON.parse(storedUserData) as UserData;
        if (currentUserData.role !== result.data.role) {
          localStorage.setItem('userData', JSON.stringify(result.data));
        }

        setIsAuthorized(true);

      } catch (error) {
        console.error('Auth validation error:', error);
        setIsAuthorized(false);
        onUnauthorized();
      } finally {
        setIsLoading(false);
      }
    };

    validateAccess();
  }, [requiredRole, onUnauthorized]);

  if (isLoading) {
    return (
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        height: '100vh',
        background: '#f8fafc'
      }}>
        <div style={{ textAlign: 'center' }}>
          <div style={{ fontSize: '24px', marginBottom: '10px' }}>🔐</div>
          <div>Verifying access...</div>
        </div>
      </div>
    );
  }

  if (!isAuthorized) {
    return (
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        height: '100vh',
        background: '#f8fafc'
      }}>
        <div style={{ textAlign: 'center' }}>
          <div style={{ fontSize: '24px', marginBottom: '10px' }}>🚫</div>
          <div>Access Denied</div>
          <div style={{ fontSize: '14px', color: '#6b7280', marginTop: '5px' }}>
            Redirecting to login...
          </div>
        </div>
      </div>
    );
  }

  return <>{children}</>;
}