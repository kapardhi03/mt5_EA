"use client";
import React, { useState, useEffect } from 'react';
import API_BASE_URL from '@/config/api';

const API_URL = API_BASE_URL; // shared base URL for group API calls

interface GroupPanelProps {
  onLogout: () => void;
}

type Screen = 'dashboard' | 'members' | 'trading-controls' | 'settlements' | 'member-reports' | 'error-reports';

interface GroupMember {
  account_id: string;
  user_id: string;
  name: string;
  email: string;
  mobile: string;
  broker: string;
  server: string;
  account_number_masked: string;
  account_type: string;
  copy_status: string;
  copy_start_date?: string;
  opening_balance: number;
  current_balance: number;
  profit_since_copy_start: number;
  running_trades_count: number;
  status: string;
  join_date?: string;
  last_sync?: string;
  last_error?: string;
}

interface DashboardData {
  group_info: {
    group_name: string;
    company_name: string;
    settlement_cycle: string;
    profit_sharing_percentage: number;
    trading_status: string;
    api_key_status: string;
    api_key: string;
  };
  statistics: {
    total_members: number;
    active_members: number;
    pending_members: number;
    total_equity: number;
    total_profit: number;
    today_profit: number;
    pending_settlement_amount: number;
  };
  recent_activity: Array<{
    date: string;
    action: string;
    details: string;
    amount?: number;
  }>;
}

interface Settlement {
  _id: string;
  period_start: string;
  period_end: string;
  settlement_date: string;
  total_profit: number;
  profit_sharing_percentage: number;
  amount_due: number;
  amount_paid: number;
  status: string;
  payment_method?: string;
  payment_reference?: string;
}

interface ErrorLog {
  _id: string;
  user_id?: string;
  account_id?: string;
  symbol?: string;
  error_code: string;
  error_message: string;
  retry_count: number;
  resolved: boolean;
  created_at: string;
}

