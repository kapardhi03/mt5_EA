// frontend/src/services/apiService.js
import axios from 'axios';
import { API_CONFIG, API_ENDPOINTS } from '../config/api';

// Create axios instance
const api = axios.create({
  baseURL: API_CONFIG.baseURL,
  timeout: API_CONFIG.timeout,
  headers: API_CONFIG.headers,
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('accessToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original = error.config;
    
    if (error.response?.status === 401 && !original._retry) {
      original._retry = true;
      
      try {
        const refreshToken = localStorage.getItem('refreshToken');
        if (refreshToken) {
          const response = await axios.post(
            `${API_CONFIG.baseURL}${API_ENDPOINTS.REFRESH_TOKEN}`,
            { refresh_token: refreshToken }
          );
          
          const { access_token } = response.data.data;
          localStorage.setItem('accessToken', access_token);
          
          return api(original);
        }
      } catch {
        // Refresh failed, logout user
        localStorage.removeItem('accessToken');
        localStorage.removeItem('refreshToken');
        localStorage.removeItem('user');
        window.location.href = '/login';
      }
    }
    
    return Promise.reject(error);
  }
);

// API Service Class
class ApiService {
  // ===== AUTHENTICATION =====
  async login(credentials) {
    try {
      const response = await api.post(API_ENDPOINTS.LOGIN, credentials);
      
      if (response.data.success) {
        const { access_token, refresh_token, user } = response.data.data;
        
        // Store tokens and user data
        localStorage.setItem('accessToken', access_token);
        localStorage.setItem('refreshToken', refresh_token);
        localStorage.setItem('user', JSON.stringify(user));
        
        return response.data;
      } else {
        throw new Error(response.data.message || 'Login failed');
      }
    } catch (error) {
      throw new Error(error.response?.data?.detail || error.message || 'Login failed');
    }
  }

  async register(userData) {
    try {
      const response = await api.post(API_ENDPOINTS.REGISTER, userData);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || error.message || 'Registration failed');
    }
  }

  async sendOTP(otpData) {
    try {
      const response = await api.post(API_ENDPOINTS.SEND_OTP, otpData);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || error.message || 'Failed to send OTP');
    }
  }

  async verifyOTP(otpData) {
    try {
      const response = await api.post(API_ENDPOINTS.VERIFY_OTP, otpData);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || error.message || 'OTP verification failed');
    }
  }

  logout() {
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    localStorage.removeItem('user');
  }

  // ===== USER MANAGEMENT =====
  async getUserProfile() {
    try {
      const response = await api.get(API_ENDPOINTS.USER_PROFILE);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || error.message || 'Failed to fetch profile');
    }
  }

  async getUserDashboard() {
    try {
      const response = await api.get(API_ENDPOINTS.USER_DASHBOARD);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || error.message || 'Failed to fetch dashboard');
    }
  }

  async getUserAccounts() {
    try {
      const response = await api.get(API_ENDPOINTS.USER_ACCOUNTS);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || error.message || 'Failed to fetch accounts');
    }
  }

  async getUserPortfolio() {
    try {
      const response = await api.get(API_ENDPOINTS.USER_PORTFOLIO);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || error.message || 'Failed to fetch portfolio');
    }
  }

  // ===== GROUPS =====
  async getGroups(filters = {}) {
    try {
      const response = await api.get(API_ENDPOINTS.GROUPS, { params: filters });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || error.message || 'Failed to fetch groups');
    }
  }

  async createGroup(groupData) {
    try {
      const response = await api.post(API_ENDPOINTS.CREATE_GROUP, groupData);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || error.message || 'Failed to create group');
    }
  }

  async getGroupDetails(groupId) {
    try {
      const response = await api.get(API_ENDPOINTS.GROUP_DETAILS(groupId));
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || error.message || 'Failed to fetch group details');
    }
  }

  async getGroupMembers(groupId) {
    try {
      const response = await api.get(API_ENDPOINTS.GROUP_MEMBERS(groupId));
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || error.message || 'Failed to fetch group members');
    }
  }

  async joinGroup(groupId, joinData) {
    try {
      const response = await api.post(API_ENDPOINTS.JOIN_GROUP(groupId), joinData);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || error.message || 'Failed to join group');
    }
  }

  async leaveGroup(groupId) {
    try {
      const response = await api.post(API_ENDPOINTS.LEAVE_GROUP(groupId));
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || error.message || 'Failed to leave group');
    }
  }

  async updateGroupStatus(groupId, statusData) {
    try {
      const response = await api.patch(API_ENDPOINTS.UPDATE_GROUP_STATUS(groupId), statusData);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || error.message || 'Failed to update group status');
    }
  }

  async approveMember(memberId, approvalData = {}) {
    try {
      const response = await api.patch(API_ENDPOINTS.APPROVE_MEMBER(memberId), approvalData);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || error.message || 'Failed to approve member');
    }
  }

  async rejectMember(memberId, rejectionData) {
    try {
      const response = await api.patch(API_ENDPOINTS.REJECT_MEMBER(memberId), rejectionData);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || error.message || 'Failed to reject member');
    }
  }

  // Get pending members for approval
  async getPendingMembers() {
    try {
      const response = await api.get('/api/v1/groups/pending-members');
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || error.message || 'Failed to fetch pending members');
    }
  }

  // ===== MEMBERS =====
  async getMembers() {
    try {
      const response = await api.get(API_ENDPOINTS.MEMBERS);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || error.message || 'Failed to fetch members');
    }
  }

  async linkAccount(accountData) {
    try {
      const response = await api.post(API_ENDPOINTS.LINK_ACCOUNT, accountData);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || error.message || 'Failed to link account');
    }
  }

  // ===== SETTLEMENTS =====
  async getSettlements() {
    try {
      const response = await api.get(API_ENDPOINTS.SETTLEMENTS);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || error.message || 'Failed to fetch settlements');
    }
  }

  // ===== ADMIN =====
  async getAdminDashboard() {
    try {
      const response = await api.get(API_ENDPOINTS.ADMIN_DASHBOARD);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || error.message || 'Failed to fetch admin dashboard');
    }
  }

  async getAdminUsers() {
    try {
      const response = await api.get(API_ENDPOINTS.ADMIN_USERS);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || error.message || 'Failed to fetch users');
    }
  }

  // ===== NOTIFICATIONS =====
  async getNotifications() {
    try {
      const response = await api.get(API_ENDPOINTS.NOTIFICATIONS);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || error.message || 'Failed to fetch notifications');
    }
  }

  async markNotificationRead(notificationId) {
    try {
      const response = await api.patch(API_ENDPOINTS.MARK_READ(notificationId));
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || error.message || 'Failed to mark notification as read');
    }
  }

  // ===== SUPPORT =====
  async getSupportTickets() {
    try {
      const response = await api.get(API_ENDPOINTS.SUPPORT_TICKETS);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || error.message || 'Failed to fetch support tickets');
    }
  }

  async createSupportTicket(ticketData) {
    try {
      const response = await api.post(API_ENDPOINTS.CREATE_TICKET, ticketData);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || error.message || 'Failed to create support ticket');
    }
  }

  // ===== REPORTS =====
  async getReportsDashboard() {
    try {
      const response = await api.get(API_ENDPOINTS.REPORTS_DASHBOARD);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || error.message || 'Failed to fetch reports dashboard');
    }
  }

  async getDetailedReports(params) {
    try {
      const response = await api.get(API_ENDPOINTS.REPORTS_DETAILED, { params });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || error.message || 'Failed to fetch detailed reports');
    }
  }

  // ===== MASTER ACCOUNTS =====
  async getMasterAccounts() {
    try {
      const response = await api.get(API_ENDPOINTS.MASTER_ACCOUNTS);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || error.message || 'Failed to fetch master accounts');
    }
  }

  async createMasterAccount(masterData) {
    try {
      const response = await api.post(API_ENDPOINTS.MASTER_ACCOUNTS, masterData);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || error.message || 'Failed to create master account');
    }
  }

  async updateMasterAccount(masterId, masterData) {
    try {
      const response = await api.put(`${API_ENDPOINTS.MASTER_ACCOUNTS}/${masterId}`, masterData);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || error.message || 'Failed to update master account');
    }
  }

  // ===== GROUP MANAGEMENT =====
  async createTradingGroup(groupData) {
    try {
      const response = await api.post(API_ENDPOINTS.TRADING_GROUPS, groupData);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || error.message || 'Failed to create trading group');
    }
  }

  async getTradingGroups() {
    try {
      const response = await api.get(API_ENDPOINTS.TRADING_GROUPS);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || error.message || 'Failed to fetch trading groups');
    }
  }

  async updateTradingGroup(groupId, groupData) {
    try {
      const response = await api.put(`${API_ENDPOINTS.TRADING_GROUPS}/${groupId}`, groupData);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || error.message || 'Failed to update trading group');
    }
  }

  async toggleTradingGroup(groupId, action) {
    try {
      const response = await api.post(`${API_ENDPOINTS.TRADING_GROUPS}/${groupId}/${action}`);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || error.message || `Failed to ${action} trading group`);
    }
  }

  // ===== SETTLEMENT MANAGEMENT =====
  async getSettlementRequests() {
    try {
      const response = await api.get(API_ENDPOINTS.SETTLEMENT_REQUESTS);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || error.message || 'Failed to fetch settlement requests');
    }
  }

  async approveSettlement(settlementId, approvalData) {
    try {
      const response = await api.post(`${API_ENDPOINTS.SETTLEMENT_REQUESTS}/${settlementId}/approve`, approvalData);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || error.message || 'Failed to approve settlement');
    }
  }

  async rejectSettlement(settlementId, rejectionData) {
    try {
      const response = await api.post(`${API_ENDPOINTS.SETTLEMENT_REQUESTS}/${settlementId}/reject`, rejectionData);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || error.message || 'Failed to reject settlement');
    }
  }

  // ===== MEMBER APPROVALS =====
  async getPendingMembers() {
    try {
      const response = await api.get(API_ENDPOINTS.PENDING_MEMBERS);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || error.message || 'Failed to fetch pending members');
    }
  }

  async approveMember(memberId, approvalData) {
    try {
      const response = await api.post(`${API_ENDPOINTS.PENDING_MEMBERS}/${memberId}/approve`, approvalData);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || error.message || 'Failed to approve member');
    }
  }

  async rejectMember(memberId, rejectionData) {
    try {
      const response = await api.post(`${API_ENDPOINTS.PENDING_MEMBERS}/${memberId}/reject`, rejectionData);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || error.message || 'Failed to reject member');
    }
  }

  // ===== ERROR REPORTING =====
  async getErrorLogs(filters = {}) {
    try {
      const response = await api.get(API_ENDPOINTS.ERROR_LOGS, { params: filters });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || error.message || 'Failed to fetch error logs');
    }
  }

  async resolveError(errorId, resolutionData) {
    try {
      const response = await api.post(`${API_ENDPOINTS.ERROR_LOGS}/${errorId}/resolve`, resolutionData);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || error.message || 'Failed to resolve error');
    }
  }

  async retryFailedTrade(errorId) {
    try {
      const response = await api.post(`${API_ENDPOINTS.ERROR_LOGS}/${errorId}/retry`);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || error.message || 'Failed to retry trade');
    }
  }

  // ===== SYMBOL MAPPING =====
  async getSymbolMappings() {
    try {
      const response = await api.get(API_ENDPOINTS.SYMBOL_MAPPINGS);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || error.message || 'Failed to fetch symbol mappings');
    }
  }

  async createSymbolMapping(mappingData) {
    try {
      const response = await api.post(API_ENDPOINTS.SYMBOL_MAPPINGS, mappingData);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || error.message || 'Failed to create symbol mapping');
    }
  }

  async updateSymbolMapping(mappingId, mappingData) {
    try {
      const response = await api.put(`${API_ENDPOINTS.SYMBOL_MAPPINGS}/${mappingId}`, mappingData);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || error.message || 'Failed to update symbol mapping');
    }
  }

  async deleteSymbolMapping(mappingId) {
    try {
      const response = await api.delete(`${API_ENDPOINTS.SYMBOL_MAPPINGS}/${mappingId}`);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || error.message || 'Failed to delete symbol mapping');
    }
  }

  // ===== USER EA TRADING =====
  async getAvailableGroups() {
    try {
      const response = await api.get(API_ENDPOINTS.AVAILABLE_GROUPS);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || error.message || 'Failed to fetch available groups');
    }
  }

  async joinGroup(groupId, joinData) {
    try {
      const response = await api.post(`${API_ENDPOINTS.AVAILABLE_GROUPS}/${groupId}/join`, joinData);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || error.message || 'Failed to join group');
    }
  }

  async leaveGroup(groupId) {
    try {
      const response = await api.post(`${API_ENDPOINTS.MY_GROUPS}/${groupId}/leave`);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || error.message || 'Failed to leave group');
    }
  }

  async getMyGroups() {
    try {
      const response = await api.get(API_ENDPOINTS.MY_GROUPS);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || error.message || 'Failed to fetch my groups');
    }
  }

  async getEATrades() {
    try {
      const response = await api.get(API_ENDPOINTS.EA_TRADES);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || error.message || 'Failed to fetch EA trades');
    }
  }

  async getUserAccounts() {
    try {
      const response = await api.get(API_ENDPOINTS.USER_ACCOUNTS);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || error.message || 'Failed to fetch user accounts');
    }
  }

  async addUserAccount(accountData) {
    try {
      const response = await api.post(API_ENDPOINTS.USER_ACCOUNTS, accountData);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || error.message || 'Failed to add account');
    }
  }

  async updateAccountSettings(accountId, settingsData) {
    try {
      const response = await api.put(`${API_ENDPOINTS.USER_ACCOUNTS}/${accountId}/settings`, settingsData);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || error.message || 'Failed to update account settings');
    }
  }

  // ===== UTILITY METHODS =====
  getCurrentUser() {
    const userStr = localStorage.getItem('user');
    return userStr ? JSON.parse(userStr) : null;
  }

  getToken() {
    return localStorage.getItem('accessToken');
  }

  isAuthenticated() {
    return !!this.getToken();
  }
}

// Export singleton instance
export const apiService = new ApiService();
export default apiService;