import React from 'react';

interface GroupCardProps {
  name: string;
  master: string;
  members: number;
  status: 'active' | 'pending';
}

const GroupCard: React.FC<GroupCardProps> = ({ name, master, members, status }) => (
  <div className="bg-[var(--background)] rounded-2xl shadow-lg p-7 pb-5 min-w-[340px] max-w-[360px] flex-1 flex flex-col gap-3 relative text-[var(--foreground)]">
    <div className="flex justify-between items-start">
      <span className="font-bold text-lg text-[var(--foreground)]">{name}</span>
      <span
        className={`rounded-lg px-3 py-0.5 text-sm font-semibold lowercase ml-2 ${
          status === 'active'
            ? 'bg-[var(--foreground)] text-[var(--background)]'
            : 'bg-gray-100 text-[var(--foreground)]'
        }`}
      >
        {status}
      </span>
    </div>
    <div className="flex items-center gap-4 mt-2">
      <span className="flex items-center gap-1.5 text-gray-500 text-[15px]">
        <svg width="18" height="18" fill="none" viewBox="0 0 24 24">
          <path d="M6 20v-2a4 4 0 0 1 4-4h4a4 4 0 0 1 4 4v2" stroke="currentColor" strokeWidth="1.5"/>
          <circle cx="9" cy="7" r="4" stroke="currentColor" strokeWidth="1.5"/>
        </svg>
        {master}
      </span>
      <span className="flex items-center gap-1.5 text-gray-500 text-[15px]">
        <svg width="18" height="18" fill="none" viewBox="0 0 24 24">
          <path d="M6 20v-2a4 4 0 0 1 4-4h4a4 4 0 0 1 4 4v2" stroke="currentColor" strokeWidth="1.5"/>
          <circle cx="12" cy="7" r="4" stroke="currentColor" strokeWidth="1.5"/>
        </svg>
        {members} members
      </span>
    </div>
  </div>
);

export default GroupCard;