export default function GroupPanel({ onLogout }: GroupPanelProps) {
  const [currentScreen, setCurrentScreen] = useState<Screen>('dashboard');
  const [loading, setLoading] = useState(false);

  // Data states
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [members, setMembers] = useState<GroupMember[]>([]);
  const [settlements, setSettlements] = useState<Settlement[]>([]);
  const [errorLogs, setErrorLogs] = useState<ErrorLog[]>([]);

  // Helper function to generate unique API key
  const generateApiKey = () => {
    const timestamp = Date.now();
    const random = Math.random().toString(36).substring(2, 15);
    return `EA_${timestamp}_${random}`.toUpperCase();
  };

  // Fetch real data from backend
  useEffect(() => {
    const fetchGroupData = async () => {
      try {
        setLoading(true);
        const token = localStorage.getItem('authToken');
        const userData = localStorage.getItem('userData');

        if (!token || !userData) {
          console.error('No authentication token found');
          return;
        }

  const user = JSON.parse(userData);

        // Fetch group dashboard data
        try {
          const dashboardResponse = await fetch(`${API_URL}/api/v1/groups/${user.group_id}/dashboard`, {
            method: 'GET',
            headers: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json',
            },
          });

          if (dashboardResponse.ok) {
            const dashboardResult = await dashboardResponse.json();
            if (dashboardResult.success && dashboardResult.data) {
              setDashboardData(dashboardResult.data);
            }
          }
        } catch (error) {
          console.error('Error fetching group dashboard:', error);
        }

        // Fetch group members
        try {
          const membersResponse = await fetch(`${API_URL}/api/v1/groups/${user.group_id}/members`, {
            method: 'GET',
            headers: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json',
            },
          });

          if (membersResponse.ok) {
            const membersResult = await membersResponse.json();
            if (membersResult.success && membersResult.data) {
              setMembers(membersResult.data);
            }
          }
        } catch (error) {
          console.error('Error fetching group members:', error);
        }

        // Fetch settlements
        try {
          const settlementsResponse = await fetch(`${API_URL}/api/v1/groups/${user.group_id}/settlements`, {
            method: 'GET',
            headers: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json',
            },
          });

          if (settlementsResponse.ok) {
            const settlementsResult = await settlementsResponse.json();
            if (settlementsResult.success && settlementsResult.data) {
              setSettlements(settlementsResult.data);
            }
          }
        } catch (error) {
          console.error('Error fetching settlements:', error);
        }

        // If no real data available, use demo data as fallback
        setTimeout(() => {
          if (!dashboardData) {
            setDashboardData({
              group_info: {
                group_name: "Professional Traders",
                company_name: "PT Trading LLC",
                settlement_cycle: "monthly",
                profit_sharing_percentage: 80,
                trading_status: "active",
                api_key_status: "active",
                api_key: generateApiKey()
              },
              statistics: {
                total_members: 30,
                active_members: 25,
                pending_members: 5,
                total_equity: 450000.50,
                total_profit: 35000.80,
                today_profit: 1250.30,
                pending_settlement_amount: 8500.20
              },
              recent_activity: [
                {
                  date: "2025-09-28T14:30:00Z",
                  action: "Member Approved",
                  details: "John Doe's Vantage account approved and activated",
                },
                {
                  date: "2025-09-28T12:15:00Z",
                  action: "EA Executed",
                  details: "EURUSD BUY trade executed for 24 accounts",
                  amount: 125.50
                },
                {
                  date: "2025-09-28T09:45:00Z",
                  action: "Settlement Request",
                  details: "Monthly settlement submitted for approval",
                  amount: 8500.20
                }
              ]
            });
          }
        }, 1000);
      } catch (error) {
        console.error('Error fetching group data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchGroupData();
  }, []);

  const showScreen = (screenId: Screen) => {
    setCurrentScreen(screenId);
  };

  const renderSidebar = () => (
    <div className="sidebar">
      <div className="sidebar-header">
        <h3>Group Panel</h3>
        <p>Group Leader Portal</p>
      </div>
      <nav className="sidebar-nav">
        <a
          href="#"
          className={`nav-item ${currentScreen === 'dashboard' ? 'active' : ''}`}
          onClick={() => showScreen('dashboard')}
        >
          <div className="nav-icon">📊</div>
          Dashboard
        </a>
        <a
          href="#"
          className={`nav-item ${currentScreen === 'members' ? 'active' : ''}`}
          onClick={() => showScreen('members')}
        >
          <div className="nav-icon">👥</div>
          Members
        </a>
        <a
          href="#"
          className={`nav-item ${currentScreen === 'trading-controls' ? 'active' : ''}`}
          onClick={() => showScreen('trading-controls')}
        >
          <div className="nav-icon">🎮</div>
          Trading Controls
        </a>
        <a
          href="#"
          className={`nav-item ${currentScreen === 'settlements' ? 'active' : ''}`}
          onClick={() => showScreen('settlements')}
        >
          <div className="nav-icon">💰</div>
          Settlements
        </a>
        <a
          href="#"
          className={`nav-item ${currentScreen === 'member-reports' ? 'active' : ''}`}
          onClick={() => showScreen('member-reports')}
        >
          <div className="nav-icon">📈</div>
          Member Reports
        </a>
        <a
          href="#"
          className={`nav-item ${currentScreen === 'error-reports' ? 'active' : ''}`}
          onClick={() => showScreen('error-reports')}
        >
          <div className="nav-icon">⚠️</div>
          Error Reports
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

  const renderDashboard = () => (
    <div className="main-content">
      <div className="dashboard-header">
        <h1>Welcome to {dashboardData?.group_info.group_name}</h1>
        <p>Manage your trading group and monitor performance</p>
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <h3>Total Members</h3>
          <div className="value">{dashboardData?.statistics.total_members}</div>
          <div className="change">{dashboardData?.statistics.active_members} active</div>
        </div>
        <div className="stat-card">
          <h3>Total Equity</h3>
          <div className="value">${dashboardData?.statistics.total_equity.toLocaleString()}</div>
          <div className="change">Combined portfolio</div>
        </div>
        <div className="stat-card">
          <h3>Total Profit</h3>
          <div className="value" style={{ color: '#10b981' }}>
            ${dashboardData?.statistics.total_profit.toLocaleString()}
          </div>
          <div className="change" style={{ color: '#10b981' }}>
            +${dashboardData?.statistics.today_profit.toLocaleString()} today
          </div>
        </div>
        <div className="stat-card">
          <h3>Pending Settlement</h3>
          <div className="value">${dashboardData?.statistics.pending_settlement_amount.toLocaleString()}</div>
          <div className="change">Ready for distribution</div>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
        <div className="card">
          <div style={{ padding: '20px', borderBottom: '1px solid #f3f4f6' }}>
            <h3>Recent Activity</h3>
          </div>
          <div style={{ padding: '20px' }}>
            {dashboardData?.recent_activity.map((activity, index) => (
              <div key={index} style={{ marginBottom: '15px', paddingBottom: '15px', borderBottom: index < dashboardData.recent_activity.length - 1 ? '1px solid #f3f4f6' : 'none' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                  <div>
                    <strong>{activity.action}</strong>
                    <div style={{ fontSize: '12px', color: '#6b7280', marginTop: '2px' }}>
                      {new Date(activity.date).toLocaleString()}
                    </div>
                    <div style={{ fontSize: '14px', marginTop: '4px' }}>{activity.details}</div>
                  </div>
                  {activity.amount && (
                    <div style={{ fontSize: '14px', color: activity.amount > 0 ? '#10b981' : '#ef4444', fontWeight: 'bold' }}>
                      {activity.amount > 0 ? '+' : ''}${activity.amount}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="card">
          <div style={{ padding: '20px', borderBottom: '1px solid #f3f4f6' }}>
            <h3>Group Information</h3>
          </div>
          <div style={{ padding: '20px' }}>
            <div style={{ marginBottom: '15px' }}>
              <div style={{ fontSize: '12px', color: '#6b7280', textTransform: 'uppercase' }}>Company</div>
              <div style={{ fontWeight: 'bold', marginTop: '4px' }}>{dashboardData?.group_info.company_name}</div>
            </div>

            <div style={{ marginBottom: '15px' }}>
              <div style={{ fontSize: '12px', color: '#6b7280', textTransform: 'uppercase' }}>Settlement Cycle</div>
              <div style={{ fontWeight: 'bold', marginTop: '4px' }}>{dashboardData?.group_info.settlement_cycle}</div>
            </div>

            <div style={{ marginBottom: '15px' }}>
              <div style={{ fontSize: '12px', color: '#6b7280', textTransform: 'uppercase' }}>Profit Sharing</div>
              <div style={{ fontWeight: 'bold', marginTop: '4px' }}>{dashboardData?.group_info.profit_sharing_percentage}% to members</div>
            </div>

            <div style={{ marginBottom: '15px' }}>
              <div style={{ fontSize: '12px', color: '#6b7280', textTransform: 'uppercase' }}>Group API Key</div>
              <div style={{
                marginTop: '4px',
                padding: '8px 12px',
                background: '#f8fafc',
                border: '1px solid #e2e8f0',
                borderRadius: '6px',
                fontFamily: 'monospace',
                fontSize: '14px',
                wordBreak: 'break-all',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center'
              }}>
                <span>{dashboardData?.group_info.api_key}</span>
                <button
                  onClick={() => navigator.clipboard.writeText(dashboardData?.group_info.api_key || '')}
                  style={{
                    padding: '4px 8px',
                    fontSize: '12px',
                    background: '#3b82f6',
                    color: 'white',
                    border: 'none',
                    borderRadius: '4px',
                    cursor: 'pointer',
                    marginLeft: '8px'
                  }}
                  title="Copy API Key"
                >
                  📋
                </button>
              </div>
              <div style={{ fontSize: '11px', color: '#6b7280', marginTop: '4px' }}>
                Use this key to integrate with external systems
              </div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '15px' }}>
              <div>
                <div style={{ fontSize: '12px', color: '#6b7280', textTransform: 'uppercase' }}>Trading Status</div>
                <div style={{ marginTop: '4px' }}>
                  <span className={`status-badge ${dashboardData?.group_info.trading_status === 'active' ? 'status-active' : 'status-warning'}`}>
                    {dashboardData?.group_info.trading_status}
                  </span>
                </div>
              </div>
              <div>
                <div style={{ fontSize: '12px', color: '#6b7280', textTransform: 'uppercase' }}>API Status</div>
                <div style={{ marginTop: '4px' }}>
                  <span className={`status-badge ${dashboardData?.group_info.api_key_status === 'active' ? 'status-active' : 'status-error'}`}>
                    {dashboardData?.group_info.api_key_status}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="card" style={{ marginTop: '20px' }}>
        <div style={{ padding: '20px', borderBottom: '1px solid #f3f4f6' }}>
          <h3>Member Overview</h3>
        </div>
        <div style={{ padding: '20px' }}>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '20px' }}>
            <div style={{ background: '#f0f9ff', padding: '20px', borderRadius: '8px', border: '1px solid #e0f2fe' }}>
              <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#0369a1' }}>
                {dashboardData?.statistics.active_members}
              </div>
              <div style={{ fontSize: '14px', color: '#0369a1' }}>Active Members</div>
            </div>
            <div style={{ background: '#fef3c7', padding: '20px', borderRadius: '8px', border: '1px solid #fbbf24' }}>
              <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#92400e' }}>
                {dashboardData?.statistics.pending_members}
              </div>
              <div style={{ fontSize: '14px', color: '#92400e' }}>Pending Approval</div>
            </div>
            <div style={{ background: '#dcfce7', padding: '20px', borderRadius: '8px', border: '1px solid #bbf7d0' }}>
              <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#166534' }}>
                {dashboardData?.statistics.total_members}
              </div>
              <div style={{ fontSize: '14px', color: '#166534' }}>Total Members</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  const renderMembers = () => (
    <div className="main-content">
      <div className="dashboard-header">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <h1>Group Members</h1>
            <p>Manage member accounts and approvals</p>
          </div>
          <div style={{ display: 'flex', gap: '10px' }}>
            <select style={{ padding: '8px 12px', borderRadius: '6px', border: '1px solid #d1d5db' }}>
              <option>All Status</option>
              <option>Active</option>
              <option>Pending</option>
              <option>Suspended</option>
            </select>
            <input
              type="text"
              placeholder="Search members..."
              style={{ padding: '8px 12px', borderRadius: '6px', border: '1px solid #d1d5db', minWidth: '200px' }}
            />
          </div>
        </div>
      </div>

      <div className="card">
        <div style={{ padding: '20px', borderBottom: '1px solid #f3f4f6' }}>
          <h3>All Members</h3>
        </div>
        <div style={{ overflowX: 'auto' }}>
          <table className="data-table">
            <thead>
              <tr>
                <th>Member</th>
                <th>Account</th>
                <th>Broker</th>
                <th>Balance</th>
                <th>Profit</th>
                <th>Copy Status</th>
                <th>Running Trades</th>
                <th>Status</th>
                <th>Join Date</th>
                <th>Last Sync</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {members.map((member, index) => (
                <tr key={index}>
                  <td>
                    <div>
                      <div style={{ fontWeight: 'bold' }}>{member.name}</div>
                      <div style={{ fontSize: '12px', color: '#6b7280' }}>{member.email}</div>
                    </div>
                  </td>
                  <td>
                    <div>
                      <div style={{ fontWeight: 'bold' }}>{member.account_number_masked}</div>
                      <div style={{ fontSize: '12px', color: '#6b7280' }}>{member.account_type}</div>
                    </div>
                  </td>
                  <td>
                    <div>
                      <div style={{ fontWeight: 'bold' }}>{member.broker}</div>
                      <div style={{ fontSize: '12px', color: '#6b7280' }}>{member.server}</div>
                    </div>
                  </td>
                  <td>${member.current_balance.toLocaleString()}</td>
                  <td>
                    <div style={{ color: member.profit_since_copy_start >= 0 ? '#10b981' : '#ef4444', fontWeight: 'bold' }}>
                      {member.profit_since_copy_start >= 0 ? '+' : ''}${member.profit_since_copy_start.toLocaleString()}
                    </div>
                  </td>
                  <td>
                    <span className={`status-badge ${member.copy_status === 'active' ? 'status-active' : 'status-pending'}`}>
                      {member.copy_status}
                    </span>
                  </td>
                  <td style={{ textAlign: 'center' }}>{member.running_trades_count}</td>
                  <td>
                    <span className={`status-badge ${member.status === 'approved' ? 'status-active' : 'status-pending'}`}>
                      {member.status}
                    </span>
                  </td>
                  <td>{member.join_date ? new Date(member.join_date).toLocaleDateString() : 'N/A'}</td>
                  <td>{member.last_sync ? new Date(member.last_sync).toLocaleString() : 'Never'}</td>
                  <td>
                    <div style={{ display: 'flex', gap: '5px' }}>
                      {member.status === 'pending' && (
                        <>
                          <button className="btn btn-primary btn-sm">Approve</button>
                          <button className="btn btn-outline btn-sm" style={{ color: '#ef4444', borderColor: '#ef4444' }}>
                            Reject
                          </button>
                        </>
                      )}
                      {member.status === 'approved' && (
                        <>
                          <button className="btn btn-outline btn-sm">View</button>
                          <button className="btn btn-outline btn-sm">Settings</button>
                        </>
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

  const renderTradingControls = () => (
    <div className="main-content">
      <div className="dashboard-header">
        <h1>Trading Controls</h1>
        <p>Manage group trading settings and operations</p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
        <div className="card">
          <div style={{ padding: '20px', borderBottom: '1px solid #f3f4f6' }}>
            <h3>Trading Status Control</h3>
          </div>
          <div style={{ padding: '20px' }}>
            <div style={{ marginBottom: '20px' }}>
              <div style={{ fontSize: '12px', color: '#6b7280', textTransform: 'uppercase', marginBottom: '8px' }}>
                Current Status
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <span className={`status-badge ${dashboardData?.group_info.trading_status === 'active' ? 'status-active' : 'status-warning'}`}>
                  {dashboardData?.group_info.trading_status}
                </span>
                <span style={{ fontSize: '14px', color: '#6b7280' }}>
                  All trades are being copied to member accounts
                </span>
              </div>
            </div>

            <div className="form-group">
              <label>Change Trading Status</label>
              <select>
                <option value="active">Active - Copy all trades</option>
                <option value="paused">Paused - Stop copying new trades</option>
                <option value="stopped">Stopped - Halt all operations</option>
              </select>
            </div>

            <div className="form-group">
              <label>OTP Verification (Required for changes)</label>
              <input type="text" placeholder="Enter 6-digit OTP" maxLength={6} />
              <div style={{ fontSize: '12px', color: '#6b7280', marginTop: '4px' }}>
                OTP will be sent to your registered mobile number
              </div>
            </div>

            <div style={{ display: 'flex', gap: '10px' }}>
              <button className="btn btn-primary">Update Status</button>
              <button className="btn btn-outline">Send OTP</button>
            </div>
          </div>
        </div>

        <div className="card">
          <div style={{ padding: '20px', borderBottom: '1px solid #f3f4f6' }}>
            <h3>Auto-Pause Rules</h3>
          </div>
          <div style={{ padding: '20px' }}>
            <div className="form-group">
              <label>Maximum Daily Loss (%)</label>
              <input type="number" defaultValue="10" min="1" max="50" />
              <div style={{ fontSize: '12px', color: '#6b7280', marginTop: '4px' }}>
                Auto-pause trading if daily loss exceeds this percentage
              </div>
            </div>

            <div className="form-group">
              <label>Maximum Drawdown (%)</label>
              <input type="number" defaultValue="20" min="5" max="50" />
              <div style={{ fontSize: '12px', color: '#6b7280', marginTop: '4px' }}>
                Auto-pause if overall drawdown exceeds this limit
              </div>
            </div>

            <div className="form-group">
              <label>Risk Management</label>
              <div style={{ marginTop: '8px' }}>
                <label style={{ display: 'flex', alignItems: 'center', marginBottom: '8px', fontWeight: 'normal' }}>
                  <input type="checkbox" style={{ marginRight: '8px' }} defaultChecked />
                  Auto-pause on high volatility
                </label>
                <label style={{ display: 'flex', alignItems: 'center', marginBottom: '8px', fontWeight: 'normal' }}>
                  <input type="checkbox" style={{ marginRight: '8px' }} defaultChecked />
                  Auto-pause during news events
                </label>
                <label style={{ display: 'flex', alignItems: 'center', marginBottom: '8px', fontWeight: 'normal' }}>
                  <input type="checkbox" style={{ marginRight: '8px' }} />
                  Auto-pause on low liquidity
                </label>
              </div>
            </div>

            <button className="btn btn-primary">Save Rules</button>
          </div>
        </div>
      </div>

      <div className="card" style={{ marginTop: '20px' }}>
        <div style={{ padding: '20px', borderBottom: '1px solid #f3f4f6' }}>
          <h3>Trading Statistics</h3>
        </div>
        <div style={{ padding: '20px' }}>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr 1fr', gap: '20px' }}>
            <div style={{ background: '#f8fafc', padding: '15px', borderRadius: '8px' }}>
              <div style={{ fontSize: '12px', color: '#6b7280', marginBottom: '5px' }}>Trades Today</div>
              <div style={{ fontSize: '24px', fontWeight: 'bold' }}>127</div>
            </div>
            <div style={{ background: '#f8fafc', padding: '15px', borderRadius: '8px' }}>
              <div style={{ fontSize: '12px', color: '#6b7280', marginBottom: '5px' }}>Success Rate</div>
              <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#10b981' }}>98.7%</div>
            </div>
            <div style={{ background: '#f8fafc', padding: '15px', borderRadius: '8px' }}>
              <div style={{ fontSize: '12px', color: '#6b7280', marginBottom: '5px' }}>Avg Copy Time</div>
              <div style={{ fontSize: '24px', fontWeight: 'bold' }}>247ms</div>
            </div>
            <div style={{ background: '#f8fafc', padding: '15px', borderRadius: '8px' }}>
              <div style={{ fontSize: '12px', color: '#6b7280', marginBottom: '5px' }}>Active Positions</div>
              <div style={{ fontSize: '24px', fontWeight: 'bold' }}>45</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  const renderSettlements = () => (
    <div className="main-content">
      <div className="dashboard-header">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <h1>Settlements</h1>
            <p>Manage profit sharing and payment settlements</p>
          </div>
          <button className="btn btn-primary">+ Create Settlement Request</button>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '20px', marginBottom: '20px' }}>
        <div className="stat-card">
          <h3>Pending Settlement</h3>
          <div className="value">${dashboardData?.statistics.pending_settlement_amount.toLocaleString()}</div>
          <div className="change">Ready for payment</div>
        </div>
        <div className="stat-card">
          <h3>This Month Profit</h3>
          <div className="value" style={{ color: '#10b981' }}>
            ${dashboardData?.statistics.total_profit.toLocaleString()}
          </div>
          <div className="change" style={{ color: '#10b981' }}>Member share: 80%</div>
        </div>
        <div className="stat-card">
          <h3>Total Paid</h3>
          <div className="value">
            ${settlements.filter(s => s.status === 'paid').reduce((sum, s) => sum + s.amount_paid, 0).toLocaleString()}
          </div>
          <div className="change">Lifetime settlements</div>
        </div>
      </div>

      <div className="card">
        <div style={{ padding: '20px', borderBottom: '1px solid #f3f4f6' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <h3>Settlement History</h3>
            <div style={{ display: 'flex', gap: '10px' }}>
              <select style={{ padding: '8px 12px', borderRadius: '6px', border: '1px solid #d1d5db' }}>
                <option>All Status</option>
                <option>Pending</option>
                <option>Paid</option>
                <option>Rejected</option>
              </select>
              <button className="btn btn-outline">Download Report</button>
            </div>
          </div>
        </div>
        <div style={{ overflowX: 'auto' }}>
          <table className="data-table">
            <thead>
              <tr>
                <th>Period</th>
                <th>Settlement Date</th>
                <th>Total Profit</th>
                <th>Member Share (%)</th>
                <th>Amount Due</th>
                <th>Amount Paid</th>
                <th>Payment Method</th>
                <th>Reference</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {settlements.map((settlement, index) => (
                <tr key={index}>
                  <td>
                    {new Date(settlement.period_start).toLocaleDateString()} - {new Date(settlement.period_end).toLocaleDateString()}
                  </td>
                  <td>{new Date(settlement.settlement_date).toLocaleDateString()}</td>
                  <td>${settlement.total_profit.toLocaleString()}</td>
                  <td>{settlement.profit_sharing_percentage}%</td>
                  <td>${settlement.amount_due.toLocaleString()}</td>
                  <td>${settlement.amount_paid.toLocaleString()}</td>
                  <td>{settlement.payment_method || 'N/A'}</td>
                  <td style={{ fontFamily: 'monospace' }}>{settlement.payment_reference || 'N/A'}</td>
                  <td>
                    <span className={`status-badge ${settlement.status === 'paid' ? 'status-active' : settlement.status === 'pending' ? 'status-pending' : 'status-error'}`}>
                      {settlement.status}
                    </span>
                  </td>
                  <td>
                    <div style={{ display: 'flex', gap: '5px' }}>
                      <button className="btn btn-outline btn-sm">View</button>
                      {settlement.status === 'pending' && (
                        <button className="btn btn-outline btn-sm">Update</button>
                      )}
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
            <h3>Settlement Calculator</h3>
          </div>
          <div style={{ padding: '20px' }}>
            <div style={{ marginBottom: '20px' }}>
              <div style={{ fontSize: '12px', color: '#6b7280', marginBottom: '8px' }}>Current Month Profit</div>
              <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#10b981' }}>
                ${dashboardData?.statistics.total_profit.toLocaleString()}
              </div>
            </div>

            <div style={{ marginBottom: '20px' }}>
              <div style={{ fontSize: '12px', color: '#6b7280', marginBottom: '8px' }}>
                Member Share ({dashboardData?.group_info.profit_sharing_percentage}%)
              </div>
              <div style={{ fontSize: '20px', fontWeight: 'bold' }}>
                ${dashboardData ? (dashboardData.statistics.total_profit * dashboardData.group_info.profit_sharing_percentage / 100).toLocaleString() : '0'}
              </div>
            </div>

            <div style={{ marginBottom: '20px' }}>
              <div style={{ fontSize: '12px', color: '#6b7280', marginBottom: '8px' }}>
                Company Share ({dashboardData ? 100 - dashboardData.group_info.profit_sharing_percentage : 0}%)
              </div>
              <div style={{ fontSize: '20px', fontWeight: 'bold' }}>
                ${dashboardData ? (dashboardData.statistics.total_profit * (100 - dashboardData.group_info.profit_sharing_percentage) / 100).toLocaleString() : '0'}
              </div>
            </div>

            <div style={{ background: '#f0f9ff', padding: '15px', borderRadius: '8px', border: '1px solid #e0f2fe' }}>
              <div style={{ fontSize: '12px', color: '#0369a1', marginBottom: '5px' }}>Settlement Due</div>
              <div style={{ fontSize: '18px', fontWeight: 'bold', color: '#0369a1' }}>
                Next settlement: October 1, 2025
              </div>
            </div>
          </div>
        </div>

        <div className="card">
          <div style={{ padding: '20px', borderBottom: '1px solid #f3f4f6' }}>
            <h3>Payment Instructions</h3>
          </div>
          <div style={{ padding: '20px' }}>
            <div style={{ marginBottom: '15px' }}>
              <div style={{ fontSize: '12px', color: '#6b7280', textTransform: 'uppercase' }}>Bank Account</div>
              <div style={{ fontWeight: 'bold', marginTop: '4px' }}>PT Trading LLC</div>
              <div style={{ fontSize: '14px', color: '#6b7280' }}>Account: 1234567890</div>
              <div style={{ fontSize: '14px', color: '#6b7280' }}>SWIFT: ABCDUS33</div>
            </div>

            <div style={{ marginBottom: '15px' }}>
              <div style={{ fontSize: '12px', color: '#6b7280', textTransform: 'uppercase' }}>Crypto Wallet</div>
              <div style={{ fontWeight: 'bold', marginTop: '4px' }}>USDT (TRC20)</div>
              <div style={{ fontSize: '12px', color: '#6b7280', fontFamily: 'monospace', wordBreak: 'break-all' }}>
                TXJ9K8L2M5N7P4Q1R6S3T8U9V2W5X7Y1Z4
              </div>
            </div>

            <div style={{ background: '#fef3c7', padding: '15px', borderRadius: '8px', border: '1px solid #fbbf24' }}>
              <div style={{ fontSize: '14px', color: '#92400e' }}>
                <strong>Important:</strong> All settlement requests require admin approval and OTP verification.
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  const renderMemberReports = () => (
    <div className="main-content">
      <div className="dashboard-header">
        <h1>Member Reports</h1>
        <p>Detailed profit sharing reports for group members</p>
      </div>

      <div className="card">
        <div style={{ padding: '20px', borderBottom: '1px solid #f3f4f6' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <h3>Profit Sharing Reports</h3>
            <div style={{ display: 'flex', gap: '10px' }}>
              <select style={{ padding: '8px 12px', borderRadius: '6px', border: '1px solid #d1d5db' }}>
                <option>This Month</option>
                <option>Last Month</option>
                <option>Last 3 Months</option>
                <option>Custom Range</option>
              </select>
              <button className="btn btn-outline">Download CSV</button>
            </div>
          </div>
        </div>
        <div style={{ overflowX: 'auto' }}>
          <table className="data-table">
            <thead>
              <tr>
                <th>Member</th>
                <th>Account</th>
                <th>Copy Start</th>
                <th>Opening Balance</th>
                <th>Current Balance</th>
                <th>Total Profit</th>
                <th>Member Share</th>
                <th>Company Share</th>
                <th>Last Settlement</th>
                <th>Pending Amount</th>
              </tr>
            </thead>
            <tbody>
              {members.filter(m => m.status === 'approved').map((member, index) => {
                const memberShare = member.profit_since_copy_start * (dashboardData?.group_info.profit_sharing_percentage || 80) / 100;
                const companyShare = member.profit_since_copy_start - memberShare;

                return (
                  <tr key={index}>
                    <td>
                      <div>
                        <div style={{ fontWeight: 'bold' }}>{member.name}</div>
                        <div style={{ fontSize: '12px', color: '#6b7280' }}>{member.email}</div>
                      </div>
                    </td>
                    <td>
                      <div>
                        <div style={{ fontWeight: 'bold' }}>{member.account_number_masked}</div>
                        <div style={{ fontSize: '12px', color: '#6b7280' }}>{member.broker} {member.account_type}</div>
                      </div>
                    </td>
                    <td>{member.copy_start_date ? new Date(member.copy_start_date).toLocaleDateString() : 'N/A'}</td>
                    <td>${member.opening_balance.toLocaleString()}</td>
                    <td>${member.current_balance.toLocaleString()}</td>
                    <td>
                      <div style={{ color: member.profit_since_copy_start >= 0 ? '#10b981' : '#ef4444', fontWeight: 'bold' }}>
                        {member.profit_since_copy_start >= 0 ? '+' : ''}${member.profit_since_copy_start.toLocaleString()}
                      </div>
                    </td>
                    <td>
                      <div style={{ color: '#10b981', fontWeight: 'bold' }}>
                        ${memberShare.toLocaleString()}
                      </div>
                    </td>
                    <td>
                      <div style={{ color: '#3b82f6', fontWeight: 'bold' }}>
                        ${companyShare.toLocaleString()}
                      </div>
                    </td>
                    <td>Sept 1, 2025</td>
                    <td>
                      <div style={{ color: '#f59e0b', fontWeight: 'bold' }}>
                        ${memberShare.toLocaleString()}
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px', marginTop: '20px' }}>
        <div className="card">
          <div style={{ padding: '20px', borderBottom: '1px solid #f3f4f6' }}>
            <h3>Performance Summary</h3>
          </div>
          <div style={{ padding: '20px' }}>
            <div style={{ marginBottom: '20px' }}>
              <div style={{ fontSize: '12px', color: '#6b7280', marginBottom: '5px' }}>Total Member Profit</div>
              <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#10b981' }}>
                +${members.filter(m => m.status === 'approved').reduce((sum, m) => sum + m.profit_since_copy_start, 0).toLocaleString()}
              </div>
            </div>

            <div style={{ marginBottom: '20px' }}>
              <div style={{ fontSize: '12px', color: '#6b7280', marginBottom: '5px' }}>Average Return</div>
              <div style={{ fontSize: '20px', fontWeight: 'bold', color: '#10b981' }}>
                +{(members.filter(m => m.status === 'approved').reduce((sum, m) => sum + (m.profit_since_copy_start / m.opening_balance * 100), 0) / members.filter(m => m.status === 'approved').length).toFixed(1)}%
              </div>
            </div>

            <div style={{ marginBottom: '20px' }}>
              <div style={{ fontSize: '12px', color: '#6b7280', marginBottom: '5px' }}>Best Performer</div>
              <div style={{ fontSize: '16px', fontWeight: 'bold' }}>
                {members.reduce((best, m) => m.profit_since_copy_start > best.profit_since_copy_start ? m : best, members[0])?.name}
              </div>
              <div style={{ fontSize: '14px', color: '#10b981' }}>
                +${members.reduce((best, m) => m.profit_since_copy_start > best.profit_since_copy_start ? m : best, members[0])?.profit_since_copy_start.toLocaleString()}
              </div>
            </div>
          </div>
        </div>

        <div className="card">
          <div style={{ padding: '20px', borderBottom: '1px solid #f3f4f6' }}>
            <h3>Revenue Breakdown</h3>
          </div>
          <div style={{ padding: '20px' }}>
            <div style={{ marginBottom: '20px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                <span style={{ fontSize: '14px' }}>Member Share (80%)</span>
                <span style={{ fontSize: '14px', fontWeight: 'bold', color: '#10b981' }}>
                  ${dashboardData ? (dashboardData.statistics.total_profit * 0.8).toLocaleString() : '0'}
                </span>
              </div>
              <div style={{ width: '100%', height: '8px', background: '#f3f4f6', borderRadius: '4px' }}>
                <div style={{ width: '80%', height: '100%', background: '#10b981', borderRadius: '4px' }}></div>
              </div>
            </div>

            <div style={{ marginBottom: '20px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                <span style={{ fontSize: '14px' }}>Company Share (20%)</span>
                <span style={{ fontSize: '14px', fontWeight: 'bold', color: '#3b82f6' }}>
                  ${dashboardData ? (dashboardData.statistics.total_profit * 0.2).toLocaleString() : '0'}
                </span>
              </div>
              <div style={{ width: '100%', height: '8px', background: '#f3f4f6', borderRadius: '4px' }}>
                <div style={{ width: '20%', height: '100%', background: '#3b82f6', borderRadius: '4px' }}></div>
              </div>
            </div>

            <div style={{ background: '#f8fafc', padding: '15px', borderRadius: '8px' }}>
              <div style={{ fontSize: '12px', color: '#6b7280', marginBottom: '5px' }}>Total Revenue</div>
              <div style={{ fontSize: '20px', fontWeight: 'bold' }}>
                ${dashboardData?.statistics.total_profit.toLocaleString()}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  const renderErrorReports = () => (
    <div className="main-content">
      <div className="dashboard-header">
        <h1>Error Reports</h1>
        <p>Monitor and resolve trading errors in your group</p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '20px', marginBottom: '20px' }}>
        <div className="stat-card">
          <h3>Total Errors</h3>
          <div className="value">{errorLogs.length}</div>
          <div className="change">Last 24 hours</div>
        </div>
        <div className="stat-card">
          <h3>Unresolved</h3>
          <div className="value" style={{ color: '#ef4444' }}>
            {errorLogs.filter(e => !e.resolved).length}
          </div>
          <div className="change">Requires attention</div>
        </div>
        <div className="stat-card">
          <h3>Resolution Rate</h3>
          <div className="value" style={{ color: '#10b981' }}>
            {errorLogs.length > 0 ? Math.round((errorLogs.filter(e => e.resolved).length / errorLogs.length) * 100) : 0}%
          </div>
          <div className="change">This month</div>
        </div>
      </div>

      <div className="card">
        <div style={{ padding: '20px', borderBottom: '1px solid #f3f4f6' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <h3>Error Log</h3>
            <div style={{ display: 'flex', gap: '10px' }}>
              <select style={{ padding: '8px 12px', borderRadius: '6px', border: '1px solid #d1d5db' }}>
                <option>All Error Types</option>
                <option>Trade Copy Failed</option>
                <option>Symbol Not Found</option>
                <option>Insufficient Margin</option>
                <option>Connection Error</option>
              </select>
              <select style={{ padding: '8px 12px', borderRadius: '6px', border: '1px solid #d1d5db' }}>
                <option>All Status</option>
                <option>Unresolved</option>
                <option>Resolved</option>
              </select>
            </div>
          </div>
        </div>
        <div style={{ overflowX: 'auto' }}>
          <table className="data-table">
            <thead>
              <tr>
                <th>Timestamp</th>
                <th>Error Code</th>
                <th>Symbol</th>
                <th>Account</th>
                <th>Error Message</th>
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
                  <td style={{ fontFamily: 'monospace', fontWeight: 'bold' }}>{error.symbol || 'N/A'}</td>
                  <td>
                    {error.account_id ?
                      members.find(m => m.account_id === error.account_id)?.account_number_masked || 'Unknown'
                      : 'N/A'
                    }
                  </td>
                  <td style={{ maxWidth: '300px' }}>
                    <div style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }} title={error.error_message}>
                      {error.error_message}
                    </div>
                  </td>
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
                        <>
                          <button className="btn btn-outline btn-sm">Retry</button>
                          <button className="btn btn-primary btn-sm">Resolve</button>
                        </>
                      )}
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
            <h3>Recent Critical Errors</h3>
          </div>
          <div style={{ padding: '20px' }}>
            {errorLogs.filter(e => !e.resolved).map((error, index) => (
              <div key={index} style={{ marginBottom: '15px', padding: '12px', background: '#fef2f2', borderRadius: '8px', border: '1px solid #fecaca' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                  <div>
                    <div style={{ fontWeight: 'bold', color: '#dc2626' }}>{error.error_code}</div>
                    <div style={{ fontSize: '12px', color: '#7f1d1d', marginTop: '2px' }}>
                      {error.symbol} • Account: {members.find(m => m.account_id === error.account_id)?.account_number_masked || 'Unknown'}
                    </div>
                    <div style={{ fontSize: '12px', color: '#7f1d1d' }}>
                      {new Date(error.created_at).toLocaleString()} • Retry #{error.retry_count}
                    </div>
                    <div style={{ fontSize: '14px', marginTop: '4px', color: '#7f1d1d' }}>
                      {error.error_message}
                    </div>
                  </div>
                  <button className="btn btn-outline btn-sm" style={{ color: '#dc2626', borderColor: '#dc2626' }}>
                    Resolve
                  </button>
                </div>
              </div>
            ))}

            {errorLogs.filter(e => !e.resolved).length === 0 && (
              <div style={{ textAlign: 'center', padding: '40px', color: '#6b7280' }}>
                <div style={{ fontSize: '48px', marginBottom: '10px' }}>✅</div>
                <div style={{ fontSize: '18px', fontWeight: 'bold', marginBottom: '5px' }}>No Critical Errors</div>
                <div>All systems are running smoothly</div>
              </div>
            )}
          </div>
        </div>

        <div className="card">
          <div style={{ padding: '20px', borderBottom: '1px solid #f3f4f6' }}>
            <h3>Error Prevention</h3>
          </div>
          <div style={{ padding: '20px' }}>
            <div style={{ marginBottom: '20px' }}>
              <h4 style={{ marginBottom: '10px' }}>💡 Prevention Tips</h4>
              <ul style={{ fontSize: '14px', color: '#6b7280', paddingLeft: '20px' }}>
                <li style={{ marginBottom: '8px' }}>Ensure all member accounts have sufficient margin</li>
                <li style={{ marginBottom: '8px' }}>Verify symbol mappings are correct for each broker</li>
                <li style={{ marginBottom: '8px' }}>Monitor broker API connectivity status</li>
                <li style={{ marginBottom: '8px' }}>Keep member account credentials updated</li>
              </ul>
            </div>

            <div style={{ background: '#f0f9ff', padding: '15px', borderRadius: '8px', border: '1px solid #e0f2fe' }}>
              <h4 style={{ marginBottom: '8px', color: '#0369a1' }}>📞 Need Help?</h4>
              <div style={{ fontSize: '14px', color: '#0369a1' }}>
                Contact support if errors persist or if you need assistance with error resolution.
              </div>
              <button className="btn btn-outline btn-sm" style={{ marginTop: '10px', color: '#0369a1', borderColor: '#0369a1' }}>
                Contact Support
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  const renderCurrentScreen = () => {
    switch (currentScreen) {
      case 'dashboard':
        return renderDashboard();
      case 'members':
        return renderMembers();
      case 'trading-controls':
        return renderTradingControls();
      case 'settlements':
        return renderSettlements();
      case 'member-reports':
        return renderMemberReports();
      case 'error-reports':
        return renderErrorReports();
      default:
        return renderDashboard();
    }
  };

  return (
    <div style={{ minHeight: '100vh', background: '#f8fafc' }}>
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
          <option value="dashboard">Dashboard</option>
          <option value="members">Members</option>
          <option value="trading-controls">Trading Controls</option>
          <option value="settlements">Settlements</option>
          <option value="member-reports">Member Reports</option>
          <option value="error-reports">Error Reports</option>
        </select>
      </div>
    </div>
  );
}