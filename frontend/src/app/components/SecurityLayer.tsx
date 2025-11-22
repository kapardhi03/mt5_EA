"use client";
import React, { useEffect } from 'react';
import API_BASE_URL from '@/config/api';

interface SecurityLayerProps {
  children: React.ReactNode;
}

export default function SecurityLayer({ children }: SecurityLayerProps) {
  useEffect(() => {
    // Prevent right-click context menu (basic security measure)
    const handleContextMenu = (e: MouseEvent) => {
      e.preventDefault();
    };

    // Prevent F12, Ctrl+Shift+I, Ctrl+U (basic security measure)
    const handleKeyDown = (e: KeyboardEvent) => {
      if (
        e.key === 'F12' ||
        (e.ctrlKey && e.shiftKey && e.key === 'I') ||
        (e.ctrlKey && e.key === 'u')
      ) {
        e.preventDefault();
        console.warn('Developer tools access attempt blocked');
      }
    };

    // Add security headers via meta tags
    const addSecurityHeaders = () => {
      // Prevent iframe embedding
      if (window !== window.top) {
        window.top!.location.href = window.location.href;
      }

      // Add Content Security Policy via meta tag
      let cspMeta = document.querySelector('meta[http-equiv="Content-Security-Policy"]');
      if (!cspMeta) {
        cspMeta = document.createElement('meta');
        cspMeta.setAttribute('http-equiv', 'Content-Security-Policy');

        const apiOrigin = (() => {
          try {
            const url = new URL(API_BASE_URL);
            return `${url.protocol}//${url.host}`;
          } catch (error) {
            console.warn('Unable to parse API base URL for CSP', error);
            return API_BASE_URL;
          }
        })();

        const websocketOrigin = (() => {
          try {
            const url = new URL(API_BASE_URL);
            const wsProtocol = url.protocol === 'https:' ? 'wss:' : 'ws:';
            return `${wsProtocol}//${url.host}`;
          } catch {
            return '';
          }
        })();

        const connectSources = [
          "'self'",
          apiOrigin,
          'http://localhost:8000',
          'http://127.0.0.1:8000',
          websocketOrigin || 'ws://localhost:8000',
        ].filter(Boolean);

        cspMeta.setAttribute('content', `default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; connect-src ${connectSources.join(' ')}`);
        document.head.appendChild(cspMeta);
      }

      // Add X-Frame-Options
      let frameMeta = document.querySelector('meta[http-equiv="X-Frame-Options"]');
      if (!frameMeta) {
        frameMeta = document.createElement('meta');
        frameMeta.setAttribute('http-equiv', 'X-Frame-Options');
        frameMeta.setAttribute('content', 'DENY');
        document.head.appendChild(frameMeta);
      }
    };

    // Monitor for unauthorized token manipulation
    const monitorLocalStorage = () => {
      const originalSetItem = localStorage.setItem;
      localStorage.setItem = function(key: string, value: string) {
        if (key === 'authToken' || key === 'userType' || key === 'userData') {
          console.warn('Authentication data modification detected');
          // In production, you might want to log this to your security monitoring system
        }
        originalSetItem.call(this, key, value);
      };
    };

    // Session timeout monitoring
    const setupSessionTimeout = () => {
      let lastActivity = Date.now();
      const SESSION_TIMEOUT = 2 * 60 * 60 * 1000; // 2 hours (increased from 30 minutes)

      const updateActivity = () => {
        lastActivity = Date.now();
      };

      const checkSession = () => {
        if (Date.now() - lastActivity > SESSION_TIMEOUT) {
          const token = localStorage.getItem('authToken');
          if (token) {
            console.warn('Session timeout - logging out gracefully');
            localStorage.removeItem('authToken');
            localStorage.removeItem('userType');
            localStorage.removeItem('userData');
            // Instead of forcing reload, redirect to login page
            window.location.href = '/';
          }
        }
      };

      // Add activity listeners
      document.addEventListener('mousedown', updateActivity);
      document.addEventListener('keydown', updateActivity);
      document.addEventListener('scroll', updateActivity);
      document.addEventListener('touchstart', updateActivity);

      // Check session every 5 minutes (reduced frequency)
      const sessionInterval = setInterval(checkSession, 5 * 60 * 1000);

      return () => {
        clearInterval(sessionInterval);
        document.removeEventListener('mousedown', updateActivity);
        document.removeEventListener('keydown', updateActivity);
        document.removeEventListener('scroll', updateActivity);
        document.removeEventListener('touchstart', updateActivity);
      };
    };

    // Initialize security measures
    document.addEventListener('contextmenu', handleContextMenu);
    document.addEventListener('keydown', handleKeyDown);
    addSecurityHeaders();
    monitorLocalStorage();
    const cleanupSession = setupSessionTimeout();

    // Cleanup function
    return () => {
      document.removeEventListener('contextmenu', handleContextMenu);
      document.removeEventListener('keydown', handleKeyDown);
      cleanupSession();
    };
  }, []);

  return <>{children}</>;
}