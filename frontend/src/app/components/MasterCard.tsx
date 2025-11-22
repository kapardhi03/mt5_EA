import React from 'react';

interface MasterCardProps {
  name: string;
  email: string;
  group: string;
  members: number;
  description: string;
  status: 'approved';
}

function getInitials(name: string | undefined) {
  if (!name) return '--';
  return name
    .split(' ')
    .map((n) => n[0])
    .join('')
    .toUpperCase();
}

const MasterCard: React.FC<MasterCardProps> = ({ name, email, group, members, description, status }) => (
  <div className="bg-[var(--background)] rounded-2xl shadow-lg p-7 pb-5 min-w-[420px] max-w-[440px] flex-1 flex flex-col gap-3 text-[var(--foreground)]">
    <div className="flex justify-between items-start">
      <div className="flex items-center gap-3.5">
        <div className="w-[38px] h-[38px] rounded-full bg-gray-100 flex items-center justify-center font-semibold text-lg text-[var(--foreground)]">
          {getInitials(name)}
        </div>
        <div className="flex flex-col gap-0.5">
          <span className="font-bold text-[17px] text-[var(--foreground)] flex items-center gap-1.5">
            {name}
            <svg width="16" height="16" fill="none" viewBox="0 0 24 24">
              <path d="M3 3h18v18H3V3z" stroke="#b42309" strokeWidth="1.5"/>
              <path d="M8 16V8m4 8V8m4 8V8" stroke="#b42309" strokeWidth="1.5"/>
            </svg>
          </span>
          <span className="text-gray-500 text-[15px]">{email}</span>
        </div>
      </div>
      <span className={`rounded-lg px-3 py-0.5 text-sm font-semibold lowercase ml-2 ${
        status === 'approved'
          ? 'bg-[var(--foreground)] text-[var(--background)]'
          : 'bg-gray-100 text-[var(--foreground)]'
      }`}>
        {status}
      </span>
    </div>
    <div className="flex items-center gap-2.5 text-gray-500 text-[15px] mt-2">
      <svg width="18" height="18" fill="none" viewBox="0 0 24 24">
        <path d="M6 20v-2a4 4 0 0 1 4-4h4a4 4 0 0 1 4 4v2" stroke="currentColor" strokeWidth="1.5"/>
        <circle cx="12" cy="7" r="4" stroke="currentColor" strokeWidth="1.5"/>
      </svg>
      {group} • {members} members
    </div>
    <div className="text-[var(--foreground)] text-[15px] mt-0.5">{description}</div>
  </div>
);

export default MasterCard;
