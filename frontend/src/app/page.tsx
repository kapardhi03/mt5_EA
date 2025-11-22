"use client";
import React, { useState } from "react";
import LoginSystem from "./components/LoginSystem";
import API_BASE_URL from "@/config/api";
import RegistrationFlow from "./components/RegistrationFlow";
import AdminPanel from "./components/AdminPanel";
import UserPanel from "./components/UserPanel";
import MasterPanel from "./components/MasterPanel";
import GroupPanel from "./components/GroupPanel";
import AuthGuard from "./components/AuthGuard";
import SecurityLayer from "./components/SecurityLayer";

interface UserData {
  id: string;
  email: string;
  name: string;
  mobile: string;
  role: string;
  verified: boolean;
  createdAt: string;
}

interface AppState {
  lastVisitedPanel?: string;
  preferences?: any;
  navigationHistory?: string[];
  lastLogoutTime?: string;
  lastActiveTime?: string;
  sessionInfo?: any;
}

export default function Home() {
  const [userType, setUserType] = useState<'user' | 'admin' | 'master' | 'group_manager' | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [userData, setUserData] = useState<UserData | null>(null);
  const [showRegistration, setShowRegistration] = useState(false);
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [appState, setAppState] = useState<AppState>({});
  const [notification, setNotification] = useState<{type: 'success' | 'error' | 'info', message: string} | null>(null);

  // Show notification helper
  const showNotification = (type: 'success' | 'error' | 'info', message: string) => {
    setNotification({ type, message });
    setTimeout(() => setNotification(null), 5000);
  };

  // Check if user is already authenticated and validate JWT
  React.useEffect(() => {
    const validateAuth = async () => {
      setIsLoading(true);
      try {
        const token = localStorage.getItem('authToken');
        const type = localStorage.getItem('userType') as 'user' | 'admin' | 'master' | 'group_manager' | null;
        const storedUserData = localStorage.getItem('userData');
        const storedAppState = localStorage.getItem('appState');

        // Restore app state
        if (storedAppState) {
          try {
            setAppState(JSON.parse(storedAppState));
          } catch (e) {
            console.warn('Failed to parse stored app state');
          }
        }

        if (token && type && storedUserData) {
          try {
            // Validate JWT token with backend
            const response = await fetch(`${API_BASE_URL}/api/v1/auth/me`, {
              headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json',
              },
            });

            if (response.ok) {
              const result = await response.json();
              if (result.success && result.data) {
                // Verify role matches stored data
                const userRole = result.data.role;
                if (userRole === type) {
                  setUserType(userRole as 'user' | 'admin' | 'master' | 'group_manager');
                  setIsAuthenticated(true);
                  setUserData(result.data);
                  showNotification('success', `Welcome back, ${result.data.name}!`);
                } else {
                  // Role mismatch - clear invalid session
                  showNotification('error', 'Session expired. Please login again.');
                  handleLogout();
                }
              } else {
                showNotification('error', 'Session expired. Please login again.');
                handleLogout();
              }
            } else {
              // Invalid token - clear session
              showNotification('error', 'Session expired. Please login again.');
              handleLogout();
            }
          } catch (error) {
            console.error('Auth validation failed:', error);
            showNotification('error', 'Connection error. Please check your internet.');
            handleLogout();
          }
        }
      } finally {
        setIsLoading(false);
      }
    };

    validateAuth();
  }, []);

  const handleAuthSuccess = (type: 'user' | 'admin' | 'master' | 'group_manager', userData: UserData) => {
    // Ensure role matches what backend says
    if (userData.role === type) {
      setUserType(type);
      setIsAuthenticated(true);
      setUserData(userData);
      setShowRegistration(false);
      setError('');

      // Update app state navigation
      const newAppState = {
        ...appState,
        lastVisitedPanel: type,
        navigationHistory: [...(appState.navigationHistory || []), type]
      };
      setAppState(newAppState);
      localStorage.setItem('appState', JSON.stringify(newAppState));

      showNotification('success', `Welcome, ${userData.name}! You are now logged in.`);
    } else {
      console.error('Role mismatch in authentication');
      setError('Authentication error: Role mismatch');
      showNotification('error', 'Authentication error: Role mismatch');
    }
  };

  const handleRegistrationSuccess = () => {
    // After registration, redirect to login instead of auto-authenticating
    setShowRegistration(false);
    showNotification('success', 'Registration completed! Please login with your credentials.');
  };

  const saveAppState = () => {
    const currentAppState = {
      ...appState,
      lastLogoutTime: new Date().toISOString(),
      preferences: {
        ...appState.preferences,
        theme: 'default',
        language: 'en'
      },
      sessionInfo: {
        browser: navigator.userAgent,
        timestamp: new Date().toISOString(),
        url: window.location.href
      }
    };
    localStorage.setItem('appState', JSON.stringify(currentAppState));
  };

  // Auto-save app state periodically
  React.useEffect(() => {
    const interval = setInterval(() => {
      if (isAuthenticated && userType) {
        const currentAppState = {
          ...appState,
          lastVisitedPanel: userType,
          lastActiveTime: new Date().toISOString(),
          navigationHistory: [...(appState.navigationHistory || []), userType].slice(-10) // Keep only last 10
        };
        setAppState(currentAppState);
        localStorage.setItem('appState', JSON.stringify(currentAppState));
      }
    }, 5 * 60 * 1000); // Save every 5 minutes (reduced from 30 seconds)

    return () => clearInterval(interval);
  }, [isAuthenticated, userType, appState]);

  const handleLogout = () => {
    // Save current state before logout
    saveAppState();

    // Clear auth data but preserve app state
    setUserType(null);
    setIsAuthenticated(false);
    setUserData(null);
    setError('');

    // Clear auth tokens but keep app state
    localStorage.removeItem('userType');
    localStorage.removeItem('authToken');
    localStorage.removeItem('userData');

    showNotification('info', 'You have been logged out successfully.');
  };

  // Loading state
  if (isLoading) {
    return (
      <div style={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: '#f8fafc'
      }}>
        <div style={{ textAlign: 'center' }}>
          <div style={{
            width: '50px',
            height: '50px',
            border: '5px solid #e5e7eb',
            borderTop: '5px solid #3b82f6',
            borderRadius: '50%',
            animation: 'spin 1s linear infinite',
            margin: '0 auto 20px'
          }}></div>
          <p style={{ color: '#6b7280', fontSize: '16px' }}>Loading EA Trading Platform...</p>
        </div>
        <style jsx>{`
          @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
          }
        `}</style>
      </div>
    );
  }

  // Notification Component
  const NotificationComponent = () => {
    if (!notification) return null;

    const bgColor = notification.type === 'success' ? '#dcfce7' :
                   notification.type === 'error' ? '#fef2f2' : '#eff6ff';
    const textColor = notification.type === 'success' ? '#166534' :
                     notification.type === 'error' ? '#dc2626' : '#1d4ed8';

    return (
      <div style={{
        position: 'fixed',
        top: '20px',
        right: '20px',
        background: bgColor,
        color: textColor,
        padding: '12px 20px',
        borderRadius: '8px',
        boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
        zIndex: 10000,
        maxWidth: '400px',
        border: `1px solid ${notification.type === 'success' ? '#bbf7d0' :
                              notification.type === 'error' ? '#fecaca' : '#bfdbfe'}`
      }}>
        {notification.message}
      </div>
    );
  };

  // Show appropriate panel based on user type with strict role validation and AuthGuard protection
  if (isAuthenticated && userType === 'admin' && userData?.role === 'admin') {
    return (
      <>
        <NotificationComponent />
        <SecurityLayer>
          <AuthGuard requiredRole="admin" onUnauthorized={handleLogout}>
            <AdminPanel onLogout={handleLogout} />
          </AuthGuard>
        </SecurityLayer>
      </>
    );
  }

  if (isAuthenticated && userType === 'master' && userData?.role === 'master' && userData) {
    return (
      <>
        <NotificationComponent />
        <SecurityLayer>
          <AuthGuard requiredRole="master" onUnauthorized={handleLogout}>
            <MasterPanel onLogout={handleLogout} userData={userData} />
          </AuthGuard>
        </SecurityLayer>
      </>
    );
  }

  if (isAuthenticated && userType === 'group_manager' && userData?.role === 'group_manager') {
    return (
      <>
        <NotificationComponent />
        <SecurityLayer>
          <AuthGuard requiredRole="group_manager" onUnauthorized={handleLogout}>
            <GroupPanel onLogout={handleLogout} />
          </AuthGuard>
        </SecurityLayer>
      </>
    );
  }

  if (isAuthenticated && userType === 'user' && userData?.role === 'user') {
    return (
      <>
        <NotificationComponent />
        <SecurityLayer>
          <AuthGuard requiredRole="user" onUnauthorized={handleLogout}>
            <UserPanel onLogout={handleLogout} />
          </AuthGuard>
        </SecurityLayer>
      </>
    );
  }

  // If authenticated but role doesn't match, logout
  if (isAuthenticated) {
    handleLogout();
    return null;
  }

  // Show registration flow if requested
  if (showRegistration) {
    return (
      <>
        <NotificationComponent />
        <div style={{ minHeight: '100vh', background: '#f8fafc' }}>
          <div style={{
            position: 'fixed',
            top: '20px',
            right: '20px',
            zIndex: 1000
          }}>
            <button
              className="btn btn-outline btn-sm"
              onClick={() => {
                setShowRegistration(false);
                showNotification('info', 'Switched back to login page.');
              }}
            >
              Back to Login
            </button>
          </div>
          <RegistrationFlow onAuthSuccess={handleRegistrationSuccess} />
        </div>
      </>
    );
  }

  // Show login system for non-authenticated users
  return (
    <>
      <NotificationComponent />
      <div style={{ minHeight: '100vh', background: '#f8fafc' }}>
        {/* Show helpful context if user just logged out */}
        {appState.lastLogoutTime && (
          <div style={{
            background: '#f0f9ff',
            padding: '12px',
            textAlign: 'center',
            color: '#1e40af',
            fontSize: '14px',
            borderBottom: '1px solid #e0e7ff'
          }}>
            Welcome back to EA Trading Platform! Last visited: {appState.lastVisitedPanel || 'N/A'}
          </div>
        )}

        <div style={{
          position: 'fixed',
          top: '20px',
          right: '20px',
          zIndex: 1000,
          display: 'flex',
          gap: '10px'
        }}>
          <button
            className="btn btn-outline btn-sm"
            onClick={() => {
              setShowRegistration(true);
              showNotification('info', 'Switched to registration page.');
            }}
          >
            New User Registration
          </button>
        </div>

        <LoginSystem onAuthSuccess={handleAuthSuccess} />
      </div>
    </>
  );
}