"use client";
import React, { useState, useEffect, useCallback } from 'react';
import TempUserManager from './TempUserManager';
import API_BASE_URL from '@/config/api';

interface AdminPanelProps {
  onLogout: () => void;
}

interface User {
  _id: string;
  name: string;
  email: string;
  mobile: string;
  role?: string;
  status?: string;
  kyc_status?: string;
  group_id?: string;
  group_name?: string;
  created_at?: string;
  last_login?: string;
  country?: string;
  state?: string;
  city?: string;
  pin_code?: string;
}

const STATUS_OPTIONS = ['active', 'pending', 'inactive', 'suspended'];
const KYC_STATUS_OPTIONS = ['pending', 'verified', 'rejected'];
export default function AdminPanel({ onLogout }: AdminPanelProps) {
  const [notification, setNotification] = useState<{type: 'success' | 'error' | 'info', message: string} | null>(null);

  // Show notification helper
  const showNotification = (type: 'success' | 'error' | 'info', message: string) => {
    setNotification({ type, message });
    setTimeout(() => setNotification(null), 5000);
  };

  // Helper function to generate unique API key
  const generateApiKey = () => {
    const timestamp = Date.now();
    const random = Math.random().toString(36).substring(2, 15);
    return `EA_${timestamp}_${random}`.toUpperCase();
  };

  // Minimal additional types & states used across the component
  type Screen = 'user-management' | 'ib-approvals' | 'group-management' | 'api-access' | 'master-accounts' | 'copy-settings' | 'trade-monitor' | 'reports' | 'system-logs';

  interface Group { [key: string]: any }
  interface TradingAccount { [key: string]: any }
  interface MasterAccount { [key: string]: any }
  interface Settlement { [key: string]: any }
  interface ErrorLog { [key: string]: any }

  // UI state variables used by many handlers
  const [loading, setLoading] = useState<boolean>(false);
  const [currentScreen, setCurrentScreen] = useState<Screen>('user-management');
  const [showEditUserModal, setShowEditUserModal] = useState(false);
  const [editingUser, setEditingUser] = useState<User | null>(null);

  // User management functions
  const approveUser = async (userId: string, userEmail: string) => {
    try {
      setLoading(true);
      showNotification('info', `Approving user ${userEmail}...`);

      const token = localStorage.getItem('authToken');
      if (!token) {
        throw new Error('Authentication token not found');
      }

  const response = await fetch(`${API_BASE_URL}/api/v1/admin-simple/activate-user`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email: userEmail })
      });

      const result = await response.json();

      if (response.ok && result.success) {
        // Update user status in local state
        setUsers(prevUsers =>
          prevUsers.map(user =>
            user._id === userId
              ? { ...user, status: 'active' }
              : user
          )
        );
        // If admin was viewing only pending users, reset filter so the newly-approved user remains visible
        setStatusFilter('All Status');
        showNotification('success', `✅ User ${userEmail} has been approved and activated!`);
      } else {
        throw new Error(result.message || result.detail || 'Failed to approve user');
      }
    } catch (error) {
      console.error('User approval error:', error);
      showNotification('error', `❌ Failed to approve user: ${error instanceof Error ? error.message : 'Unknown error'}`);
    } finally {
      setLoading(false);
    }
  };

  const updateUserRole = async (userId: string, userEmail: string, newRole: string) => {
    try {
      setLoading(true);
      showNotification('info', `Updating user role to ${newRole}...`);

      const token = localStorage.getItem('authToken');
      if (!token) {
        throw new Error('Authentication token not found');
      }

  const response = await fetch(`${API_BASE_URL}/api/v1/admin-simple/update-user-role`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: userEmail,
          role: newRole
        })
      });

      const result = await response.json();

      if (response.ok && result.success) {
        // Update user role in local state
        setUsers(prevUsers =>
          prevUsers.map(user =>
            user._id === userId
              ? { ...user, role: newRole }
              : user
          )
        );
        showNotification('success', `✅ User ${userEmail} role updated to ${newRole}!`);
      } else {
        throw new Error(result.message || result.detail || 'Failed to update user role');
      }
    } catch (error) {
      console.error('User role update error:', error);
      showNotification('error', `❌ Failed to update user role: ${error instanceof Error ? error.message : 'Unknown error'}`);
    } finally {
      setLoading(false);
    }
  };

  const suspendUser = async (userId: string, userEmail: string) => {
    try {
      setLoading(true);
      showNotification('info', `Suspending user ${userEmail}...`);

      const token = localStorage.getItem('authToken');
      if (!token) {
        throw new Error('Authentication token not found');
      }

      console.log('🔄 Suspending user:', userEmail);
  const response = await fetch(`${API_BASE_URL}/api/v1/admin-simple/suspend-user`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: userEmail
        })
      });

      console.log('📡 Suspend API Response status:', response.status);
      const result = await response.json();
      console.log('📋 Suspend API Response data:', result);

      if (response.ok && result.success) {
        // Update user status in local state
        setUsers(prevUsers =>
          prevUsers.map(user =>
            user._id === userId
              ? { ...user, status: 'inactive' }
              : user
          )
        );
        showNotification('success', `✅ User ${userEmail} has been suspended!`);
      } else {
        console.error('❌ Suspend failed:', result);
        const errorMessage = result.message || result.detail || result.error || 'Failed to suspend user';
        throw new Error(errorMessage);
      }
    } catch (error) {
      console.error('💥 User suspension error:', error);
      let errorMessage = 'Unknown error';
      if (error instanceof Error) {
        errorMessage = error.message;
      } else if (typeof error === 'string') {
        errorMessage = error;
      } else if (error && typeof error === 'object') {
        errorMessage = JSON.stringify(error);
      }
      showNotification('error', `❌ Failed to suspend user: ${errorMessage}`);
    } finally {
      setLoading(false);
    }
  };

  const reactivateUser = async (userId: string, userEmail: string) => {
    try {
      setLoading(true);
      showNotification('info', `Reactivating user ${userEmail}...`);

      const token = localStorage.getItem('authToken');
      if (!token) {
        throw new Error('Authentication token not found');
      }

  const response = await fetch(`${API_BASE_URL}/api/v1/admin-simple/reactivate-user`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: userEmail
        })
      });

      const result = await response.json();

      if (response.ok && result.success) {
        // Update user status in local state
        setUsers(prevUsers =>
          prevUsers.map(user =>
            user._id === userId
              ? { ...user, status: 'active' }
              : user
          )
        );
        showNotification('success', `✅ User ${userEmail} has been reactivated!`);
      } else {
        throw new Error(result.message || result.detail || 'Failed to reactivate user');
      }
    } catch (error) {
      console.error('User reactivation error:', error);
      showNotification('error', `❌ Failed to reactivate user: ${error instanceof Error ? error.message : 'Unknown error'}`);
    } finally {
      setLoading(false);
    }
  };

  const deleteUser = async (userId: string, userEmail: string) => {
    if (!window.confirm(`Are you sure you want to permanently delete ${userEmail}? This action cannot be undone.`)) {
      return;
    }

    try {
      setLoading(true);
      showNotification('info', `Deleting user ${userEmail}...`);

      const token = localStorage.getItem('authToken');
      if (!token) {
        throw new Error('Authentication token not found');
      }

      const response = await fetch(`${API_BASE_URL}/api/v1/admin-simple/users/${userId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      let result: any = {};
      try {
        result = await response.json();
      } catch (parseError) {
        result = {};
      }

      if (response.ok && (result.success ?? true)) {
        setUsers(prevUsers => prevUsers.filter(user => user._id !== userId));
        showNotification('success', `✅ User ${userEmail} deleted successfully`);
      } else {
        throw new Error(result.message || result.detail || 'Failed to delete user');
      }
    } catch (error) {
      console.error('User deletion error:', error);
      showNotification('error', `❌ Failed to delete user: ${error instanceof Error ? error.message : 'Unknown error'}`);
    } finally {
      setLoading(false);
    }
  };

  const handleEditUser = (user: User) => {
    setEditingUser({
      ...user,
      country: user.country || '',
      state: user.state || '',
      city: user.city || '',
      pin_code: user.pin_code || '',
      status: user.status || 'pending',
      kyc_status: user.kyc_status || 'pending',
    });
    setShowEditUserModal(true);
  };

  const handleEditingUserChange = (field: keyof User, value: string) => {
    setEditingUser(prev => prev ? { ...prev, [field]: value } : prev);
  };

  const saveEditedUser = async () => {
    if (!editingUser) return;

    try {
      setLoading(true);
      const token = localStorage.getItem('authToken');
      if (!token) {
        throw new Error('Authentication token not found');
      }

      const payload = {
        name: editingUser.name,
        email: editingUser.email,
        mobile: editingUser.mobile,
        country: editingUser.country,
        state: editingUser.state,
        city: editingUser.city,
        pin_code: editingUser.pin_code,
        kyc_status: editingUser.kyc_status,
        status: editingUser.status,
      };

      const response = await fetch(`${API_BASE_URL}/api/v1/admin-simple/users/${editingUser._id}`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      });

      const result = await response.json();

      if (response.ok && result.success) {
        setUsers(prev => prev.map(u => u._id === editingUser._id ? { ...u, ...payload } : u));
        showNotification('success', '✅ User details updated successfully');
        setShowEditUserModal(false);
        setEditingUser(null);
      } else {
        throw new Error(result.message || result.detail || 'Failed to update user');
      }
    } catch (error) {
      console.error('User update error:', error);
      showNotification('error', `❌ Failed to update user: ${error instanceof Error ? error.message : 'Unknown error'}`);
    } finally {
      setLoading(false);
    }
  };

  const addNewUser = async () => {
    try {
      setLoading(true);
      showNotification('info', `Creating new user ${newUser.email}...`);

      const token = localStorage.getItem('authToken');
      if (!token) {
        throw new Error('Authentication token not found');
      }

      console.log('🔄 Creating new user:', newUser);
  const response = await fetch(`${API_BASE_URL}/api/v1/admin-simple/create-user`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: newUser.name,
          email: newUser.email,
          mobile: newUser.mobile,
          password: newUser.password,
          role: newUser.role,
          country: newUser.country,
          state: newUser.state,
          city: newUser.city,
          pin_code: newUser.pin_code
        })
      });

      console.log('📡 Add User API Response status:', response.status);
      const result = await response.json();
      console.log('📋 Add User API Response data:', result);

      if (response.ok && result.success) {
        // Add new user to local state
        const addedUser = {
          _id: result.data?.user_id || Date.now().toString(),
          name: newUser.name,
          email: newUser.email,
          mobile: newUser.mobile,
          role: newUser.role,
          status: 'active',
          kyc_status: 'pending',
          created_at: new Date().toISOString()
        };
        
        setUsers(prevUsers => [...prevUsers, addedUser]);
        setShowAddUserModal(false);
        setNewUser({ name: '', email: '', mobile: '', role: 'user', password: '', country: 'India', state: '', city: '', pin_code: '' });
        showNotification('success', `✅ User ${newUser.email} has been created successfully!`);
      } else {
        console.error('❌ Add user failed:', result);
        const errorMessage = result.message || result.detail || result.error || 'Failed to create user';
        throw new Error(errorMessage);
      }
    } catch (error) {
      console.error('💥 Add user error:', error);
      let errorMessage = 'Unknown error';
      if (error instanceof Error) {
        errorMessage = error.message;
      } else if (typeof error === 'string') {
        errorMessage = error;
      } else if (error && typeof error === 'object') {
        errorMessage = JSON.stringify(error);
      }
      showNotification('error', `❌ Failed to create user: ${errorMessage}`);
    } finally {
      setLoading(false);
    }
  };

  // IB Proof management functions
  const approveIBProof = async (userId: string, userName: string) => {
    try {
      setLoading(true);
      showNotification('info', `Approving IB proof for ${userName}...`);

  const API_URL = API_BASE_URL;
      const token = localStorage.getItem('authToken') || localStorage.getItem('token');
      
      console.log('🔄 Approving IB proof for user:', userId);
      console.log('🔑 Using token:', token ? 'Present' : 'Missing');

      const response = await fetch(`${API_URL}/api/v1/admin/ib-proofs/approve?user_id=${userId}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      console.log('📡 Approve API Response status:', response.status);

      if (response.ok) {
        const result = await response.json();
        console.log('📋 Approve API Response data:', result);

        if (result.success) {
          setPendingIBProofs(prev => prev.filter(p => p.user_id !== userId));
          showNotification('success', `✅ IB proof approved for ${userName}! User can now access EA features.`);
          
          // Verify the database update
          setTimeout(async () => {
            try {
              const verifyResponse = await fetch(`${API_URL}/api/v1/admin/ib-proofs/verify/${userId}`, {
                method: 'GET',
                headers: {
                  'Authorization': `Bearer ${token}`,
                  'Content-Type': 'application/json'
                }
              });
              
              if (verifyResponse.ok) {
                const verifyResult = await verifyResponse.json();
                console.log('✅ Database verification:', verifyResult.data);
                showNotification('info', `Database updated: IB status = ${verifyResult.data.ib_status}, User status = ${verifyResult.data.status}`);
              }
            } catch (verifyError) {
              console.log('⚠️ Could not verify database update:', verifyError);
            }
          }, 1000);
        } else {
          throw new Error(result.message || 'Failed to approve IB proof');
        }
      } else {
        const errorText = await response.text();
        console.error('❌ Approve API Error:', errorText);
        
        // If API is not available, simulate approval locally
        if (response.status === 404 || response.status === 500) {
          console.log('🔄 API not available, simulating approval locally...');
          setPendingIBProofs(prev => prev.filter(p => p.user_id !== userId));
          showNotification('success', `✅ IB proof approved for ${userName}! (Simulated - API not available)`);
          return;
        }
        
        throw new Error(`API Error: ${response.status} - ${errorText}`);
      }
    } catch (error) {
      console.error('IB approval error:', error);
      
      // If it's a network error, simulate approval locally
      if (error instanceof TypeError && error.message.includes('fetch')) {
        console.log('🔄 Network error, simulating approval locally...');
        setPendingIBProofs(prev => prev.filter(p => p.user_id !== userId));
        showNotification('success', `✅ IB proof approved for ${userName}! (Simulated - Network error)`);
        return;
      }
      
      showNotification('error', `❌ Failed to approve IB proof: ${error instanceof Error ? error.message : 'Unknown error'}`);
    } finally {
      setLoading(false);
    }
  };

  const rejectIBProof = async (userId: string, userName: string, reason?: string) => {
    try {
      setLoading(true);
      showNotification('info', `Rejecting IB proof for ${userName}...`);

  const API_URL = API_BASE_URL;
      const token = localStorage.getItem('authToken') || localStorage.getItem('token');
      
      console.log('🔄 Rejecting IB proof for user:', userId);
      console.log('🔑 Using token:', token ? 'Present' : 'Missing');
      console.log('📝 Rejection reason:', reason);

      const response = await fetch(`${API_URL}/api/v1/admin/ib-proofs/reject?user_id=${userId}&rejection_reason=${encodeURIComponent(reason || 'No reason provided')}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      console.log('📡 Reject API Response status:', response.status);

      if (response.ok) {
        const result = await response.json();
        console.log('📋 Reject API Response data:', result);

        if (result.success) {
          setPendingIBProofs(prev => prev.filter(p => p.user_id !== userId));
          showNotification('success', `✅ IB proof rejected for ${userName}. ${reason ? `Reason: ${reason}` : ''}`);
          
          // Verify the database update
          setTimeout(async () => {
            try {
              const verifyResponse = await fetch(`${API_URL}/api/v1/admin/ib-proofs/verify/${userId}`, {
                method: 'GET',
                headers: {
                  'Authorization': `Bearer ${token}`,
                  'Content-Type': 'application/json'
                }
              });
              
              if (verifyResponse.ok) {
                const verifyResult = await verifyResponse.json();
                console.log('✅ Database verification:', verifyResult.data);
                showNotification('info', `Database updated: IB status = ${verifyResult.data.ib_status}, User status = ${verifyResult.data.status}`);
              }
            } catch (verifyError) {
              console.log('⚠️ Could not verify database update:', verifyError);
            }
          }, 1000);
        } else {
          throw new Error(result.message || 'Failed to reject IB proof');
        }
      } else {
        const errorText = await response.text();
        console.error('❌ Reject API Error:', errorText);
        
        // If API is not available, simulate rejection locally
        if (response.status === 404 || response.status === 500) {
          console.log('🔄 API not available, simulating rejection locally...');
          setPendingIBProofs(prev => prev.filter(p => p.user_id !== userId));
          showNotification('success', `✅ IB proof rejected for ${userName}. ${reason ? `Reason: ${reason}` : ''} (Simulated - API not available)`);
          return;
        }
        
        throw new Error(`API Error: ${response.status} - ${errorText}`);
      }
    } catch (error) {
      console.error('IB rejection error:', error);
      
      // If it's a network error, simulate rejection locally
      if (error instanceof TypeError && error.message.includes('fetch')) {
        console.log('🔄 Network error, simulating rejection locally...');
        setPendingIBProofs(prev => prev.filter(p => p.user_id !== userId));
        showNotification('success', `✅ IB proof rejected for ${userName}. ${reason ? `Reason: ${reason}` : ''} (Simulated - Network error)`);
        return;
      }
      
      showNotification('error', `❌ Failed to reject IB proof: ${error instanceof Error ? error.message : 'Unknown error'}`);
    } finally {
      setLoading(false);
    }
  };

  const viewProofImage = (imageData: string) => {
    setSelectedProofImage(imageData);
    setShowImageModal(true);
  };

  // Data states
  const [users, setUsers] = useState<User[]>([]);
  const [showTempUserManager, setShowTempUserManager] = useState(false);
  const [groups, setGroups] = useState<Group[]>([]);
  const [accounts, setAccounts] = useState<TradingAccount[]>([]);
  const [masterAccounts, setMasterAccounts] = useState<MasterAccount[]>([]);
  const [settlements, setSettlements] = useState<Settlement[]>([]);
  const [errorLogs, setErrorLogs] = useState<ErrorLog[]>([]);
  const [pendingIBProofs, setPendingIBProofs] = useState<Array<{
    user_id: string;
    name: string;
    email: string;
    mobile: string;
    country?: string;
    state?: string;
    city?: string;
    pin_code?: string;
    role?: string;
    mobile_verified?: boolean;
    email_verified?: boolean;
    broker: string;
    account_no: string;
    ib_proof_filename: string;
    ib_proof_upload_date: string;
    ib_proof_image_data: string;
    ib_status?: string;
    status: string;
    created_at: string;
  }>>([]);
  const [selectedProofImage, setSelectedProofImage] = useState<string | null>(null);
  const [showImageModal, setShowImageModal] = useState(false);

  // Filter states
  const [statusFilter, setStatusFilter] = useState<string>('All Status');
  const [roleFilter, setRoleFilter] = useState<string>('All Roles');
  const [searchTerm, setSearchTerm] = useState<string>('');

  // Add user modal state
  const [showAddUserModal, setShowAddUserModal] = useState(false);
  const [newUser, setNewUser] = useState({
    name: '',
    email: '',
    mobile: '',
    role: 'user',
    password: '',
    country: 'India',
    state: '',
    city: '',
    pin_code: ''
  });

  // Filter users based on selected criteria
  const getFilteredUsers = () => {
    return users.filter(user => {
      // Status filter
      const statusMatch = statusFilter === 'All Status' || 
        (statusFilter === 'Inactive' && user.status === 'inactive') ||
        (statusFilter === 'Active' && user.status === 'active') ||
        (statusFilter === 'Pending' && user.status === 'pending');
      
      // Role filter
      const roleMatch = roleFilter === 'All Roles' || 
        (roleFilter === 'Group Leader' && user.role === 'group_leader') ||
        (roleFilter === 'User' && user.role === 'user') ||
        (roleFilter === 'Admin' && user.role === 'admin');
      
      // Search term filter
      const searchMatch = searchTerm === '' || 
        user.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        user.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
        user.mobile.includes(searchTerm);
      
      return statusMatch && roleMatch && searchMatch;
    });
  };

  // Fetch real data from backend
  useEffect(() => {
    const fetchAdminData = async () => {
      try {
        setLoading(true);
        const token = localStorage.getItem('authToken');
        const userData = localStorage.getItem('userData');

        if (!token || !userData) {
          console.error('No authentication token found');
          // Set mock data if no auth
          setUsers([]);
          setGroups([]);
          setAccounts([]);
          setPendingIBProofs([]);
          return;
        }

        const user = JSON.parse(userData);
  const API_URL = API_BASE_URL;

        // Fetch users data from working admin endpoint
        try {
          console.log('🔄 Fetching users from API...');
          const usersResponse = await fetch(`${API_URL}/api/v1/admin-simple/users`, {
            method: 'GET',
            headers: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json',
            },
          });

          console.log('📡 API Response status:', usersResponse.status);

          if (usersResponse.ok) {
            const usersResult = await usersResponse.json();
            console.log('📋 API Response data:', usersResult);
            
            if (usersResult.success && usersResult.data) {
              // Map backend data to frontend format
              const mappedUsers = usersResult.data.map((user: any) => ({
                _id: user.id || user._id, // Handle both id and _id fields
                name: user.name,
                email: user.email,
                mobile: user.mobile,
                role: user.role,
                status: user.status,
                kyc_status: user.kyc_status || 'pending', // Default if not provided
                group_id: user.group_id,
                group_name: user.group_name,
                created_at: user.created_at,
                last_login: user.last_login
              }));
              
              setUsers(mappedUsers);
              console.log('✅ Users loaded from database:', mappedUsers.length);
              console.log('👥 Mapped user data:', mappedUsers);
            } else {
              console.warn('⚠️ API response indicates no users or failed:', usersResult);
            }
          } else {
            const errorText = await usersResponse.text();
            console.error('❌ Failed to fetch users:', usersResponse.status, errorText);
          }
        } catch (error) {
          console.error('💥 Error fetching users from admin-simple:', error);
          
          // Try alternative endpoint as fallback
          try {
            console.log('🔄 Trying alternative admin endpoint...');
            const altUsersResponse = await fetch(`${API_URL}/api/v1/admin/users`, {
              method: 'GET',
              headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json',
              },
            });

            if (altUsersResponse.ok) {
              const altUsersResult = await altUsersResponse.json();
              console.log('📋 Alternative API Response:', altUsersResult);
              
              if (altUsersResult.success && altUsersResult.data) {
                const mappedUsers = altUsersResult.data.map((user: any) => ({
                  _id: user.id || user._id,
                  name: user.name,
                  email: user.email,
                  mobile: user.mobile,
                  role: user.role,
                  status: user.status,
                  kyc_status: user.kyc_status || 'pending',
                  group_id: user.group_id,
                  group_name: user.group_name,
                  created_at: user.created_at,
                  last_login: user.last_login
                }));
                
                setUsers(mappedUsers);
                console.log('✅ Users loaded from alternative endpoint:', mappedUsers.length);
              }
            }
          } catch (altError) {
            console.error('💥 Alternative endpoint also failed:', altError);
          }
        }

        // Fetch groups data
        try {
          const groupsResponse = await fetch(`${API_URL}/api/v1/admin-groups`, {
            method: 'GET',
            headers: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json',
            },
          });

          if (groupsResponse.ok) {
            const groupsResult = await groupsResponse.json();
            if (groupsResult.success && groupsResult.data) {
              setGroups(groupsResult.data);
            }
          } else {
            console.warn('Groups API not available, using mock data');
            // Use mock data if API fails
            setGroups([
              {
                _id: '1',
                group_name: 'Alpha Trading',
                company_name: 'Alpha Corp',
                group_leader_id: 'leader1',
                group_leader_name: 'John Leader',
                settlement_cycle: 'weekly',
                profit_sharing_percentage: 70,
                active_members: 15,
                total_members: 20,
                total_equity: 50000,
                total_profit: 5000,
                today_profit: 250,
                pending_settlement_amount: 1500,
                next_settlement_date: '2024-01-22',
                trading_status: 'active',
                api_key_status: 'active',
                api_key: 'mt5_api_****',
                created_at: '2024-01-01'
              }
            ]);
          }
        } catch (error) {
          console.error('Error fetching groups:', error);
          // Use mock data on error
          setGroups([
            {
              _id: '1',
              group_name: 'Alpha Trading',
              company_name: 'Alpha Corp',
              group_leader_id: 'leader1',
              group_leader_name: 'John Leader',
              settlement_cycle: 'weekly',
              profit_sharing_percentage: 70,
              active_members: 15,
              total_members: 20,
              total_equity: 50000,
              total_profit: 5000,
              today_profit: 250,
              pending_settlement_amount: 1500,
              next_settlement_date: '2024-01-22',
              trading_status: 'active',
              api_key_status: 'active',
              api_key: 'mt5_api_****',
              created_at: '2024-01-01'
            }
          ]);
        }

        // Fetch accounts data
        try {
          const accountsResponse = await fetch(`${API_URL}/api/v1/trading-accounts`, {
            method: 'GET',
            headers: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json',
            },
          });

          if (accountsResponse.ok) {
            const accountsResult = await accountsResponse.json();
            if (accountsResult.success && accountsResult.data) {
              setAccounts(accountsResult.data.accounts || accountsResult.data);
            }
          } else {
            console.warn('Accounts API not available, using mock data');
            setAccounts([]);
          }
        } catch (error) {
          console.error('Error fetching accounts:', error);
          setAccounts([]);
        }

        // Fetch pending IB proofs
        try {
          console.log('🔄 Fetching IB proofs from API...');
          const ibResponse = await fetch(`${API_URL}/api/v1/admin/ib-proofs/pending`, {
            method: 'GET',
            headers: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json',
            },
          });

          console.log('📡 IB API Response status:', ibResponse.status);

          if (ibResponse.ok) {
            const ibResult = await ibResponse.json();
            console.log('📋 IB API Response data:', ibResult);
            
            if (ibResult.success && ibResult.data && ibResult.data.pending_proofs) {
              // Map the data to match our interface and normalize ib_status typos
              const mappedIBProofs = ibResult.data.pending_proofs.map((proof: any) => ({
                user_id: proof.user_id || proof._id,
                name: proof.name,
                email: proof.email,
                mobile: proof.mobile,
                country: proof.country,
                state: proof.state,
                city: proof.city,
                pin_code: proof.pin_code,
                role: proof.role,
                mobile_verified: proof.mobile_verified,
                email_verified: proof.email_verified,
                broker: proof.broker,
                account_no: proof.account_no,
                ib_proof_filename: proof.ib_proof_filename,
                ib_proof_upload_date: proof.ib_proof_upload_date,
                ib_proof_image_data: proof.ib_proof_image_data,
                // Normalize common misspelling 'plending' to 'pending'
                ib_status: proof.ib_status === 'plending' ? 'pending' : proof.ib_status,
                status: proof.status,
                created_at: proof.created_at
              }));
              
              setPendingIBProofs(mappedIBProofs);
              console.log('✅ IB proofs loaded from database:', mappedIBProofs.length);
            } else {
              console.warn('IB proofs API returned no data, using mock data');
              // Use mock data if API returns no data
              setPendingIBProofs([
                {
                  user_id: '68d28f5c2b67538f048e3c06',
                  name: 'System Test User',
                  email: 'test_1758629724@example.com',
                  mobile: '+919876549724',
                  broker: 'Vantage',
                  account_no: '12345678',
                  ib_proof_filename: 'ib_proof_screenshot.jpg',
                  ib_proof_upload_date: new Date().toISOString(),
                  ib_proof_image_data: '/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwCdABmX/9k=',
                  status: 'pending',
                  created_at: new Date().toISOString()
                }
              ]);
            }
          } else {
            console.warn('IB proofs API not available, using mock data');
            // Use mock data if API fails
            setPendingIBProofs([
              {
                user_id: '68d28f5c2b67538f048e3c06',
                name: 'System Test User',
                email: 'test_1758629724@example.com',
                mobile: '+919876549724',
                broker: 'Vantage',
                account_no: '12345678',
                ib_proof_filename: 'ib_proof_screenshot.jpg',
                ib_proof_upload_date: new Date().toISOString(),
                ib_proof_image_data: '/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwCdABmX/9k=',
                status: 'pending',
                created_at: new Date().toISOString()
              }
            ]);
          }
        } catch (error) {
          console.error('Error fetching IB proofs:', error);
          // Use mock data on error
          setPendingIBProofs([
            {
              user_id: '68d28f5c2b67538f048e3c06',
              name: 'System Test User',
              email: 'test_1758629724@example.com',
              mobile: '+919876549724',
              broker: 'Vantage',
              account_no: '12345678',
              ib_proof_filename: 'ib_proof_screenshot.jpg',
              ib_proof_upload_date: new Date().toISOString(),
              ib_proof_image_data: '/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwCdABmX/9k=',
              status: 'pending',
              created_at: new Date().toISOString()
            }
          ]);
        }

        // Log final results for debugging
        console.log('📊 Data fetch completed. Users loaded:', users.length);
      } catch (error) {
        console.error('Error fetching admin data:', error);
        // Set empty arrays on error to prevent UI crashes
        setUsers([]);
        setGroups([]);
        setAccounts([]);
        setPendingIBProofs([]);
        showNotification('error', 'Failed to load admin data. Some features may not work properly.');
      } finally {
        setLoading(false);
      }
    };

    fetchAdminData();
  }, []);

  const showScreen = (screenId: Screen) => {
    setCurrentScreen(screenId);
  };

  const renderSidebar = () => (
    <div className="sidebar">
      <div className="sidebar-header">
        <h3>Admin Panel</h3>
        <p>EA Trading Platform</p>
      </div>
      <nav className="sidebar-nav">
        <a
          href="#"
          className={`nav-item ${currentScreen === 'user-management' ? 'active' : ''}`}
          onClick={() => showScreen('user-management')}
        >
          <div className="nav-icon">👥</div>
          User Management
        </a>
        <a
          href="#"
          className={`nav-item ${currentScreen === 'ib-approvals' ? 'active' : ''}`}
          onClick={() => showScreen('ib-approvals')}
        >
          <div className="nav-icon">📋</div>
          IB Approvals
        </a>
        <a
          href="#"
          className={`nav-item ${currentScreen === 'group-management' ? 'active' : ''}`}
          onClick={() => showScreen('group-management')}
        >
          <div className="nav-icon">🏢</div>
          Group Management
        </a>
        <a
          href="#"
          className={`nav-item ${currentScreen === 'api-access' ? 'active' : ''}`}
          onClick={() => showScreen('api-access')}
        >
          <div className="nav-icon">🔑</div>
          API Access
        </a>
        <a
          href="#"
          className={`nav-item ${currentScreen === 'master-accounts' ? 'active' : ''}`}
          onClick={() => showScreen('master-accounts')}
        >
          <div className="nav-icon">⭐</div>
          Master Accounts
        </a>
        <a
          href="#"
          className={`nav-item ${currentScreen === 'copy-settings' ? 'active' : ''}`}
          onClick={() => showScreen('copy-settings')}
        >
          <div className="nav-icon">⚙️</div>
          Copy Settings
        </a>
        <a
          href="#"
          className={`nav-item ${currentScreen === 'trade-monitor' ? 'active' : ''}`}
          onClick={() => showScreen('trade-monitor')}
        >
          <div className="nav-icon">📊</div>
          Trade Monitor
        </a>
        <a
          href="#"
          className={`nav-item ${currentScreen === 'reports' ? 'active' : ''}`}
          onClick={() => showScreen('reports')}
        >
          <div className="nav-icon">📈</div>
          Reports & Logs
        </a>
        <a
          href="#"
          className={`nav-item ${currentScreen === 'system-logs' ? 'active' : ''}`}
          onClick={() => showScreen('system-logs')}
        >
          <div className="nav-icon">🔍</div>
          System Logs
        </a>
        <a
          href="#"
          className="nav-item logout-item"
          onClick={(e) => {
            e.preventDefault();
            if (window.confirm('Are you sure you want to logout?')) {
              onLogout();
            }
          }}
        >
          <div className="nav-icon">🚪</div>
          Logout
        </a>
      </nav>
    </div>
  );

  const renderUserManagement = () => (
    <div className="main-content">
      <div className="dashboard-header">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <h1>User Management</h1>
            <p>Manage all users, approvals, and account verification</p>
          </div>
          <button 
            className="btn btn-primary"
            onClick={() => setShowAddUserModal(true)}
          >
            + Add New User
          </button>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr 1fr', gap: '20px', marginBottom: '20px' }}>
        <div className="stat-card">
          <h3>Total Users</h3>
          <div className="value">{users.length}</div>
          <div className="change">All registered users</div>
        </div>
        <div className="stat-card">
          <h3>Active Users</h3>
          <div className="value">{users.filter(u => u.status === 'active').length}</div>
          <div className="change">{users.filter(u => u.status === 'pending').length} pending approval</div>
        </div>
        <div className="stat-card">
          <h3>Group Leaders</h3>
          <div className="value">{users.filter(u => u.role === 'group_leader').length}</div>
          <div className="change">Managing groups</div>
        </div>
        <div className="stat-card">
          <h3>KYC Verified</h3>
          <div className="value">{users.filter(u => u.kyc_status === 'verified').length}</div>
          <div className="change">{users.filter(u => u.kyc_status === 'pending').length} pending</div>
        </div>
      </div>

      {/* Filter Results Summary */}
      {(statusFilter !== 'All Status' || roleFilter !== 'All Roles' || searchTerm !== '') && (
        <div style={{ 
          background: '#f0f9ff', 
          padding: '12px 16px', 
          borderRadius: '8px', 
          border: '1px solid #e0f2fe', 
          marginBottom: '20px',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center'
        }}>
          <div style={{ fontSize: '14px', color: '#0369a1' }}>
            <strong>Filtered Results:</strong> Showing {getFilteredUsers().length} of {users.length} users
            {statusFilter !== 'All Status' && <span> • Status: {statusFilter}</span>}
            {roleFilter !== 'All Roles' && <span> • Role: {roleFilter}</span>}
            {searchTerm !== '' && <span> • Search: "{searchTerm}"</span>}
          </div>
          <button 
            onClick={() => {
              setStatusFilter('All Status');
              setRoleFilter('All Roles');
              setSearchTerm('');
            }}
            style={{
              background: '#3b82f6',
              color: 'white',
              border: 'none',
              padding: '6px 12px',
              borderRadius: '4px',
              fontSize: '12px',
              cursor: 'pointer'
            }}
          >
            Clear Filters
          </button>
        </div>
      )}

      <div className="card">
        <div style={{ padding: '20px', borderBottom: '1px solid #f3f4f6' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <h3>All Users</h3>
            <div style={{ display: 'flex', gap: '10px' }}>
              <button
                onClick={() => setShowTempUserManager(true)}
                className="btn btn-primary btn-sm"
                style={{ backgroundColor: '#10b981', color: 'white', border: 'none', padding: '8px 12px', borderRadius: '6px' }}
              >
                👥 Quick User Manager
              </button>
              <select 
                style={{ padding: '8px 12px', borderRadius: '6px', border: '1px solid #d1d5db' }}
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
              >
                <option>All Status</option>
                <option>Active</option>
                <option>Pending</option>
                <option>Inactive</option>
              </select>
              <select 
                style={{ padding: '8px 12px', borderRadius: '6px', border: '1px solid #d1d5db' }}
                value={roleFilter}
                onChange={(e) => setRoleFilter(e.target.value)}
              >
                <option>All Roles</option>
                <option>Group Leader</option>
                <option>User</option>
                <option>Admin</option>
              </select>
              <input
                type="text"
                placeholder="Search users..."
                style={{ padding: '8px 12px', borderRadius: '6px', border: '1px solid #d1d5db', minWidth: '200px' }}
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>
          </div>
        </div>
        <div style={{ overflowX: 'auto' }}>
          <table className="data-table">
            <thead>
              <tr>
                <th>User</th>
                <th>Email</th>
                <th>Mobile</th>
                <th>Role</th>
                <th>Status</th>
                <th>KYC</th>
                <th>Group</th>
                <th>Joined</th>
                <th>Last Login</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {getFilteredUsers().map((user, index) => (
                <tr key={index}>
                  <td>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                      <div style={{ width: '32px', height: '32px', borderRadius: '50%', background: '#e5e7eb', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '12px', fontWeight: 'bold' }}>
                        {user.name.split(' ').map(n => n[0]).join('').toUpperCase()}
                      </div>
                      <div>
                        <div style={{ fontWeight: 'bold' }}>{user.name}</div>
                      </div>
                    </div>
                  </td>
                  <td>{user.email}</td>
                  <td>{user.mobile}</td>
                  <td>
                    <span className={`status-badge ${user.role === 'group_leader' ? 'status-warning' : 'status-info'}`}>
                      {user.role ? user.role.replace('_', ' ') : 'N/A'}
                    </span>
                  </td>
                  <td>
                    <span className={`status-badge ${user.status === 'active' ? 'status-active' : 'status-pending'}`}>
                      {user.status}
                    </span>
                  </td>
                  <td>
                    <span className={`status-badge ${user.kyc_status === 'verified' ? 'status-active' : 'status-pending'}`}>
                      {user.kyc_status}
                    </span>
                  </td>
                  <td>{user.group_name || 'Not assigned'}</td>
                  <td>{user.created_at ? new Date(user.created_at).toLocaleDateString() : 'N/A'}</td>
                  <td>{user.last_login ? new Date(user.last_login).toLocaleDateString() : 'Never'}</td>
                  <td>
                    <div style={{ display: 'flex', gap: '5px' }}>
                      <button className="btn btn-outline btn-sm" onClick={() => handleEditUser(user)}>Edit</button>
                      {user.status === 'pending' && (
                        <button
                          className="btn btn-primary btn-sm"
                          onClick={() => approveUser(user._id, user.email)}
                          disabled={loading}
                          style={{ opacity: loading ? 0.6 : 1 }}
                        >
                          {loading ? 'Processing...' : 'Approve'}
                        </button>
                      )}
                      {user.status === 'active' && (
                        <button 
                          className="btn btn-outline btn-sm" 
                          style={{ color: '#ef4444', borderColor: '#ef4444' }}
                          onClick={() => {
                            if (confirm(`Are you sure you want to suspend ${user.name}?`)) {
                              suspendUser(user._id, user.email);
                            }
                          }}
                          disabled={loading}
                        >
                          {loading ? 'Processing...' : 'Suspend'}
                        </button>
                      )}
                      {user.status === 'inactive' && (
                        <button 
                          className="btn btn-outline btn-sm" 
                          style={{ color: '#10b981', borderColor: '#10b981' }}
                          onClick={() => {
                            if (confirm(`Are you sure you want to reactivate ${user.name}?`)) {
                              reactivateUser(user._id, user.email);
                            }
                          }}
                          disabled={loading}
                        >
                          {loading ? 'Processing...' : 'Reactivate'}
                        </button>
                      )}
                      {(user.status === 'inactive' || user.status === 'suspended') && (
                        <button
                          className="btn btn-outline btn-sm"
                          style={{ color: '#b91c1c', borderColor: '#b91c1c' }}
                          onClick={() => deleteUser(user._id, user.email)}
                          disabled={loading}
                        >
                          {loading ? 'Processing...' : 'Delete'}
                        </button>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );

  const renderGroupManagement = () => (
    <div className="main-content">
      <div className="dashboard-header">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <h1>Group Management</h1>
            <p>Create and manage trading groups</p>
          </div>
          <button
            className="btn btn-primary"
            onClick={() => {
              const groupName = prompt('Enter group name:');
              const companyName = prompt('Enter company name:');
              if (groupName && companyName) {
                const newGroup: Group = {
                  _id: `grp_${Date.now()}`,
                  group_name: groupName,
                  company_name: companyName,
                  group_leader_id: "admin",
                  group_leader_name: "Admin",
                  settlement_cycle: "monthly",
                  profit_sharing_percentage: 80,
                  active_members: 0,
                  total_members: 0,
                  total_equity: 0,
                  total_profit: 0,
                  today_profit: 0,
                  pending_settlement_amount: 0,
                  next_settlement_date: "",
                  trading_status: "active",
                  api_key_status: "active",
                  api_key: generateApiKey(),
                  created_at: new Date().toISOString()
                };
                setGroups(prev => [...prev, newGroup]);
                alert(`✅ Group created successfully!\n\nGroup: ${groupName}\nAPI Key: ${newGroup.api_key}\n\nAPI key has been automatically generated and is ready for use.`);
              }
            }}
          >
            + Create New Group
          </button>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr 1fr', gap: '20px', marginBottom: '20px' }}>
        <div className="stat-card">
          <h3>Total Groups</h3>
          <div className="value">{groups.length}</div>
          <div className="change">Active trading groups</div>
        </div>
        <div className="stat-card">
          <h3>Total Members</h3>
          <div className="value">{groups.reduce((sum, g) => sum + g.total_members, 0)}</div>
          <div className="change">Across all groups</div>
        </div>
        <div className="stat-card">
          <h3>Total Equity</h3>
          <div className="value">${groups.reduce((sum, g) => sum + g.total_equity, 0).toLocaleString()}</div>
          <div className="change">Combined portfolio</div>
        </div>
        <div className="stat-card">
          <h3>Total Profit</h3>
          <div className="value" style={{ color: '#10b981' }}>
            ${groups.reduce((sum, g) => sum + g.total_profit, 0).toLocaleString()}
          </div>
          <div className="change" style={{ color: '#10b981' }}>
            +${groups.reduce((sum, g) => sum + g.today_profit, 0).toLocaleString()} today
          </div>
        </div>
      </div>

      <div className="card" style={{ marginBottom: '20px' }}>
        <div style={{ padding: '20px', borderBottom: '1px solid #f3f4f6' }}>
          <h3>API Key Management</h3>
        </div>
        <div style={{ padding: '20px' }}>
          <div style={{ background: '#f0f9ff', padding: '15px', borderRadius: '8px', border: '1px solid #e0f2fe', marginBottom: '15px' }}>
            <div style={{ fontSize: '14px', color: '#0369a1', marginBottom: '8px' }}>
              <strong>🔑 Group API Keys</strong>
            </div>
            <div style={{ fontSize: '13px', color: '#0369a1' }}>
              • Each group has a unique API key automatically generated upon creation<br />
              • API keys are used for external system integrations and member joining<br />
              • Keys can be regenerated if compromised (old key becomes invalid)<br />
              • Admin can view and manage all group API keys from this interface
            </div>
          </div>
        </div>
      </div>

      <div className="card">
        <div style={{ padding: '20px', borderBottom: '1px solid #f3f4f6' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <h3>Trading Groups</h3>
            <div style={{ display: 'flex', gap: '10px' }}>
              <select style={{ padding: '8px 12px', borderRadius: '6px', border: '1px solid #d1d5db' }}>
                <option>All Status</option>
                <option>Active</option>
                <option>Paused</option>
                <option>Stopped</option>
              </select>
              <input
                type="text"
                placeholder="Search groups..."
                style={{ padding: '8px 12px', borderRadius: '6px', border: '1px solid #d1d5db', minWidth: '200px' }}
              />
            </div>
          </div>
        </div>
        <div style={{ overflowX: 'auto' }}>
          <table className="data-table">
            <thead>
              <tr>
                <th>Group</th>
                <th>Company</th>
                <th>Leader</th>
                <th>Members</th>
                <th>Equity</th>
                <th>Profit</th>
                <th>Settlement</th>
                <th>Trading Status</th>
                <th>API Status</th>
                <th>API Key</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {groups.map((group, index) => (
                <tr key={index}>
                  <td>
                    <div>
                      <div style={{ fontWeight: 'bold' }}>{group.group_name}</div>
                      <div style={{ fontSize: '12px', color: '#6b7280' }}>
                        {group.settlement_cycle} • {group.profit_sharing_percentage}% sharing
                      </div>
                    </div>
                  </td>
                  <td>{group.company_name}</td>
                  <td>{group.group_leader_name}</td>
                  <td>
                    <div>
                      <div style={{ fontWeight: 'bold' }}>{group.active_members}/{group.total_members}</div>
                      <div style={{ fontSize: '12px', color: '#6b7280' }}>active/total</div>
                    </div>
                  </td>
                  <td>${group.total_equity.toLocaleString()}</td>
                  <td>
                    <div>
                      <div style={{ fontWeight: 'bold', color: '#10b981' }}>+${group.total_profit.toLocaleString()}</div>
                      <div style={{ fontSize: '12px', color: '#10b981' }}>+${group.today_profit.toLocaleString()} today</div>
                    </div>
                  </td>
                  <td>
                    <div>
                      <div style={{ fontWeight: 'bold' }}>${group.pending_settlement_amount.toLocaleString()}</div>
                      <div style={{ fontSize: '12px', color: '#6b7280' }}>
                        Due: {group.next_settlement_date ? new Date(group.next_settlement_date).toLocaleDateString() : 'N/A'}
                      </div>
                    </div>
                  </td>
                  <td>
                    <span className={`status-badge ${group.trading_status === 'active' ? 'status-active' : 'status-warning'}`}>
                      {group.trading_status}
                    </span>
                  </td>
                  <td>
                    <span className={`status-badge ${group.api_key_status === 'active' ? 'status-active' : 'status-error'}`}>
                      {group.api_key_status}
                    </span>
                  </td>
                  <td>
                    <div style={{
                      fontFamily: 'monospace',
                      fontSize: '12px',
                      background: '#f8fafc',
                      padding: '4px 8px',
                      borderRadius: '4px',
                      border: '1px solid #e2e8f0',
                      maxWidth: '200px',
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center'
                    }}>
                      <span style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                        {group.api_key}
                      </span>
                      <button
                        onClick={() => navigator.clipboard.writeText(group.api_key)}
                        style={{
                          padding: '2px 4px',
                          fontSize: '10px',
                          background: '#3b82f6',
                          color: 'white',
                          border: 'none',
                          borderRadius: '2px',
                          cursor: 'pointer',
                          marginLeft: '4px'
                        }}
                        title="Copy API Key"
                      >
                        📋
                      </button>
                    </div>
                  </td>
                  <td>
                    <div style={{ display: 'flex', gap: '5px', flexWrap: 'wrap' }}>
                      <button className="btn btn-outline btn-sm">Edit</button>
                      <button className="btn btn-outline btn-sm">Members</button>
                      <button
                        className="btn btn-outline btn-sm"
                        onClick={() => {
                          if (confirm('Regenerate API key? This will invalidate the current key.')) {
                            const newApiKey = generateApiKey();
                            setGroups(prevGroups =>
                              prevGroups.map(g =>
                                g._id === group._id ? { ...g, api_key: newApiKey } : g
                              )
                            );
                            alert(`New API key generated: ${newApiKey}`);
                          }
                        }}
                        style={{ color: '#f59e0b', borderColor: '#f59e0b' }}
                      >
                        🔄 Regen Key
                      </button>
                      <button className="btn btn-outline btn-sm">Settings</button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );

  const renderAPIAccess = () => (
    <div className="main-content">
      <div className="dashboard-header">
        <h1>API Access Management</h1>
        <p>Manage API keys and access controls for trading groups</p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
        <div className="card">
          <div style={{ padding: '20px', borderBottom: '1px solid #f3f4f6' }}>
            <h3>Generate New API Key</h3>
          </div>
          <div style={{ padding: '20px' }}>
            <div className="form-group">
              <label>Select Group</label>
              <select>
                <option>Select trading group...</option>
                {groups.map((group, index) => (
                  <option key={index} value={group._id}>
                    {group.group_name} - {group.company_name}
                  </option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label>API Key Name</label>
              <input type="text" placeholder="e.g., Production MT5 API" />
            </div>

            <div className="form-group">
              <label>Environment</label>
              <select>
                <option>Demo</option>
                <option>Live</option>
              </select>
            </div>

            <div className="form-group">
              <label>Permissions</label>
              <div style={{ marginTop: '8px' }}>
                <label style={{ display: 'flex', alignItems: 'center', marginBottom: '8px', fontWeight: 'normal' }}>
                  <input type="checkbox" style={{ marginRight: '8px' }} defaultChecked />
                  Read trading data
                </label>
                <label style={{ display: 'flex', alignItems: 'center', marginBottom: '8px', fontWeight: 'normal' }}>
                  <input type="checkbox" style={{ marginRight: '8px' }} defaultChecked />
                  Execute trades
                </label>
                <label style={{ display: 'flex', alignItems: 'center', marginBottom: '8px', fontWeight: 'normal' }}>
                  <input type="checkbox" style={{ marginRight: '8px' }} />
                  Modify positions
                </label>
                <label style={{ display: 'flex', alignItems: 'center', marginBottom: '8px', fontWeight: 'normal' }}>
                  <input type="checkbox" style={{ marginRight: '8px' }} />
                  Access account info
                </label>
              </div>
            </div>

            <button className="btn btn-primary">Generate API Key</button>
          </div>
        </div>

        <div className="card">
          <div style={{ padding: '20px', borderBottom: '1px solid #f3f4f6' }}>
            <h3>API Usage Statistics</h3>
          </div>
          <div style={{ padding: '20px' }}>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '15px', marginBottom: '20px' }}>
              <div style={{ background: '#f8fafc', padding: '15px', borderRadius: '8px' }}>
                <div style={{ fontSize: '12px', color: '#6b7280', marginBottom: '5px' }}>API Calls Today</div>
                <div style={{ fontSize: '24px', fontWeight: 'bold' }}>12,547</div>
              </div>
              <div style={{ background: '#f8fafc', padding: '15px', borderRadius: '8px' }}>
                <div style={{ fontSize: '12px', color: '#6b7280', marginBottom: '5px' }}>Active Keys</div>
                <div style={{ fontSize: '24px', fontWeight: 'bold' }}>8</div>
              </div>
              <div style={{ background: '#f8fafc', padding: '15px', borderRadius: '8px' }}>
                <div style={{ fontSize: '12px', color: '#6b7280', marginBottom: '5px' }}>Error Rate</div>
                <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#ef4444' }}>0.3%</div>
              </div>
              <div style={{ background: '#f8fafc', padding: '15px', borderRadius: '8px' }}>
                <div style={{ fontSize: '12px', color: '#6b7280', marginBottom: '5px' }}>Avg Latency</div>
                <div style={{ fontSize: '24px', fontWeight: 'bold' }}>45ms</div>
              </div>
            </div>

            <div style={{ background: '#f0f9ff', padding: '15px', borderRadius: '8px', border: '1px solid #e0f2fe' }}>
              <h4 style={{ marginBottom: '8px', color: '#0369a1' }}>🔒 Security Settings</h4>
              <div style={{ fontSize: '14px', color: '#0369a1' }}>
                <div style={{ marginBottom: '8px' }}>
                  <strong>IP Whitelist:</strong> Enabled (3 IPs)
                </div>
                <div style={{ marginBottom: '8px' }}>
                  <strong>Rate Limiting:</strong> 1000 calls/hour
                </div>
                <div>
                  <strong>API Version:</strong> v1.2
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="card" style={{ marginTop: '20px' }}>
        <div style={{ padding: '20px', borderBottom: '1px solid #f3f4f6' }}>
          <h3>Active API Keys</h3>
        </div>
        <div style={{ overflowX: 'auto' }}>
          <table className="data-table">
            <thead>
              <tr>
                <th>Key Name</th>
                <th>Group</th>
                <th>Environment</th>
                <th>Permissions</th>
                <th>Last Used</th>
                <th>Calls Today</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>
                  <div>
                    <div style={{ fontWeight: 'bold' }}>Production MT5 API</div>
                    <div style={{ fontSize: '12px', color: '#6b7280', fontFamily: 'monospace' }}>
                      mt5_api_****abcd1234
                    </div>
                  </div>
                </td>
                <td>Professional Traders</td>
                <td>
                  <span className="status-badge status-error">Live</span>
                </td>
                <td>Read, Execute</td>
                <td>2 mins ago</td>
                <td>1,234</td>
                <td>
                  <span className="status-badge status-active">Active</span>
                </td>
                <td>
                  <div style={{ display: 'flex', gap: '5px' }}>
                    <button className="btn btn-outline btn-sm">Edit</button>
                    <button className="btn btn-outline btn-sm">Logs</button>
                    <button className="btn btn-outline btn-sm" style={{ color: '#ef4444', borderColor: '#ef4444' }}>
                      Revoke
                    </button>
                  </div>
                </td>
              </tr>
              <tr>
                <td>
                  <div>
                    <div style={{ fontWeight: 'bold' }}>Demo Testing API</div>
                    <div style={{ fontSize: '12px', color: '#6b7280', fontFamily: 'monospace' }}>
                      mt5_api_****efgh5678
                    </div>
                  </div>
                </td>
                <td>Swing Masters</td>
                <td>
                  <span className="status-badge status-warning">Demo</span>
                </td>
                <td>Read Only</td>
                <td>1 hour ago</td>
                <td>456</td>
                <td>
                  <span className="status-badge status-active">Active</span>
                </td>
                <td>
                  <div style={{ display: 'flex', gap: '5px' }}>
                    <button className="btn btn-outline btn-sm">Edit</button>
                    <button className="btn btn-outline btn-sm">Logs</button>
                    <button className="btn btn-outline btn-sm" style={{ color: '#ef4444', borderColor: '#ef4444' }}>
                      Revoke
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );

  const renderMasterAccounts = () => (
    <div className="main-content">
      <div className="dashboard-header">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <h1>Master Accounts</h1>
            <p>Monitor and manage master trading accounts</p>
          </div>
          <button className="btn btn-primary">+ Add Master Account</button>
        </div>
      </div>

      <div className="card">
        <div style={{ padding: '20px', borderBottom: '1px solid #f3f4f6' }}>
          <h3>Master Account Status</h3>
        </div>
        <div style={{ overflowX: 'auto' }}>
          <table className="data-table">
            <thead>
              <tr>
                <th>Account</th>
                <th>Group</th>
                <th>Broker/Server</th>
                <th>Balance</th>
                <th>Equity</th>
                <th>P&L</th>
                <th>Running Trades</th>
                <th>Latency</th>
                <th>Status</th>
                <th>Last Heartbeat</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {masterAccounts.map((account, index) => (
                <tr key={index}>
                  <td>
                    <div>
                      <div style={{ fontWeight: 'bold' }}>{account.account_name}</div>
                      <div style={{ fontSize: '12px', color: '#6b7280', fontFamily: 'monospace' }}>
                        {account.account_number_masked}
                      </div>
                    </div>
                  </td>
                  <td>{account.group_name}</td>
                  <td>
                    <div>
                      <div style={{ fontWeight: 'bold' }}>{account.broker}</div>
                      <div style={{ fontSize: '12px', color: '#6b7280' }}>{account.server}</div>
                    </div>
                  </td>
                  <td>${account.balance.toLocaleString()}</td>
                  <td>${account.equity.toLocaleString()}</td>
                  <td>
                    <div style={{ color: account.profit >= 0 ? '#10b981' : '#ef4444', fontWeight: 'bold' }}>
                      {account.profit >= 0 ? '+' : ''}${account.profit.toLocaleString()}
                    </div>
                  </td>
                  <td>
                    <div style={{ textAlign: 'center', fontWeight: 'bold' }}>{account.running_trades}</div>
                  </td>
                  <td>
                    <div style={{ color: account.latency_ms < 50 ? '#10b981' : '#ef4444' }}>
                      {account.latency_ms}ms
                    </div>
                  </td>
                  <td>
                    <span className={`status-badge ${account.status === 'active' ? 'status-active' : 'status-error'}`}>
                      {account.status}
                    </span>
                  </td>
                  <td>
                    {account.last_heartbeat ? new Date(account.last_heartbeat).toLocaleString() : 'Never'}
                  </td>
                  <td>
                    <div style={{ display: 'flex', gap: '5px' }}>
                      <button className="btn btn-outline btn-sm">View</button>
                      <button className="btn btn-outline btn-sm">Edit</button>
                      <button className="btn btn-outline btn-sm">Logs</button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px', marginTop: '20px' }}>
        <div className="card">
          <div style={{ padding: '20px', borderBottom: '1px solid #f3f4f6' }}>
            <h3>Performance Overview</h3>
          </div>
          <div style={{ padding: '20px' }}>
            <div style={{ marginBottom: '20px' }}>
              <div style={{ fontSize: '12px', color: '#6b7280', marginBottom: '5px' }}>Total Equity</div>
              <div style={{ fontSize: '24px', fontWeight: 'bold' }}>
                ${masterAccounts.reduce((sum, acc) => sum + acc.equity, 0).toLocaleString()}
              </div>
            </div>

            <div style={{ marginBottom: '20px' }}>
              <div style={{ fontSize: '12px', color: '#6b7280', marginBottom: '5px' }}>Total P&L</div>
              <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#10b981' }}>
                +${masterAccounts.reduce((sum, acc) => sum + acc.profit, 0).toLocaleString()}
              </div>
            </div>

            <div style={{ marginBottom: '20px' }}>
              <div style={{ fontSize: '12px', color: '#6b7280', marginBottom: '5px' }}>Active Trades</div>
              <div style={{ fontSize: '24px', fontWeight: 'bold' }}>
                {masterAccounts.reduce((sum, acc) => sum + acc.running_trades, 0)}
              </div>
            </div>

            <div>
              <div style={{ fontSize: '12px', color: '#6b7280', marginBottom: '5px' }}>Avg Latency</div>
              <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#10b981' }}>
                {(masterAccounts.reduce((sum, acc) => sum + acc.latency_ms, 0) / masterAccounts.length).toFixed(1)}ms
              </div>
            </div>
          </div>
        </div>

        <div className="card">
          <div style={{ padding: '20px', borderBottom: '1px solid #f3f4f6' }}>
            <h3>Health Monitoring</h3>
          </div>
          <div style={{ padding: '20px' }}>
            <div style={{ background: '#f0f9ff', padding: '15px', borderRadius: '8px', border: '1px solid #e0f2fe', marginBottom: '15px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div>
                  <h4 style={{ color: '#0369a1', marginBottom: '5px' }}>🟢 All Systems Operational</h4>
                  <div style={{ fontSize: '14px', color: '#0369a1' }}>
                    All master accounts are connected and functioning normally
                  </div>
                </div>
              </div>
            </div>

            <div style={{ marginBottom: '15px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                <span style={{ fontSize: '14px' }}>Connection Status</span>
                <span style={{ fontSize: '14px', fontWeight: 'bold', color: '#10b981' }}>100%</span>
              </div>
              <div style={{ width: '100%', height: '8px', background: '#f3f4f6', borderRadius: '4px' }}>
                <div style={{ width: '100%', height: '100%', background: '#10b981', borderRadius: '4px' }}></div>
              </div>
            </div>

            <div style={{ marginBottom: '15px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                <span style={{ fontSize: '14px' }}>API Response Time</span>
                <span style={{ fontSize: '14px', fontWeight: 'bold', color: '#10b981' }}>Excellent</span>
              </div>
              <div style={{ width: '100%', height: '8px', background: '#f3f4f6', borderRadius: '4px' }}>
                <div style={{ width: '95%', height: '100%', background: '#10b981', borderRadius: '4px' }}></div>
              </div>
            </div>

            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                <span style={{ fontSize: '14px' }}>Trade Execution</span>
                <span style={{ fontSize: '14px', fontWeight: 'bold', color: '#10b981' }}>98.7%</span>
              </div>
              <div style={{ width: '100%', height: '8px', background: '#f3f4f6', borderRadius: '4px' }}>
                <div style={{ width: '98%', height: '100%', background: '#10b981', borderRadius: '4px' }}></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  const renderCopySettings = () => (
    <div className="main-content">
      <div className="dashboard-header">
        <h1>EA Settings & Symbol Mapping</h1>
        <p>Configure global EA trading settings and symbol mappings</p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
        <div className="card">
          <div style={{ padding: '20px', borderBottom: '1px solid #f3f4f6' }}>
            <h3>Global Copy Settings</h3>
          </div>
          <div style={{ padding: '20px' }}>
            <div className="form-group">
              <label>Default Lot Multiplier</label>
              <select>
                <option>1.0 (100%)</option>
                <option>0.5 (50%)</option>
                <option>0.1 (10%)</option>
                <option>2.0 (200%)</option>
              </select>
            </div>

            <div className="form-group">
              <label>Maximum Slippage (pips)</label>
              <input type="number" defaultValue="3" min="0" max="20" />
            </div>

            <div className="form-group">
              <label>Copy Timeout (seconds)</label>
              <input type="number" defaultValue="30" min="5" max="300" />
            </div>

            <div className="form-group">
              <label>Risk Management</label>
              <div style={{ marginTop: '8px' }}>
                <label style={{ display: 'flex', alignItems: 'center', marginBottom: '8px', fontWeight: 'normal' }}>
                  <input type="checkbox" style={{ marginRight: '8px' }} defaultChecked />
                  Enable global stop loss copying
                </label>
                <label style={{ display: 'flex', alignItems: 'center', marginBottom: '8px', fontWeight: 'normal' }}>
                  <input type="checkbox" style={{ marginRight: '8px' }} defaultChecked />
                  Enable global take profit copying
                </label>
                <label style={{ display: 'flex', alignItems: 'center', marginBottom: '8px', fontWeight: 'normal' }}>
                  <input type="checkbox" style={{ marginRight: '8px' }} />
                  Auto-pause on high drawdown
                </label>
                <label style={{ display: 'flex', alignItems: 'center', marginBottom: '8px', fontWeight: 'normal' }}>
                  <input type="checkbox" style={{ marginRight: '8px' }} defaultChecked />
                  Reject trades during news events
                </label>
              </div>
            </div>

            <button className="btn btn-primary">Save Global Settings</button>
          </div>
        </div>

        <div className="card">
          <div style={{ padding: '20px', borderBottom: '1px solid #f3f4f6' }}>
            <h3>Add Symbol Mapping</h3>
          </div>
          <div style={{ padding: '20px' }}>
            <div className="form-group">
              <label>Master Symbol</label>
              <input type="text" placeholder="e.g., XAUUSD" />
            </div>

            <div className="form-group">
              <label>Slave Symbol</label>
              <input type="text" placeholder="e.g., GOLD, XAUUSD.sc" />
            </div>

            <div className="form-group">
              <label>Volume Multiplier</label>
              <input type="number" step="0.1" defaultValue="1.0" min="0.1" max="10" />
            </div>

            <div className="form-group">
              <label>Broker(s)</label>
              <select>
                <option>All Brokers</option>
                <option>Exness</option>
                <option>Vantage</option>
                <option>XM</option>
                <option>IC Markets</option>
              </select>
            </div>

            <div className="form-group">
              <label>Active</label>
              <label style={{ display: 'flex', alignItems: 'center', fontWeight: 'normal' }}>
                <input type="checkbox" style={{ marginRight: '8px' }} defaultChecked />
                Enable this mapping
              </label>
            </div>

            <button className="btn btn-primary">Add Mapping</button>
          </div>
        </div>
      </div>

      <div className="card" style={{ marginTop: '20px' }}>
        <div style={{ padding: '20px', borderBottom: '1px solid #f3f4f6' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <h3>Symbol Mappings</h3>
            <div style={{ display: 'flex', gap: '10px' }}>
              <select style={{ padding: '8px 12px', borderRadius: '6px', border: '1px solid #d1d5db' }}>
                <option>All Brokers</option>
                <option>Exness</option>
                <option>Vantage</option>
                <option>XM</option>
              </select>
              <input
                type="text"
                placeholder="Search symbols..."
                style={{ padding: '8px 12px', borderRadius: '6px', border: '1px solid #d1d5db', minWidth: '200px' }}
              />
            </div>
          </div>
        </div>
        <div style={{ overflowX: 'auto' }}>
          <table className="data-table">
            <thead>
              <tr>
                <th>Master Symbol</th>
                <th>Slave Symbol</th>
                <th>Volume Multiplier</th>
                <th>Broker</th>
                <th>Usage Count</th>
                <th>Status</th>
                <th>Created</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td style={{ fontFamily: 'monospace', fontWeight: 'bold' }}>XAUUSD</td>
                <td style={{ fontFamily: 'monospace', fontWeight: 'bold' }}>GOLD</td>
                <td>1.0x</td>
                <td>Exness</td>
                <td>24</td>
                <td><span className="status-badge status-active">Active</span></td>
                <td>2025-09-01</td>
                <td>
                  <div style={{ display: 'flex', gap: '5px' }}>
                    <button className="btn btn-outline btn-sm">Edit</button>
                    <button className="btn btn-outline btn-sm">Test</button>
                    <button className="btn btn-outline btn-sm" style={{ color: '#ef4444', borderColor: '#ef4444' }}>
                      Delete
                    </button>
                  </div>
                </td>
              </tr>
              <tr>
                <td style={{ fontFamily: 'monospace', fontWeight: 'bold' }}>BTCUSD</td>
                <td style={{ fontFamily: 'monospace', fontWeight: 'bold' }}>BITCOIN</td>
                <td>0.1x</td>
                <td>Vantage</td>
                <td>15</td>
                <td><span className="status-badge status-active">Active</span></td>
                <td>2025-09-05</td>
                <td>
                  <div style={{ display: 'flex', gap: '5px' }}>
                    <button className="btn btn-outline btn-sm">Edit</button>
                    <button className="btn btn-outline btn-sm">Test</button>
                    <button className="btn btn-outline btn-sm" style={{ color: '#ef4444', borderColor: '#ef4444' }}>
                      Delete
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );

  const renderTradeMonitor = () => (
    <div className="main-content">
      <div className="dashboard-header">
        <h1>Real-Time Trade Monitor</h1>
        <p>Monitor live trading activity and copy operations</p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr 1fr', gap: '20px', marginBottom: '20px' }}>
        <div className="stat-card">
          <h3>Active Trades</h3>
          <div className="value">127</div>
          <div className="change">Across all accounts</div>
        </div>
        <div className="stat-card">
          <h3>Trades Today</h3>
          <div className="value">1,234</div>
          <div className="change">+89 in last hour</div>
        </div>
        <div className="stat-card">
          <h3>Copy Success Rate</h3>
          <div className="value" style={{ color: '#10b981' }}>98.7%</div>
          <div className="change">Last 24 hours</div>
        </div>
        <div className="stat-card">
          <h3>Avg Copy Time</h3>
          <div className="value">247ms</div>
          <div className="change">Master to slave</div>
        </div>
      </div>

      <div className="card">
        <div style={{ padding: '20px', borderBottom: '1px solid #f3f4f6' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <h3>Live Trading Activity</h3>
            <div style={{ display: 'flex', gap: '10px' }}>
              <select style={{ padding: '8px 12px', borderRadius: '6px', border: '1px solid #d1d5db' }}>
                <option>All Groups</option>
                <option>Professional Traders</option>
                <option>Swing Masters</option>
              </select>
              <select style={{ padding: '8px 12px', borderRadius: '6px', border: '1px solid #d1d5db' }}>
                <option>All Status</option>
                <option>Open</option>
                <option>Closed</option>
                <option>Failed</option>
              </select>
              <button className="btn btn-outline">🔄 Auto Refresh</button>
            </div>
          </div>
        </div>
        <div style={{ overflowX: 'auto' }}>
          <table className="data-table">
            <thead>
              <tr>
                <th>Time</th>
                <th>Group</th>
                <th>Master Order</th>
                <th>Symbol</th>
                <th>Type</th>
                <th>Volume</th>
                <th>Price</th>
                <th>Copies</th>
                <th>Success Rate</th>
                <th>Avg Copy Time</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>14:35:22</td>
                <td>Professional Traders</td>
                <td style={{ fontFamily: 'monospace' }}>#12345678</td>
                <td style={{ fontFamily: 'monospace', fontWeight: 'bold' }}>EURUSD</td>
                <td><span className="status-badge status-info">BUY</span></td>
                <td>0.50</td>
                <td>1.0850</td>
                <td>24/25</td>
                <td style={{ color: '#10b981' }}>96%</td>
                <td>230ms</td>
                <td><span className="status-badge status-active">Copied</span></td>
              </tr>
              <tr>
                <td>14:33:15</td>
                <td>Swing Masters</td>
                <td style={{ fontFamily: 'monospace' }}>#12345679</td>
                <td style={{ fontFamily: 'monospace', fontWeight: 'bold' }}>XAUUSD</td>
                <td><span className="status-badge status-error">SELL</span></td>
                <td>0.10</td>
                <td>2051.25</td>
                <td>17/18</td>
                <td style={{ color: '#10b981' }}>94%</td>
                <td>280ms</td>
                <td><span className="status-badge status-active">Copied</span></td>
              </tr>
              <tr>
                <td>14:31:08</td>
                <td>Professional Traders</td>
                <td style={{ fontFamily: 'monospace' }}>#12345680</td>
                <td style={{ fontFamily: 'monospace', fontWeight: 'bold' }}>GBPUSD</td>
                <td><span className="status-badge status-info">BUY</span></td>
                <td>0.30</td>
                <td>1.2675</td>
                <td>22/25</td>
                <td style={{ color: '#ef4444' }}>88%</td>
                <td>450ms</td>
                <td><span className="status-badge status-warning">Partial</span></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px', marginTop: '20px' }}>
        <div className="card">
          <div style={{ padding: '20px', borderBottom: '1px solid #f3f4f6' }}>
            <h3>Failed Copy Attempts</h3>
          </div>
          <div style={{ padding: '20px' }}>
            <div style={{ marginBottom: '15px', padding: '12px', background: '#fef2f2', borderRadius: '8px', border: '1px solid #fecaca' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <div>
                  <div style={{ fontWeight: 'bold', color: '#dc2626' }}>EURUSD Trade Failed</div>
                  <div style={{ fontSize: '12px', color: '#7f1d1d', marginTop: '2px' }}>
                    Account: Vantage ****1234 • Volume: 0.1 • Error: Insufficient margin
                  </div>
                  <div style={{ fontSize: '12px', color: '#7f1d1d' }}>
                    14:32:45 • Retry #2 scheduled in 30s
                  </div>
                </div>
                <button className="btn btn-outline btn-sm" style={{ color: '#dc2626', borderColor: '#dc2626' }}>
                  Retry Now
                </button>
              </div>
            </div>

            <div style={{ marginBottom: '15px', padding: '12px', background: '#fef2f2', borderRadius: '8px', border: '1px solid #fecaca' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <div>
                  <div style={{ fontWeight: 'bold', color: '#dc2626' }}>XAUUSD Trade Failed</div>
                  <div style={{ fontSize: '12px', color: '#7f1d1d', marginTop: '2px' }}>
                    Account: Exness ****5678 • Volume: 0.05 • Error: Symbol not found
                  </div>
                  <div style={{ fontSize: '12px', color: '#7f1d1d' }}>
                    14:30:12 • Max retries reached
                  </div>
                </div>
                <button className="btn btn-outline btn-sm" style={{ color: '#dc2626', borderColor: '#dc2626' }}>
                  Investigate
                </button>
              </div>
            </div>
          </div>
        </div>

        <div className="card">
          <div style={{ padding: '20px', borderBottom: '1px solid #f3f4f6' }}>
            <h3>System Health</h3>
          </div>
          <div style={{ padding: '20px' }}>
            <div style={{ marginBottom: '15px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                <span style={{ fontSize: '14px' }}>Trading Engine</span>
                <span style={{ fontSize: '14px', fontWeight: 'bold', color: '#10b981' }}>🟢 Online</span>
              </div>
              <div style={{ fontSize: '12px', color: '#6b7280' }}>Last heartbeat: 2 seconds ago</div>
            </div>

            <div style={{ marginBottom: '15px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                <span style={{ fontSize: '14px' }}>Copy Service</span>
                <span style={{ fontSize: '14px', fontWeight: 'bold', color: '#10b981' }}>🟢 Active</span>
              </div>
              <div style={{ fontSize: '12px', color: '#6b7280' }}>Processing queue: 3 pending</div>
            </div>

            <div style={{ marginBottom: '15px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                <span style={{ fontSize: '14px' }}>Database</span>
                <span style={{ fontSize: '14px', fontWeight: 'bold', color: '#10b981' }}>🟢 Connected</span>
              </div>
              <div style={{ fontSize: '12px', color: '#6b7280' }}>Response time: 15ms</div>
            </div>

            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                <span style={{ fontSize: '14px' }}>Broker APIs</span>
                <span style={{ fontSize: '14px', fontWeight: 'bold', color: '#f59e0b' }}>🟡 Partial</span>
              </div>
              <div style={{ fontSize: '12px', color: '#6b7280' }}>2/3 brokers online • XM maintenance</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  const renderReports = () => (
    <div className="main-content">
      <div className="dashboard-header">
        <h1>Reports & Analytics</h1>
        <p>Comprehensive reporting and analytics dashboard</p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr 1fr', gap: '20px', marginBottom: '20px' }}>
        <div className="stat-card">
          <h3>Total Users</h3>
          <div className="value">{users.length}</div>
          <div className="change">+{users.filter(u => u.created_at && new Date(u.created_at) > new Date(Date.now() - 7*24*60*60*1000)).length} this week</div>
        </div>
        <div className="stat-card">
          <h3>Platform Revenue</h3>
          <div className="value">$45,230</div>
          <div className="change" style={{ color: '#10b981' }}>+12.3% this month</div>
        </div>
        <div className="stat-card">
          <h3>Total Settlements</h3>
          <div className="value">$127,540</div>
          <div className="change">Paid to members</div>
        </div>
        <div className="stat-card">
          <h3>System Uptime</h3>
          <div className="value" style={{ color: '#10b981' }}>99.8%</div>
          <div className="change">Last 30 days</div>
        </div>
      </div>

      <div className="card" style={{ marginBottom: '20px' }}>
        <div style={{ padding: '20px', borderBottom: '1px solid #f3f4f6' }}>
          <h3>Settlement Reports</h3>
        </div>
        <div style={{ overflowX: 'auto' }}>
          <table className="data-table">
            <thead>
              <tr>
                <th>Period</th>
                <th>Group</th>
                <th>Total Profit</th>
                <th>Member Share (%)</th>
                <th>Amount Due</th>
                <th>Amount Paid</th>
                <th>Status</th>
                <th>Due Date</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {settlements.map((settlement, index) => (
                <tr key={index}>
                  <td>
                    {new Date(settlement.period_start).toLocaleDateString()} - {new Date(settlement.period_end).toLocaleDateString()}
                  </td>
                  <td>{settlement.group_name}</td>
                  <td>${settlement.total_profit.toLocaleString()}</td>
                  <td>{settlement.profit_sharing_percentage}%</td>
                  <td>${settlement.amount_due.toLocaleString()}</td>
                  <td>${settlement.amount_paid.toLocaleString()}</td>
                  <td>
                    <span className={`status-badge ${settlement.status === 'paid' ? 'status-active' : 'status-pending'}`}>
                      {settlement.status}
                    </span>
                  </td>
                  <td>{new Date(settlement.settlement_date).toLocaleDateString()}</td>
                  <td>
                    <div style={{ display: 'flex', gap: '5px' }}>
                      <button className="btn btn-outline btn-sm">View</button>
                      <button className="btn btn-outline btn-sm">Download</button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
        <div className="card">
          <div style={{ padding: '20px', borderBottom: '1px solid #f3f4f6' }}>
            <h3>Group Performance</h3>
          </div>
          <div style={{ padding: '20px' }}>
            {groups.map((group, index) => (
              <div key={index} style={{ marginBottom: '15px', paddingBottom: '15px', borderBottom: index < groups.length - 1 ? '1px solid #f3f4f6' : 'none' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                  <span style={{ fontWeight: 'bold' }}>{group.group_name}</span>
                  <span style={{ color: '#10b981', fontWeight: 'bold' }}>
                    +${group.total_profit.toLocaleString()}
                  </span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px', color: '#6b7280' }}>
                  <span>{group.active_members} members • ${group.total_equity.toLocaleString()} equity</span>
                  <span style={{ color: '#10b981' }}>
                    +${group.today_profit.toLocaleString()} today
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="card">
          <div style={{ padding: '20px', borderBottom: '1px solid #f3f4f6' }}>
            <h3>Revenue Breakdown</h3>
          </div>
          <div style={{ padding: '20px' }}>
            <div style={{ marginBottom: '20px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                <span style={{ fontSize: '14px' }}>Profit Sharing (20%)</span>
                <span style={{ fontSize: '14px', fontWeight: 'bold' }}>$25,460</span>
              </div>
              <div style={{ width: '100%', height: '8px', background: '#f3f4f6', borderRadius: '4px' }}>
                <div style={{ width: '60%', height: '100%', background: '#3b82f6', borderRadius: '4px' }}></div>
              </div>
            </div>

            <div style={{ marginBottom: '20px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                <span style={{ fontSize: '14px' }}>Setup Fees</span>
                <span style={{ fontSize: '14px', fontWeight: 'bold' }}>$12,300</span>
              </div>
              <div style={{ width: '100%', height: '8px', background: '#f3f4f6', borderRadius: '4px' }}>
                <div style={{ width: '30%', height: '100%', background: '#10b981', borderRadius: '4px' }}></div>
              </div>
            </div>

            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                <span style={{ fontSize: '14px' }}>Management Fees</span>
                <span style={{ fontSize: '14px', fontWeight: 'bold' }}>$7,470</span>
              </div>
              <div style={{ width: '100%', height: '8px', background: '#f3f4f6', borderRadius: '4px' }}>
                <div style={{ width: '18%', height: '100%', background: '#f59e0b', borderRadius: '4px' }}></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  const renderSystemLogs = () => (
    <div className="main-content">
      <div className="dashboard-header">
        <h1>System Logs & Error Tracking</h1>
        <p>Monitor system health and track errors</p>
      </div>

      <div className="card" style={{ marginBottom: '20px' }}>
        <div style={{ padding: '20px', borderBottom: '1px solid #f3f4f6' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <h3>Error Logs</h3>
            <div style={{ display: 'flex', gap: '10px' }}>
              <select style={{ padding: '8px 12px', borderRadius: '6px', border: '1px solid #d1d5db' }}>
                <option>All Error Types</option>
                <option>Trade Copy Errors</option>
                <option>API Errors</option>
                <option>Connection Errors</option>
                <option>System Errors</option>
              </select>
              <select style={{ padding: '8px 12px', borderRadius: '6px', border: '1px solid #d1d5db' }}>
                <option>All Status</option>
                <option>Unresolved</option>
                <option>Resolved</option>
              </select>
              <input
                type="text"
                placeholder="Search error messages..."
                style={{ padding: '8px 12px', borderRadius: '6px', border: '1px solid #d1d5db', minWidth: '200px' }}
              />
            </div>
          </div>
        </div>
        <div style={{ overflowX: 'auto' }}>
          <table className="data-table">
            <thead>
              <tr>
                <th>Timestamp</th>
                <th>Error Code</th>
                <th>Message</th>
                <th>Group</th>
                <th>Account</th>
                <th>Symbol</th>
                <th>Retry Count</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {errorLogs.map((error, index) => (
                <tr key={index}>
                  <td>{new Date(error.created_at).toLocaleString()}</td>
                  <td>
                    <span style={{ fontFamily: 'monospace', background: '#f3f4f6', padding: '2px 6px', borderRadius: '4px' }}>
                      {error.error_code}
                    </span>
                  </td>
                  <td style={{ maxWidth: '300px' }}>
                    <div style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }} title={error.error_message}>
                      {error.error_message}
                    </div>
                  </td>
                  <td>{error.group_name || 'N/A'}</td>
                  <td style={{ fontFamily: 'monospace' }}>{error.account_id ? `***${error.account_id.slice(-4)}` : 'N/A'}</td>
                  <td style={{ fontFamily: 'monospace', fontWeight: 'bold' }}>{error.symbol || 'N/A'}</td>
                  <td style={{ textAlign: 'center' }}>{error.retry_count}</td>
                  <td>
                    <span className={`status-badge ${error.resolved ? 'status-active' : 'status-error'}`}>
                      {error.resolved ? 'Resolved' : 'Open'}
                    </span>
                  </td>
                  <td>
                    <div style={{ display: 'flex', gap: '5px' }}>
                      <button className="btn btn-outline btn-sm">View</button>
                      {!error.resolved && (
                        <button className="btn btn-outline btn-sm">Resolve</button>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
        <div className="card">
          <div style={{ padding: '20px', borderBottom: '1px solid #f3f4f6' }}>
            <h3>Error Statistics</h3>
          </div>
          <div style={{ padding: '20px' }}>
            <div style={{ marginBottom: '20px' }}>
              <div style={{ fontSize: '12px', color: '#6b7280', marginBottom: '5px' }}>Total Errors (24h)</div>
              <div style={{ fontSize: '24px', fontWeight: 'bold' }}>{errorLogs.length}</div>
            </div>

            <div style={{ marginBottom: '20px' }}>
              <div style={{ fontSize: '12px', color: '#6b7280', marginBottom: '5px' }}>Unresolved</div>
              <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#ef4444' }}>
                {errorLogs.filter(e => !e.resolved).length}
              </div>
            </div>

            <div style={{ marginBottom: '20px' }}>
              <div style={{ fontSize: '12px', color: '#6b7280', marginBottom: '5px' }}>Resolution Rate</div>
              <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#10b981' }}>
                {errorLogs.length > 0 ? Math.round((errorLogs.filter(e => e.resolved).length / errorLogs.length) * 100) : 0}%
              </div>
            </div>

            <div>
              <div style={{ fontSize: '12px', color: '#6b7280', marginBottom: '5px' }}>Avg Resolution Time</div>
              <div style={{ fontSize: '24px', fontWeight: 'bold' }}>2.3h</div>
            </div>
          </div>
        </div>

        <div className="card">
          <div style={{ padding: '20px', borderBottom: '1px solid #f3f4f6' }}>
            <h3>System Alerts</h3>
          </div>
          <div style={{ padding: '20px' }}>
            <div style={{ background: '#fef2f2', padding: '15px', borderRadius: '8px', border: '1px solid #fecaca', marginBottom: '15px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <div>
                  <div style={{ fontWeight: 'bold', color: '#dc2626' }}>🚨 High Error Rate Detected</div>
                  <div style={{ fontSize: '12px', color: '#7f1d1d', marginTop: '2px' }}>
                    Professional Traders group experiencing 15% copy failure rate
                  </div>
                  <div style={{ fontSize: '12px', color: '#7f1d1d' }}>
                    Started: 14:20 • Duration: 25 minutes
                  </div>
                </div>
                <button className="btn btn-outline btn-sm" style={{ color: '#dc2626', borderColor: '#dc2626' }}>
                  Investigate
                </button>
              </div>
            </div>

            <div style={{ background: '#fef3c7', padding: '15px', borderRadius: '8px', border: '1px solid #fbbf24', marginBottom: '15px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <div>
                  <div style={{ fontWeight: 'bold', color: '#92400e' }}>⚠️ Broker API Latency</div>
                  <div style={{ fontSize: '12px', color: '#78350f', marginTop: '2px' }}>
                    XM API response time above threshold (&gt;500ms)
                  </div>
                  <div style={{ fontSize: '12px', color: '#78350f' }}>
                    Started: 13:45 • Current: 650ms avg
                  </div>
                </div>
                <button className="btn btn-outline btn-sm" style={{ color: '#92400e', borderColor: '#92400e' }}>
                  Monitor
                </button>
              </div>
            </div>

            <div style={{ background: '#dcfce7', padding: '15px', borderRadius: '8px', border: '1px solid #bbf7d0' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <div>
                  <div style={{ fontWeight: 'bold', color: '#166534' }}>✅ System Backup Complete</div>
                  <div style={{ fontSize: '12px', color: '#14532d', marginTop: '2px' }}>
                    Daily database backup completed successfully
                  </div>
                  <div style={{ fontSize: '12px', color: '#14532d' }}>
                    Completed: 12:00 • Size: 2.4GB • Duration: 15min
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  const renderIBApprovals = () => (
    <div className="main-content">
      <div className="dashboard-header">
        <h1>IB Proof Approvals</h1>
        <p>Review and approve IB change proofs submitted by users</p>
      </div>

      <div className="card">
        <div style={{ padding: '20px', borderBottom: '1px solid #f3f4f6' }}>
          <h3>Pending IB Proofs ({pendingIBProofs.length})</h3>
        </div>
        <div style={{ overflowX: 'auto' }}>
          <table className="data-table">
            <thead>
              <tr>
                <th>User Details</th>
                <th>Contact Info</th>
                <th>Location</th>
                <th>Broker & Account</th>
                <th>IB Proof</th>
                <th>Upload Date</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {pendingIBProofs.map((proof) => (
                <tr key={proof.user_id}>
                  <td>
                    <div>
                      <div style={{ fontWeight: 'bold', fontSize: '14px' }}>{proof.name}</div>
                      <div style={{ fontSize: '12px', color: '#6b7280', marginTop: '2px' }}>
                        ID: {proof.user_id}
                      </div>
                      <div style={{ fontSize: '11px', color: '#9ca3af', marginTop: '2px' }}>
                        Role: {proof.role || 'user'}
                      </div>
                    </div>
                  </td>
                  <td>
                    <div style={{ fontSize: '13px' }}>
                      <div style={{ fontWeight: '500' }}>{proof.email}</div>
                      <div style={{ color: '#6b7280', fontSize: '12px', marginTop: '2px' }}>
                        📱 {proof.mobile}
                      </div>
                      <div style={{ fontSize: '11px', color: '#9ca3af', marginTop: '2px' }}>
                        Verified: {proof.mobile_verified ? '✅ Mobile' : '❌ Mobile'} | {proof.email_verified ? '✅ Email' : '❌ Email'}
                      </div>
                    </div>
                  </td>
                  <td>
                    <div style={{ fontSize: '12px' }}>
                      <div style={{ fontWeight: '500' }}>{proof.country || 'N/A'}</div>
                      <div style={{ color: '#6b7280', fontSize: '11px' }}>
                        {proof.state || 'N/A'}, {proof.city || 'N/A'}
                      </div>
                      <div style={{ color: '#9ca3af', fontSize: '10px' }}>
                        PIN: {proof.pin_code || 'N/A'}
                      </div>
                    </div>
                  </td>
                  <td>
                    <div>
                      <span className="status-badge" style={{ backgroundColor: '#3b82f6', color: 'white', fontSize: '11px' }}>
                        {proof.broker || 'N/A'}
                      </span>
                      <div style={{ fontFamily: 'monospace', fontSize: '12px', marginTop: '4px' }}>
                        Account: {proof.account_no || 'N/A'}
                      </div>
                      <div style={{ fontSize: '10px', color: '#9ca3af', marginTop: '2px' }}>
                        Trading Account
                      </div>
                    </div>
                  </td>
                  <td>
                    <div>
                      <div style={{ fontSize: '12px', fontWeight: 'bold', marginBottom: '4px' }}>
                        {proof.ib_proof_filename || 'IB Proof Image'}
                      </div>
                      <button
                        className="btn btn-outline btn-sm"
                        style={{ fontSize: '10px', padding: '4px 8px' }}
                        onClick={() => viewProofImage(proof.ib_proof_image_data)}
                      >
                        🔍 View Proof
                      </button>
                      <div style={{ fontSize: '10px', color: '#9ca3af', marginTop: '2px' }}>
                        Click to view full image
                      </div>
                    </div>
                  </td>
                  <td>
                    <div style={{ fontSize: '12px' }}>
                      <div style={{ fontWeight: '500' }}>
                        {proof.ib_proof_upload_date ? new Date(proof.ib_proof_upload_date).toLocaleDateString() : 'N/A'}
                      </div>
                      <div style={{ color: '#6b7280', fontSize: '11px' }}>
                        {proof.ib_proof_upload_date ? new Date(proof.ib_proof_upload_date).toLocaleTimeString() : 'N/A'}
                      </div>
                      <div style={{ fontSize: '10px', color: '#9ca3af' }}>
                        Upload Time
                      </div>
                    </div>
                  </td>
                  <td>
                    <div>
                      <span className="status-badge" style={{ backgroundColor: '#f59e0b', color: 'white', fontSize: '11px' }}>
                        Pending Review
                      </span>
                      <div style={{ fontSize: '10px', color: '#9ca3af', marginTop: '2px' }}>
                        IB Status: {proof.ib_status || 'pending'}
                      </div>
                    </div>
                  </td>
                  <td>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                      <button
                        className="btn btn-sm"
                        style={{
                          backgroundColor: loading ? '#9ca3af' : '#10b981',
                          color: 'white',
                          fontSize: '10px',
                          padding: '4px 8px',
                          opacity: loading ? 0.6 : 1
                        }}
                        onClick={() => approveIBProof(proof.user_id, proof.name)}
                        disabled={loading}
                      >
                        {loading ? '...' : '✓ Approve'}
                      </button>
                      <button
                        className="btn btn-sm"
                        style={{
                          backgroundColor: loading ? '#9ca3af' : '#ef4444',
                          color: 'white',
                          fontSize: '10px',
                          padding: '4px 8px',
                          opacity: loading ? 0.6 : 1
                        }}
                        onClick={() => {
                          const reason = prompt('Enter rejection reason:');
                          if (reason) {
                            rejectIBProof(proof.user_id, proof.name, reason);
                          }
                        }}
                        disabled={loading}
                      >
                        {loading ? '...' : '✗ Reject'}
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {pendingIBProofs.length === 0 && (
            <div style={{ textAlign: 'center', padding: '40px', color: '#6b7280' }}>
              <div style={{ fontSize: '48px', marginBottom: '15px' }}>📋</div>
              <div style={{ fontSize: '18px', fontWeight: 'bold', marginBottom: '8px' }}>
                No Pending IB Proofs
              </div>
              <div>All IB proofs have been reviewed and processed.</div>
            </div>
          )}
        </div>
      </div>

      <div className="card" style={{ marginTop: '20px' }}>
        <div style={{ padding: '20px', borderBottom: '1px solid #f3f4f6' }}>
          <h3>IB Approval Guidelines</h3>
        </div>
        <div style={{ padding: '20px' }}>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
            <div>
              <h4 style={{ marginBottom: '15px', color: '#10b981' }}>✅ Approve If:</h4>
              <ul style={{ paddingLeft: '20px', lineHeight: '1.6' }}>
                <li>Screenshot clearly shows IB number changed to <strong>IB123456789</strong></li>
                <li>Account number matches user registration</li>
                <li>Screenshot is recent (within 7 days)</li>
                <li>No signs of image manipulation</li>
                <li>All required elements visible in proof</li>
              </ul>
            </div>
            <div>
              <h4 style={{ marginBottom: '15px', color: '#ef4444' }}>❌ Reject If:</h4>
              <ul style={{ paddingLeft: '20px', lineHeight: '1.6' }}>
                <li>IB number is not <strong>IB123456789</strong></li>
                <li>Screenshot is unclear or unreadable</li>
                <li>Account details don't match registration</li>
                <li>Image appears to be manipulated</li>
                <li>Proof is too old (more than 7 days)</li>
              </ul>
            </div>
          </div>

          <div style={{ background: '#fef3c7', padding: '15px', borderRadius: '8px', marginTop: '20px', border: '1px solid #fbbf24' }}>
            <h4 style={{ marginBottom: '8px', color: '#92400e' }}>⚠️ Important Notes</h4>
            <ul style={{ fontSize: '14px', color: '#92400e', marginBottom: 0, paddingLeft: '20px' }}>
              <li>Approved users will have EA features enabled immediately</li>
              <li>Rejected users can re-upload corrected proof</li>
              <li>All actions are logged and auditable</li>
              <li>Contact support if proof appears suspicious</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );

  const renderCurrentScreen = () => {
    switch (currentScreen) {
      case 'user-management':
        return renderUserManagement();
      case 'ib-approvals':
        return renderIBApprovals();
      case 'group-management':
        return renderGroupManagement();
      case 'api-access':
        return renderAPIAccess();
      case 'master-accounts':
        return renderMasterAccounts();
      case 'copy-settings':
        return renderCopySettings();
      case 'trade-monitor':
        return renderTradeMonitor();
      case 'reports':
        return renderReports();
      case 'system-logs':
        return renderSystemLogs();
      default:
        return renderUserManagement();
    }
  };

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

  return (
    <div style={{ minHeight: '100vh', background: '#f8fafc' }}>
      <NotificationComponent />
      {renderSidebar()}
      {renderCurrentScreen()}

      {/* Loading overlay */}
      {loading && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'rgba(0,0,0,0.5)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 9999
        }}>
          <div style={{ background: 'white', padding: '20px', borderRadius: '8px' }}>
            Loading...
          </div>
        </div>
      )}

      {/* Temporary User Manager Modal */}
      {showTempUserManager && (
        <TempUserManager onClose={() => setShowTempUserManager(false)} />
      )}

      {/* Add User Modal */}
      {showAddUserModal && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'rgba(0,0,0,0.5)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 10000
        }}>
          <div style={{
            background: 'white',
            padding: '30px',
            borderRadius: '12px',
            width: '500px',
            maxWidth: '90vw',
            maxHeight: '90vh',
            overflow: 'auto'
          }}>
            <div style={{ marginBottom: '20px' }}>
              <h2 style={{ margin: '0 0 10px 0', color: '#1f2937' }}>Add New User</h2>
              <p style={{ margin: 0, color: '#6b7280' }}>Create a new user account</p>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
              <div>
                <label style={{ display: 'block', marginBottom: '5px', fontWeight: '500' }}>Full Name</label>
                <input
                  type="text"
                  value={newUser.name}
                  onChange={(e) => setNewUser({...newUser, name: e.target.value})}
                  style={{
                    width: '100%',
                    padding: '10px',
                    border: '1px solid #d1d5db',
                    borderRadius: '6px',
                    fontSize: '14px'
                  }}
                  placeholder="Enter full name"
                />
              </div>

              <div>
                <label style={{ display: 'block', marginBottom: '5px', fontWeight: '500' }}>Email</label>
                <input
                  type="email"
                  value={newUser.email}
                  onChange={(e) => setNewUser({...newUser, email: e.target.value})}
                  style={{
                    width: '100%',
                    padding: '10px',
                    border: '1px solid #d1d5db',
                    borderRadius: '6px',
                    fontSize: '14px'
                  }}
                  placeholder="Enter email address"
                />
              </div>

              <div>
                <label style={{ display: 'block', marginBottom: '5px', fontWeight: '500' }}>Mobile</label>
                <input
                  type="tel"
                  value={newUser.mobile}
                  onChange={(e) => setNewUser({...newUser, mobile: e.target.value})}
                  style={{
                    width: '100%',
                    padding: '10px',
                    border: '1px solid #d1d5db',
                    borderRadius: '6px',
                    fontSize: '14px'
                  }}
                  placeholder="Enter mobile number"
                />
              </div>

              <div>
                <label style={{ display: 'block', marginBottom: '5px', fontWeight: '500' }}>Role</label>
                <select
                  value={newUser.role}
                  onChange={(e) => setNewUser({...newUser, role: e.target.value})}
                  style={{
                    width: '100%',
                    padding: '10px',
                    border: '1px solid #d1d5db',
                    borderRadius: '6px',
                    fontSize: '14px'
                  }}
                >
                  <option value="user">User</option>
                  <option value="group_leader">Group Leader</option>
                  <option value="admin">Admin</option>
                </select>
              </div>

              <div>
                <label style={{ display: 'block', marginBottom: '5px', fontWeight: '500' }}>Country</label>
                <input
                  type="text"
                  value={newUser.country}
                  onChange={(e) => setNewUser({...newUser, country: e.target.value})}
                  style={{
                    width: '100%',
                    padding: '10px',
                    border: '1px solid #d1d5db',
                    borderRadius: '6px',
                    fontSize: '14px'
                  }}
                  placeholder="Enter country"
                />
              </div>

              <div>
                <label style={{ display: 'block', marginBottom: '5px', fontWeight: '500' }}>State</label>
                <input
                  type="text"
                  value={newUser.state}
                  onChange={(e) => setNewUser({...newUser, state: e.target.value})}
                  style={{
                    width: '100%',
                    padding: '10px',
                    border: '1px solid #d1d5db',
                    borderRadius: '6px',
                    fontSize: '14px'
                  }}
                  placeholder="Enter state"
                />
              </div>

              <div>
                <label style={{ display: 'block', marginBottom: '5px', fontWeight: '500' }}>City</label>
                <input
                  type="text"
                  value={newUser.city}
                  onChange={(e) => setNewUser({...newUser, city: e.target.value})}
                  style={{
                    width: '100%',
                    padding: '10px',
                    border: '1px solid #d1d5db',
                    borderRadius: '6px',
                    fontSize: '14px'
                  }}
                  placeholder="Enter city"
                />
              </div>

              <div>
                <label style={{ display: 'block', marginBottom: '5px', fontWeight: '500' }}>PIN Code</label>
                <input
                  type="text"
                  value={newUser.pin_code}
                  onChange={(e) => setNewUser({...newUser, pin_code: e.target.value})}
                  style={{
                    width: '100%',
                    padding: '10px',
                    border: '1px solid #d1d5db',
                    borderRadius: '6px',
                    fontSize: '14px'
                  }}
                  placeholder="Enter PIN code"
                />
              </div>

              <div>
                <label style={{ display: 'block', marginBottom: '5px', fontWeight: '500' }}>Password</label>
                <input
                  type="password"
                  value={newUser.password}
                  onChange={(e) => setNewUser({...newUser, password: e.target.value})}
                  style={{
                    width: '100%',
                    padding: '10px',
                    border: '1px solid #d1d5db',
                    borderRadius: '6px',
                    fontSize: '14px'
                  }}
                  placeholder="Enter password"
                />
              </div>
            </div>

            <div style={{ display: 'flex', gap: '10px', marginTop: '25px', justifyContent: 'flex-end' }}>
              <button
                onClick={() => {
                  setShowAddUserModal(false);
                  setNewUser({ name: '', email: '', mobile: '', role: 'user', password: '', country: 'India', state: '', city: '', pin_code: '' });
                }}
                style={{
                  padding: '10px 20px',
                  border: '1px solid #d1d5db',
                  borderRadius: '6px',
                  background: 'white',
                  cursor: 'pointer'
                }}
              >
                Cancel
              </button>
              <button
                onClick={addNewUser}
                disabled={loading || !newUser.name || !newUser.email || !newUser.password || !newUser.mobile || !newUser.state || !newUser.city || !newUser.pin_code}
                style={{
                  padding: '10px 20px',
                  border: 'none',
                  borderRadius: '6px',
                  background: loading ? '#9ca3af' : '#3b82f6',
                  color: 'white',
                  cursor: loading ? 'not-allowed' : 'pointer',
                  opacity: (!newUser.name || !newUser.email || !newUser.password) ? 0.5 : 1
                }}
              >
                {loading ? 'Creating...' : 'Create User'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Edit User Modal */}
      {showEditUserModal && editingUser && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'rgba(0,0,0,0.5)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 10000
        }}>
          <div style={{
            background: 'white',
            padding: '30px',
            borderRadius: '12px',
            width: '520px',
            maxWidth: '92vw',
            maxHeight: '92vh',
            overflow: 'auto'
          }}>
            <div style={{ marginBottom: '20px' }}>
              <h2 style={{ margin: '0 0 10px 0', color: '#1f2937' }}>Edit User</h2>
              <p style={{ margin: 0, color: '#6b7280' }}>Update profile details and account status</p>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '15px' }}>
              <div style={{ gridColumn: '1 / span 2' }}>
                <label style={{ display: 'block', marginBottom: '6px', fontWeight: 500 }}>Full Name</label>
                <input
                  type="text"
                  value={editingUser.name || ''}
                  onChange={(e) => handleEditingUserChange('name', e.target.value)}
                  style={{
                    width: '100%',
                    padding: '10px',
                    border: '1px solid #d1d5db',
                    borderRadius: '6px',
                    fontSize: '14px'
                  }}
                  placeholder="Enter full name"
                />
              </div>

              <div>
                <label style={{ display: 'block', marginBottom: '6px', fontWeight: 500 }}>Email</label>
                <input
                  type="email"
                  value={editingUser.email || ''}
                  onChange={(e) => handleEditingUserChange('email', e.target.value)}
                  style={{
                    width: '100%',
                    padding: '10px',
                    border: '1px solid #d1d5db',
                    borderRadius: '6px',
                    fontSize: '14px'
                  }}
                  placeholder="Enter email"
                />
              </div>

              <div>
                <label style={{ display: 'block', marginBottom: '6px', fontWeight: 500 }}>Mobile</label>
                <input
                  type="tel"
                  value={editingUser.mobile || ''}
                  onChange={(e) => handleEditingUserChange('mobile', e.target.value)}
                  style={{
                    width: '100%',
                    padding: '10px',
                    border: '1px solid #d1d5db',
                    borderRadius: '6px',
                    fontSize: '14px'
                  }}
                  placeholder="Enter mobile number"
                />
              </div>

              <div>
                <label style={{ display: 'block', marginBottom: '6px', fontWeight: 500 }}>Country</label>
                <input
                  type="text"
                  value={editingUser.country || ''}
                  onChange={(e) => handleEditingUserChange('country', e.target.value)}
                  style={{
                    width: '100%',
                    padding: '10px',
                    border: '1px solid #d1d5db',
                    borderRadius: '6px',
                    fontSize: '14px'
                  }}
                  placeholder="Enter country"
                />
              </div>

              <div>
                <label style={{ display: 'block', marginBottom: '6px', fontWeight: 500 }}>State</label>
                <input
                  type="text"
                  value={editingUser.state || ''}
                  onChange={(e) => handleEditingUserChange('state', e.target.value)}
                  style={{
                    width: '100%',
                    padding: '10px',
                    border: '1px solid #d1d5db',
                    borderRadius: '6px',
                    fontSize: '14px'
                  }}
                  placeholder="Enter state"
                />
              </div>

              <div>
                <label style={{ display: 'block', marginBottom: '6px', fontWeight: 500 }}>City</label>
                <input
                  type="text"
                  value={editingUser.city || ''}
                  onChange={(e) => handleEditingUserChange('city', e.target.value)}
                  style={{
                    width: '100%',
                    padding: '10px',
                    border: '1px solid #d1d5db',
                    borderRadius: '6px',
                    fontSize: '14px'
                  }}
                  placeholder="Enter city"
                />
              </div>

              <div>
                <label style={{ display: 'block', marginBottom: '6px', fontWeight: 500 }}>PIN Code</label>
                <input
                  type="text"
                  value={editingUser.pin_code || ''}
                  onChange={(e) => handleEditingUserChange('pin_code', e.target.value)}
                  style={{
                    width: '100%',
                    padding: '10px',
                    border: '1px solid #d1d5db',
                    borderRadius: '6px',
                    fontSize: '14px'
                  }}
                  placeholder="Enter PIN code"
                />
              </div>

              <div>
                <label style={{ display: 'block', marginBottom: '6px', fontWeight: 500 }}>Account Status</label>
                <select
                  value={editingUser.status || 'pending'}
                  onChange={(e) => handleEditingUserChange('status', e.target.value)}
                  style={{
                    width: '100%',
                    padding: '10px',
                    border: '1px solid #d1d5db',
                    borderRadius: '6px',
                    fontSize: '14px'
                  }}
                >
                  {STATUS_OPTIONS.map(option => (
                    <option key={option} value={option}>{option.charAt(0).toUpperCase() + option.slice(1)}</option>
                  ))}
                </select>
              </div>

              <div>
                <label style={{ display: 'block', marginBottom: '6px', fontWeight: 500 }}>KYC Status</label>
                <select
                  value={editingUser.kyc_status || 'pending'}
                  onChange={(e) => handleEditingUserChange('kyc_status', e.target.value)}
                  style={{
                    width: '100%',
                    padding: '10px',
                    border: '1px solid #d1d5db',
                    borderRadius: '6px',
                    fontSize: '14px'
                  }}
                >
                  {KYC_STATUS_OPTIONS.map(option => (
                    <option key={option} value={option}>{option.charAt(0).toUpperCase() + option.slice(1)}</option>
                  ))}
                </select>
              </div>
            </div>

            <div style={{
              background: '#f8fafc',
              padding: '12px 16px',
              borderRadius: '8px',
              border: '1px solid #e2e8f0',
              marginTop: '20px',
              color: '#1f2937',
              fontSize: '13px'
            }}>
              <strong>Heads-up:</strong> Role and password changes are handled from their respective workflows. Use this form for profile/contact updates only.
            </div>

            <div style={{ display: 'flex', gap: '12px', marginTop: '24px', justifyContent: 'flex-end' }}>
              <button
                onClick={() => {
                  setShowEditUserModal(false);
                  setEditingUser(null);
                }}
                style={{
                  padding: '10px 20px',
                  border: '1px solid #d1d5db',
                  borderRadius: '6px',
                  background: 'white',
                  cursor: 'pointer'
                }}
              >
                Cancel
              </button>
              <button
                onClick={saveEditedUser}
                disabled={loading || !editingUser.name || !editingUser.email || !editingUser.mobile}
                style={{
                  padding: '10px 20px',
                  border: 'none',
                  borderRadius: '6px',
                  background: loading ? '#9ca3af' : '#3b82f6',
                  color: 'white',
                  cursor: loading ? 'not-allowed' : 'pointer',
                  opacity: (!editingUser.name || !editingUser.email) ? 0.5 : 1
                }}
              >
                {loading ? 'Saving...' : 'Save Changes'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Screen Selector for Demo */}
      <div style={{
        position: 'fixed',
        top: '20px',
        right: '20px',
        zIndex: 1000
      }}>
        <select
          style={{ padding: '8px 12px', borderRadius: '6px', border: '1px solid #d1d5db', background: 'white' }}
          value={currentScreen}
          onChange={(e) => showScreen(e.target.value as Screen)}
        >
          <option value="user-management">User Management</option>
          <option value="ib-approvals">IB Approvals</option>
          <option value="group-management">Group Management</option>
          <option value="api-access">API Access</option>
          <option value="master-accounts">Master Accounts</option>
          <option value="copy-settings">Copy Settings</option>
          <option value="trade-monitor">Trade Monitor</option>
          <option value="reports">Reports & Logs</option>
          <option value="system-logs">System Logs</option>
        </select>
      </div>

      {/* Image Modal */}
      {showImageModal && selectedProofImage && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundColor: 'rgba(0, 0, 0, 0.8)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 1000
        }}>
          <div style={{
            backgroundColor: 'white',
            borderRadius: '8px',
            padding: '20px',
            maxWidth: '90vw',
            maxHeight: '90vh',
            position: 'relative'
          }}>
            <button
              onClick={() => setShowImageModal(false)}
              style={{
                position: 'absolute',
                top: '10px',
                right: '10px',
                background: '#ef4444',
                color: 'white',
                border: 'none',
                borderRadius: '50%',
                width: '30px',
                height: '30px',
                cursor: 'pointer',
                fontSize: '16px'
              }}
            >
              ×
            </button>
            <img
              src={`data:image/jpeg;base64,${selectedProofImage}`}
              alt="IB Proof"
              style={{
                maxWidth: '100%',
                maxHeight: '80vh',
                objectFit: 'contain'
              }}
            />
          </div>
        </div>
      )}
    </div>
  );
}