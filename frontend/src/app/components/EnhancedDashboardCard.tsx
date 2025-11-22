import React from 'react';

interface EnhancedDashboardCardProps {
  title: string;
  value: string | number;
  icon: React.ReactNode;
  iconBg: string;
}

const EnhancedDashboardCard: React.FC<EnhancedDashboardCardProps> = ({ 
  title, 
  value, 
  icon,
  iconBg
}) => {
  return (
    <div
      className="rounded-lg shadow-sm p-6"
      style={{
        background: 'var(--background)',
        color: 'var(--foreground)',
        border: '1px solid #e5e7eb',
        borderColor: 'var(--foreground, #e5e7eb)'
      }}
    >
      <div className="flex justify-between items-center mb-6">
        <span className="text-sm" style={{ color: 'var(--foreground)' }}>{title}</span>
        <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${iconBg}`}>
          {icon}
        </div>
      </div>
      <div className="font-medium text-2xl" style={{ color: 'var(--foreground)' }}>{value}</div>
    </div>
  );
};

export default EnhancedDashboardCard;
