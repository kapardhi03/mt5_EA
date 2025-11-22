"use client";
import React, { useState, useEffect } from 'react';
import API_BASE_URL from '@/config/api';

const API_URL = API_BASE_URL; // shared base URL for master API calls

interface MasterPanelProps {
  onLogout: () => void;
  userData: UserData;
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

type Screen = 'dashboard' | 'my-group' | 'members' | 'performance' | 'settings' | 'accounts';

export default function MasterPanel({ onLogout, userData }: MasterPanelProps) {
  const [currentScreen, setCurrentScreen] = useState<Screen>('dashboard');
  const [loading, setLoading] = useState(false);
  const [groupData, setGroupData] = useState({
    name: 'Swing Traders Pro',
    company: 'SwingTrade Inc',
    members: 25,
    activeMembers: 22,
    totalProfit: 45680.50,
    monthlyReturn: 18.5,
    winRate: 75.4,
    avgTradeTime: '3.2 days',
    settlementCycle: 'Weekly',
    nextSettlement: 'Jan 22, 2024',
    profitShare: 30,
    status: 'Active'
  });

  const [recentTrades, setRecentTrades] = useState([
    {
      id: 1,
      symbol: 'EURUSD',
      type: 'BUY',
      volume: 0.10,
      openPrice: 1.0850,
      currentPrice: 1.0875,
      pnl: 250.00,
      openTime: '2024-01-15 14:30',
      status: 'Open',
      copiedBy: 18
    },
    {
      id: 2,
      symbol: 'XAUUSD',
      type: 'SELL',
      volume: 0.02,
      openPrice: 2045.50,
      closePrice: 2040.20,
      pnl: 106.00,
      openTime: '2024-01-15 09:15',
      closeTime: '2024-01-15 15:45',
      status: 'Closed',
      copiedBy: 20
    },
    {
      id: 3,
      symbol: 'GBPUSD',
      type: 'BUY',
      volume: 0.05,
      openPrice: 1.2650,
      closePrice: 1.2630,
      pnl: -100.00,
      openTime: '2024-01-14 16:20',
      closeTime: '2024-01-14 18:30',
      status: 'Closed',
      copiedBy: 15
    }
  ]);

  const [members, setMembers] = useState([
    {
      id: 1,
      name: 'Alex Rodriguez',
      email: 'alex@example.com',
      joinDate: '2024-01-01',
      accountBalance: 5000,
      totalProfit: 850.30,
      roi: 17.0,
      status: 'Active',
      lotMultiplier: 1.0,
      riskLevel: 'Medium'
    },
    {
      id: 2,
      name: 'Emma Wilson',
      email: 'emma@example.com',
      joinDate: '2023-12-15',
      accountBalance: 10000,
      totalProfit: 1650.75,
      roi: 16.5,
      status: 'Active',
      lotMultiplier: 2.0,
      riskLevel: 'High'
    },
    {
      id: 3,
      name: 'Michael Chen',
      email: 'michael@example.com',
      joinDate: '2024-01-10',
      accountBalance: 2500,
      totalProfit: 320.45,
      roi: 12.8,
      status: 'Active',
      lotMultiplier: 0.5,
      riskLevel: 'Low'
    }
  ]);

  // Fetch real data from backend
  useEffect(() => {
    const fetchMasterData = async () => {
      try {
        setLoading(true);
        const token = localStorage.getItem('authToken');
        const userData = localStorage.getItem('userData');

        if (!token || !userData) {
          console.error('No authentication token found');
          return;
        }

  const user = JSON.parse(userData);

        // Fetch master dashboard data
        try {
          const dashboardResponse = await fetch(`${API_URL}/api/v1/masters/${user.id}/dashboard`, {
            method: 'GET',
            headers: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json',
            },
          });

          if (dashboardResponse.ok) {
            const dashboardResult = await dashboardResponse.json();
            if (dashboardResult.success && dashboardResult.data) {
              setGroupData(dashboardResult.data.group_info);
            }
          }
        } catch (error) {
          console.error('Error fetching master dashboard:', error);
        }

        // Fetch recent trades
        try {
          const tradesResponse = await fetch(`${API_URL}/api/v1/masters/${user.id}/trades/recent`, {
            method: 'GET',
            headers: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json',
            },
          });

          if (tradesResponse.ok) {
            const tradesResult = await tradesResponse.json();
            if (tradesResult.success && tradesResult.data) {
              setRecentTrades(tradesResult.data);
            }
          }
        } catch (error) {
          console.error('Error fetching recent trades:', error);
        }

        // Fetch group members
        try {
          const membersResponse = await fetch(`${API_URL}/api/v1/masters/${user.id}/members`, {
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
          console.error('Error fetching members:', error);
        }
      } catch (error) {
        console.error('Error fetching master data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchMasterData();
  }, [userData.id]);

  const showScreen = (screenId: Screen) => {
    setCurrentScreen(screenId);
  };

  const renderSidebar = () => (
    <div className="sidebar">
      <div className="sidebar-header">
        <h3>Master Trader Panel</h3>
        <p>{userData.name}</p>
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
          className={`nav-item ${currentScreen === 'my-group' ? 'active' : ''}`}
          onClick={() => showScreen('my-group')}
        >
          <div className="nav-icon">👥</div>
          My Group
        </a>
        <a
          href="#"
          className={`nav-item ${currentScreen === 'members' ? 'active' : ''}`}
          onClick={() => showScreen('members')}
        >
          <div className="nav-icon">🎯</div>
          Members
        </a>
        <a
          href="#"
          className={`nav-item ${currentScreen === 'performance' ? 'active' : ''}`}
          onClick={() => showScreen('performance')}
        >
          <div className="nav-icon">📈</div>
          Performance
        </a>
        <a
          href="#"
          className={`nav-item ${currentScreen === 'accounts' ? 'active' : ''}`}
          onClick={() => showScreen('accounts')}
        >
          <div className="nav-icon">🏦</div>
          Trading Accounts
        </a>
        <a
          href="#"
          className={`nav-item ${currentScreen === 'settings' ? 'active' : ''}`}
          onClick={() => showScreen('settings')}
        >
          <div className="nav-icon">⚙️</div>
          Settings
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
        <h1>Master Trader Dashboard</h1>
        <p>Welcome back, {userData.name}! Here&apos;s your group performance overview</p>
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <h3>Group Members</h3>
          <div className="value">{groupData.members}</div>
          <div className="change" style={{ color: '#10b981' }}>{groupData.activeMembers} Active</div>
        </div>
        <div className="stat-card">
          <h3>Total Group Profit</h3>
          <div className="value">${groupData.totalProfit.toLocaleString()}</div>
          <div className="change" style={{ color: '#10b981' }}>+{groupData.monthlyReturn}% this month</div>
        </div>
        <div className="stat-card">
          <h3>Win Rate</h3>
          <div className="value">{groupData.winRate}%</div>
          <div className="change">Last 30 days</div>
        </div>
        <div className="stat-card">
          <h3>Next Settlement</h3>
          <div className="value" style={{ fontSize: '16px' }}>{groupData.nextSettlement}</div>
          <div className="change">Weekly cycle</div>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '20px' }}>
        <div className="card">
          <div style={{ padding: '20px', borderBottom: '1px solid #f3f4f6' }}>
            <h3>Recent Trades</h3>
          </div>
          <div style={{ overflowX: 'auto' }}>
            <table className="data-table">
              <thead>
                <tr>
                  <th>Symbol</th>
                  <th>Type</th>
                  <th>Volume</th>
                  <th>Price</th>
                  <th>P&L</th>
                  <th>Copied By</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {recentTrades.map(trade => (
                  <tr key={trade.id}>
                    <td><strong>{trade.symbol}</strong></td>
                    <td>{trade.type}</td>
                    <td>{trade.volume}</td>
                    <td>{trade.status === 'Open' ? trade.currentPrice : trade.closePrice}</td>
                    <td style={{ color: trade.pnl >= 0 ? '#10b981' : '#ef4444' }}>
                      {trade.pnl >= 0 ? '+' : ''}${trade.pnl.toFixed(2)}
                    </td>
                    <td>{trade.copiedBy} members</td>
                    <td>
                      <span className={`status-badge ${trade.status === 'Open' ? 'status-pending' : 'status-active'}`}>
                        {trade.status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <div className="card">
          <div style={{ padding: '20px', borderBottom: '1px solid #f3f4f6' }}>
            <h3>Quick Actions</h3>
          </div>
          <div style={{ padding: '20px' }}>
            <button className="btn btn-primary" style={{ width: '100%', marginBottom: '10px' }}>
              Open New Trade
            </button>
            <button className="btn btn-outline" style={{ width: '100%', marginBottom: '10px' }}>
              Close All Positions
            </button>
            <button className="btn btn-outline" style={{ width: '100%', marginBottom: '10px' }}>
              Send Group Message
            </button>
            <button className="btn btn-secondary" style={{ width: '100%' }}>
              Export Trade History
            </button>
          </div>
        </div>
      </div>
    </div>
  );

  const renderMyGroup = () => (
    <div className="main-content">
      <div className="dashboard-header">
        <h1>My Trading Group</h1>
        <p>Manage your group settings and member access</p>
      </div>

      <div className="card">
        <div className="card-header">
          <h3>Group Information</h3>
          <button className="btn btn-primary btn-sm">Edit Group</button>
        </div>

        <div className="form-grid">
          <div className="form-group">
            <label>Group Name</label>
            <input type="text" value={groupData.name} readOnly />
          </div>
          <div className="form-group">
            <label>Company Name</label>
            <input type="text" value={groupData.company} readOnly />
          </div>
          <div className="form-group">
            <label>Profit Share %</label>
            <input type="text" value={`${groupData.profitShare}%`} readOnly />
          </div>
          <div className="form-group">
            <label>Settlement Cycle</label>
            <input type="text" value={groupData.settlementCycle} readOnly />
          </div>
        </div>

        <div className="alert alert-info">
          <strong>Group Status:</strong> Your group is currently active and accepting new members.
          API connection is stable with 45ms latency.
        </div>
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <h3>Total Members</h3>
          <div className="value">{groupData.members}</div>
          <div className="change">3 pending approvals</div>
        </div>
        <div className="stat-card">
          <h3>Active Copiers</h3>
          <div className="value">{groupData.activeMembers}</div>
          <div className="change">Currently following trades</div>
        </div>
        <div className="stat-card">
          <h3>Average ROI</h3>
          <div className="value">{groupData.monthlyReturn}%</div>
          <div className="change">Monthly performance</div>
        </div>
        <div className="stat-card">
          <h3>Group Rating</h3>
          <div className="value">4.8/5</div>
          <div className="change">Based on member feedback</div>
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
            <p>Manage your group members and their EA trading settings</p>
          </div>
          <div style={{ display: 'flex', gap: '10px' }}>
            <button className="btn btn-outline">Export List</button>
            <button className="btn btn-primary">Send Message</button>
          </div>
        </div>
      </div>

      <div className="card">
        <div className="card-header">
          <h3>Active Members</h3>
          <div style={{ display: 'flex', gap: '10px' }}>
            <select style={{ padding: '8px 12px', borderRadius: '6px', border: '1px solid #d1d5db' }}>
              <option>All Members</option>
              <option>Active</option>
              <option>Paused</option>
              <option>High Performers</option>
            </select>
            <input type="text" placeholder="Search members..." style={{ padding: '8px 12px', borderRadius: '6px', border: '1px solid #d1d5db' }} />
          </div>
        </div>

        <table className="data-table">
          <thead>
            <tr>
              <th>Member</th>
              <th>Join Date</th>
              <th>Account Balance</th>
              <th>Total Profit</th>
              <th>ROI</th>
              <th>Lot Multiplier</th>
              <th>Risk Level</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {members.map(member => (
              <tr key={member.id}>
                <td>
                  <div>
                    <strong>{member.name}</strong>
                    <div style={{ fontSize: '12px', color: '#6b7280' }}>{member.email}</div>
                  </div>
                </td>
                <td>{member.joinDate}</td>
                <td>${member.accountBalance.toLocaleString()}</td>
                <td style={{ color: '#10b981' }}>+${member.totalProfit.toFixed(2)}</td>
                <td style={{ color: '#10b981' }}>+{member.roi}%</td>
                <td>{member.lotMultiplier}x</td>
                <td>
                  <span className={`status-badge ${
                    member.riskLevel === 'High' ? 'status-rejected' :
                    member.riskLevel === 'Medium' ? 'status-pending' : 'status-active'
                  }`}>
                    {member.riskLevel}
                  </span>
                </td>
                <td><span className="status-badge status-active">{member.status}</span></td>
                <td>
                  <div style={{ display: 'flex', gap: '5px' }}>
                    <button className="btn btn-outline btn-sm">View</button>
                    <button className="btn btn-outline btn-sm">Message</button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );

  const renderPerformance = () => (
    <div className="main-content">
      <div className="dashboard-header">
        <h1>Performance Analytics</h1>
        <p>Detailed analysis of your trading performance and member results</p>
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <h3>Total Trades</h3>
          <div className="value">156</div>
          <div className="change">This month: 23</div>
        </div>
        <div className="stat-card">
          <h3>Win Rate</h3>
          <div className="value">{groupData.winRate}%</div>
          <div className="change" style={{ color: '#10b981' }}>+2.3% vs last month</div>
        </div>
        <div className="stat-card">
          <h3>Avg. Trade Duration</h3>
          <div className="value">{groupData.avgTradeTime}</div>
          <div className="change">Swing trading style</div>
        </div>
        <div className="stat-card">
          <h3>Max Drawdown</h3>
          <div className="value">8.5%</div>
          <div className="change">Within risk limits</div>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
        <div className="card">
          <div style={{ padding: '20px', borderBottom: '1px solid #f3f4f6' }}>
            <h3>Monthly Performance</h3>
          </div>
          <div style={{ padding: '20px' }}>
            <div style={{ marginBottom: '15px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span>January 2024</span>
                <span style={{ color: '#10b981' }}>+18.5%</span>
              </div>
            </div>
            <div style={{ marginBottom: '15px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span>December 2023</span>
                <span style={{ color: '#10b981' }}>+12.3%</span>
              </div>
            </div>
            <div style={{ marginBottom: '15px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span>November 2023</span>
                <span style={{ color: '#ef4444' }}>-2.1%</span>
              </div>
            </div>
            <div style={{ marginBottom: '15px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span>October 2023</span>
                <span style={{ color: '#10b981' }}>+9.8%</span>
              </div>
            </div>
          </div>
        </div>

        <div className="card">
          <div style={{ padding: '20px', borderBottom: '1px solid #f3f4f6' }}>
            <h3>Top Performing Symbols</h3>
          </div>
          <div style={{ padding: '20px' }}>
            <div style={{ marginBottom: '15px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span>EURUSD</span>
                <span style={{ color: '#10b981' }}>+$2,450</span>
              </div>
              <div style={{ fontSize: '12px', color: '#6b7280' }}>32 trades • 78% win rate</div>
            </div>
            <div style={{ marginBottom: '15px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span>XAUUSD</span>
                <span style={{ color: '#10b981' }}>+$1,890</span>
              </div>
              <div style={{ fontSize: '12px', color: '#6b7280' }}>18 trades • 72% win rate</div>
            </div>
            <div style={{ marginBottom: '15px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span>GBPUSD</span>
                <span style={{ color: '#10b981' }}>+$980</span>
              </div>
              <div style={{ fontSize: '12px', color: '#6b7280' }}>25 trades • 68% win rate</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  const renderAccounts = () => (
    <div className="main-content">
      <div className="dashboard-header">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <h1>Trading Accounts</h1>
            <p>Manage your master trading accounts</p>
          </div>
          <button className="btn btn-primary">+ Add Account</button>
        </div>
      </div>

      <div className="account-list">
        <div className="account-list-header">
          <h3>Connected Master Accounts</h3>
        </div>

        <div className="account-item">
          <div className="account-info">
            <div className="account-avatar">EX</div>
            <div className="account-details">
              <h4>Account 123456789</h4>
              <p>Exness • Standard • ExnessReal-Server</p>
            </div>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
            <div style={{ textAlign: 'right' }}>
              <div style={{ fontWeight: 'bold' }}>$25,450.80</div>
              <div style={{ fontSize: '12px', color: '#6b7280' }}>Balance</div>
            </div>
            <div style={{ textAlign: 'right' }}>
              <div style={{ fontWeight: 'bold', color: '#10b981' }}>+$4,680.30</div>
              <div style={{ fontSize: '12px', color: '#6b7280' }}>This Month</div>
            </div>
            <span className="status-badge status-active">Connected</span>
            <div className="account-actions">
              <button className="btn btn-outline btn-sm">Settings</button>
              <button className="btn btn-outline btn-sm">View Live</button>
            </div>
          </div>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px', marginTop: '20px' }}>
        <div className="card">
          <div style={{ padding: '20px', borderBottom: '1px solid #f3f4f6' }}>
            <h3>Trading Settings</h3>
          </div>
          <div style={{ padding: '20px' }}>
            <div className="form-group">
              <label>Max Daily Trades</label>
              <input type="number" defaultValue="10" min="1" max="50" />
            </div>

            <div className="form-group">
              <label>Risk Per Trade (%)</label>
              <input type="number" defaultValue="2" min="0.5" max="10" step="0.1" />
            </div>

            <div className="form-group">
              <label>Trading Hours</label>
              <select>
                <option>24/7</option>
                <option>London Session</option>
                <option>NY Session</option>
                <option>Asian Session</option>
              </select>
            </div>

            <button className="btn btn-primary">Save Settings</button>
          </div>
        </div>

        <div className="card">
          <div style={{ padding: '20px', borderBottom: '1px solid #f3f4f6' }}>
            <h3>Account Health</h3>
          </div>
          <div style={{ padding: '20px' }}>
            <div style={{ marginBottom: '15px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span>Connection Status</span>
                <span className="status-badge status-active">Stable</span>
              </div>
            </div>
            <div style={{ marginBottom: '15px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span>Latency</span>
                <span style={{ color: '#10b981' }}>45ms</span>
              </div>
            </div>
            <div style={{ marginBottom: '15px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span>Last Update</span>
                <span>2 seconds ago</span>
              </div>
            </div>
            <div style={{ marginBottom: '15px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span>Open Positions</span>
                <span>3</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  const renderSettings = () => (
    <div className="main-content">
      <div className="dashboard-header">
        <h1>Master Settings</h1>
        <p>Configure your trading group and member access preferences</p>
      </div>

      <div className="card">
        <div style={{ padding: '20px', borderBottom: '1px solid #f3f4f6' }}>
          <h3>Group Settings</h3>
        </div>
        <div style={{ padding: '20px' }}>
          <div className="form-group">
            <label style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <span>Accept New Members</span>
              <label className="toggle-switch">
                <input type="checkbox" defaultChecked />
                <span className="slider"></span>
              </label>
            </label>
          </div>

          <div className="form-group">
            <label style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <span>Auto-approve Members</span>
              <label className="toggle-switch">
                <input type="checkbox" />
                <span className="slider"></span>
              </label>
            </label>
          </div>

          <div className="form-group">
            <label>Minimum Account Balance</label>
            <input type="number" defaultValue="1000" />
          </div>

          <div className="form-group">
            <label>Maximum Members</label>
            <input type="number" defaultValue="100" />
          </div>
        </div>
      </div>

      <div className="card">
        <div style={{ padding: '20px', borderBottom: '1px solid #f3f4f6' }}>
          <h3>Notification Preferences</h3>
        </div>
        <div style={{ padding: '20px' }}>
          <label style={{ display: 'flex', alignItems: 'center', marginBottom: '10px', fontWeight: 'normal' }}>
            <input type="checkbox" style={{ marginRight: '12px' }} defaultChecked /> New member joins
          </label>
          <label style={{ display: 'flex', alignItems: 'center', marginBottom: '10px', fontWeight: 'normal' }}>
            <input type="checkbox" style={{ marginRight: '12px' }} defaultChecked /> Settlement requests
          </label>
          <label style={{ display: 'flex', alignItems: 'center', marginBottom: '10px', fontWeight: 'normal' }}>
            <input type="checkbox" style={{ marginRight: '12px' }} /> Member messages
          </label>
          <label style={{ display: 'flex', alignItems: 'center', marginBottom: '10px', fontWeight: 'normal' }}>
            <input type="checkbox" style={{ marginRight: '12px' }} defaultChecked /> Performance alerts
          </label>
        </div>
      </div>

      <button className="btn btn-primary">Save All Settings</button>
    </div>
  );

  const renderCurrentScreen = () => {
    switch (currentScreen) {
      case 'dashboard':
        return renderDashboard();
      case 'my-group':
        return renderMyGroup();
      case 'members':
        return renderMembers();
      case 'performance':
        return renderPerformance();
      case 'accounts':
        return renderAccounts();
      case 'settings':
        return renderSettings();
      default:
        return renderDashboard();
    }
  };

  return (
    <div style={{ minHeight: '100vh', background: '#f8fafc' }}>
      {renderSidebar()}
      {renderCurrentScreen()}

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
          <option value="dashboard">Master Dashboard</option>
          <option value="my-group">My Group</option>
          <option value="members">Members</option>
          <option value="performance">Performance</option>
          <option value="accounts">Trading Accounts</option>
          <option value="settings">Settings</option>
        </select>
      </div>
    </div>
  );
}