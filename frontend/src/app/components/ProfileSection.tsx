import React from 'react';

interface ProfileSectionProps {
  title?: string;
  children: React.ReactNode;
  canEdit?: boolean;
  onEdit?: () => void;
}

const ProfileSection: React.FC<ProfileSectionProps> = ({
  title,
  children,
  canEdit,
  onEdit
}) => (
  <div
    className="rounded-lg shadow-sm"
    style={{
      background: 'var(--background)',
      color: 'var(--foreground)',
      border: '1px solid #e5e7eb',
      borderColor: 'var(--foreground, #e5e7eb)'
    }}
  >
    {title && (
      <div
        className="flex items-center justify-between p-6 border-b"
        style={{ borderBottom: '1px solid #e5e7eb', borderBottomColor: 'var(--foreground, #e5e7eb)' }}
      >
        <h2 className="text-base font-medium" style={{ color: 'var(--foreground)' }}>{title}</h2>
        {canEdit && (
          <button
            onClick={onEdit}
            className="flex items-center gap-1 text-sm"
            style={{ color: 'var(--foreground)' }}
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M16 4L20 8L8 20H4V16L16 4Z" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
            Edit
          </button>
        )}
      </div>
    )}
    <div className="p-6" style={{ color: 'var(--foreground)' }}>
      {children}
    </div>
  </div>
);

export default ProfileSection;
