'use client';
import Link from 'next/link';
import { usePathname } from 'next/navigation';

import { useTheme } from './ThemeContext';
import { Switch } from './SettingsComponents';
import Logo from './Logo';


export default function Sidebar() {
  const pathname = usePathname();
  const { theme, toggleTheme } = useTheme();
  const isDark = theme === 'dark';
  return (
    <aside className="w-64 h-screen bg-white dark:bg-gray-900 border-r border-gray-200 dark:border-gray-700 flex flex-col">
      <div className="p-6 border-b border-gray-200 dark:border-gray-700">
        <div className="flex flex-col items-center space-y-4">
          <Logo size="md" userType="admin" />
          <div className="flex items-center space-x-3">
            <span className="text-sm text-gray-600 dark:text-gray-400">
              {isDark ? 'Dark' : 'Light'} Mode
            </span>
            <Switch checked={isDark} onChange={toggleTheme} />
          </div>
        </div>
      </div>
      <nav className="flex-1 p-4">
        <ul className="space-y-2">
          <li>
            <Link
              href="/admin/dashboard"
              className={`flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-colors ${
                pathname === '/admin/dashboard'
                  ? 'bg-gray-900 dark:bg-gray-100 text-white dark:text-gray-900'
                  : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800'
              }`}
            >
              <svg width="20" height="20" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="1.5">
                <rect x="3" y="3" width="18" height="18" rx="4"/>
              </svg>
              Dashboard
            </Link>
          </li>
          <li>
            <Link
              href="/admin/groups"
              className={`flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-colors ${
                pathname === '/admin/groups'
                  ? 'bg-gray-900 dark:bg-gray-100 text-white dark:text-gray-900'
                  : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800'
              }`}
            >
              <svg width="20" height="20" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="1.5">
                <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
                <circle cx="9" cy="7" r="4" />
                <path d="M23 21v-2a4 4 0 0 0-3-3.87" />
                <path d="M16 3.13a4 4 0 0 1 0 7.75" />
              </svg>
              Groups
            </Link>
          </li>
          <li>
            <Link
              href="/admin/masters"
              className={`flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-colors ${
                pathname === '/admin/masters'
                  ? 'bg-gray-900 dark:bg-gray-100 text-white dark:text-gray-900'
                  : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800'
              }`}
            >
              <svg width="20" height="20" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="1.5">
                <path d="M3 3h18v18H3V3z" />
                <path d="M8 16V8m4 8V8m4 8V8" />
              </svg>
              Masters
            </Link>
          </li>
          <li>
            <Link
              href="/admin/approvals"
              className={`flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-colors ${
                pathname === '/admin/approvals'
                  ? 'bg-gray-900 dark:bg-gray-100 text-white dark:text-gray-900'
                  : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800'
              }`}
            >
              <svg width="20" height="20" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="1.5">
                <circle cx="12" cy="12" r="10" />
                <path d="M8 12l2 2 4-4" />
              </svg>
              Approvals
            </Link>
          </li>
          <li>
            <Link
              href="/admin/settings"
              className={`flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-colors ${
                pathname === '/admin/settings'
                  ? 'bg-gray-900 dark:bg-gray-100 text-white dark:text-gray-900'
                  : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800'
              }`}
            >
              <svg width="20" height="20" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="1.5">
                <path d="M19.4 13.5c.04-.5.1-1 .1-1.5s-.06-1-.1-1.5l2.1-1.6a.5.5 0 0 0 .12-.65l-2-3.46a.5.5 0 0 0-.61-.22l-2.5 1a7.07 7.07 0 0 0-2.6-1.5l-.4-2.65A.5.5 0 0 0 13 2h-4a.5.5 0 0 0-.49.42l-.4 2.65a7.07 7.07 0 0 0-2.6 1.5l-2.5-1a.5.5 0 0 0-.61.22l-2 3.46a.5.5 0 0 0 .12.65l2.1 1.6c-.04.5-.1 1-.1 1.5s.06 1 .1 1.5l-2.1 1.6a.5.5 0 0 0-.12.65l2 3.46c.14.24.43.34.61.22l2.5-1a7.07 7.07 0 0 0 2.6 1.5l.4 2.65A.5.5 0 0 0 9 22h4a.5.5 0 0 0 .49-.42l.4-2.65a7.07 7.07 0 0 0 2.6-1.5l2.5 1c.18.12.47.02.61-.22l2-3.46a.5.5 0 0 0-.12-.65l-2.1-1.6Z" />
                <circle cx="12" cy="12" r="3" />
              </svg>
              Settings
            </Link>
          </li>
        </ul>
      </nav>
    </aside>
  );
}
