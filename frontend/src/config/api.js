// frontend/src/config/api.js
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';

export const API_ENDPOINTS = {
    // Authentication
    LOGIN: '/api/v1/auth/login',
    REGISTER: '/api/v1/auth/register',
    SEND_OTP: '/api/v1/auth/send-otp',
    VERIFY_OTP: '/api/v1/auth/verify-otp',
    REFRESH_TOKEN: '/api/v1/auth/refresh',

    // User Management
    USER_DASHBOARD: '/api/v1/users/dashboard',
    USER_PROFILE: '/api/v1/users/profile',
    USER_ACCOUNTS: '/api/v1/users/accounts',
    USER_PORTFOLIO: '/api/v1/users/portfolio',

    // Groups
    GROUPS: '/api/v1/groups/list',
    CREATE_GROUP: '/api/v1/groups/create',
    GROUP_DETAILS: (id) => `/api/v1/groups/${id}`,
    GROUP_MEMBERS: (id) => `/api/v1/groups/${id}/members`,
    JOIN_GROUP: (id) => `/api/v1/groups/${id}/join`,
    LEAVE_GROUP: (id) => `/api/v1/groups/${id}/leave`,
    UPDATE_GROUP_STATUS: (id) => `/api/v1/groups/${id}/status`,
    APPROVE_MEMBER: (id) => `/api/v1/groups/members/${id}/approve`,
    REJECT_MEMBER: (id) => `/api/v1/groups/members/${id}/reject`,

    // Members
    MEMBERS: '/api/v1/members',
    MEMBER_DETAILS: (id) => `/api/v1/members/${id}`,
    LINK_ACCOUNT: '/api/v1/members/link-account',

    // Settlements
    SETTLEMENTS: '/api/v1/settlements',
    SETTLEMENT_DETAILS: (id) => `/api/v1/settlements/${id}`,

    // Reports
    REPORTS_DASHBOARD: '/api/v1/reports/dashboard',
    REPORTS_DETAILED: '/api/v1/reports/detailed',
    EXPORT_REPORT: '/api/v1/reports/export',

    // Admin
    ADMIN_DASHBOARD: '/api/v1/admin/dashboard',
    ADMIN_USERS: '/api/v1/admin/users',
    ADMIN_ANALYTICS: '/api/v1/admin/analytics',

    // Support
    SUPPORT_TICKETS: '/api/v1/support/tickets',
    CREATE_TICKET: '/api/v1/support/tickets',

    // Notifications
    NOTIFICATIONS: '/api/v1/notifications',
    MARK_READ: (id) => `/api/v1/notifications/${id}/read`,

    // Master Accounts
    MASTER_ACCOUNTS: '/api/v1/master-accounts'
};

export const API_CONFIG = {
    baseURL: API_BASE_URL,
    timeout: 30000,
    headers: {
        'Content-Type': 'application/json',
    }
};

export default API_BASE_URL;