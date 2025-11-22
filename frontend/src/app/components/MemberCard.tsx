import React from 'react';
import Image from 'next/image';

interface MemberCardProps {
  name: string;
  email: string;
  joinedDate: string;
  lastActive: string;
  performance: string;
  status: 'active' | 'inactive';
  initials: string;
}

const MemberCard: React.FC<MemberCardProps> = ({
  name,
  email,
  joinedDate,
  lastActive,
  performance,
  status,
  initials
}) => (
  <div className="bg-white rounded-xl shadow-sm p-6">
    <div className="flex items-start justify-between">
      {/* Left section with avatar and info */}
      <div className="flex items-start gap-3">
        <div className="w-10 h-10 bg-gray-100 rounded-full flex items-center justify-center text-gray-600">
          {initials}
        </div>
        <div>
          <h3 className="font-medium text-base">{name}</h3>
          <div className="flex items-center gap-2 text-gray-500 text-sm">
            <Image src="/file.svg" alt="email" width={14} height={14} />
            <span>{email}</span>
          </div>
        </div>
      </div>

      {/* Status badge */}
      <span className={`px-3 py-1 rounded-full text-xs ${
        status === 'active' 
          ? 'bg-black text-white' 
          : 'bg-gray-200 text-gray-600'
      }`}>
        {status}
      </span>
    </div>

    {/* Time and performance info */}
    <div className="mt-6 flex flex-col gap-1 text-sm text-gray-500">
      <div className="flex items-center gap-2">
        <Image src="/file.svg" alt="joined" width={14} height={14} />
        <span>Joined {joinedDate}</span>
      </div>
      <div className="flex items-center gap-2">
        <Image src="/file.svg" alt="active" width={14} height={14} />
        <span>Last active: {lastActive}</span>
      </div>
      {performance && (
        <div className="flex items-center gap-2 text-green-500 mt-2">
          <Image src="/file.svg" alt="performance" width={14} height={14} className="text-green-500" />
          <span>{performance}</span>
        </div>
      )}
    </div>

    {/* Action buttons */}
    <div className="mt-6 flex gap-3">
      <button className="flex items-center gap-2 px-4 py-2 text-sm text-gray-600 hover:bg-gray-50 rounded-lg transition-colors">
        <Image src="/file.svg" alt="message" width={16} height={16} />
        Message
      </button>
      <button className="flex items-center gap-2 px-4 py-2 text-sm text-gray-600 hover:bg-gray-50 rounded-lg transition-colors">
        View Details
      </button>
    </div>
  </div>
);

export default MemberCard;
