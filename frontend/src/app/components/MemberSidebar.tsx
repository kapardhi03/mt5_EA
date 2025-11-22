"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useTheme } from "./ThemeContext";
import { ChartIcon, UsersIcon, GridIcon, UserIcon } from "./DashboardIcons";
import Logo from "./Logo";


const MemberSidebar = () => {
  const pathname = usePathname();
  const { theme, toggleTheme } = useTheme();

  return (
    <div className="h-screen w-64 bg-white dark:bg-gray-900 border-r border-gray-200 dark:border-gray-700 shadow-sm flex flex-col">
      <div className="p-6">
        {/* Header */}
        <div className="mb-8">
          <Logo size="md" userType="master" />
        </div>

        {/* Dark Mode Toggle */}
        <div className="flex items-center justify-between mb-6">
          <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Dark Mode</span>
          <button
            onClick={toggleTheme}
            className="rounded-full p-1 border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
            aria-label="Toggle dark mode"
          >
            {theme === 'dark' ? '🌙' : '☀️'}
          </button>
        </div>

        {/* Navigation */}
        <div className="flex-1 space-y-2">
          {/* Dashboard */}
          <Link href="/member/dashboard">
            <div
              className={`flex items-center gap-3 py-3 px-4 rounded-lg text-sm font-medium transition-colors ${
                pathname === '/member/dashboard'
                  ? 'bg-gray-900 dark:bg-gray-100 text-white dark:text-gray-900'
                  : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800'
              }`}
            >
              <GridIcon className="w-5 h-5" />
              <span>Dashboard</span>
            </div>
          </Link>

          {/* My Group */}
          <Link href="/member/mygroup">
            <div
              className={`flex items-center gap-3 py-3 px-4 rounded-lg text-sm font-medium transition-colors ${
                pathname === '/member/mygroup'
                  ? 'bg-gray-900 dark:bg-gray-100 text-white dark:text-gray-900'
                  : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800'
              }`}
            >
              <ChartIcon className="w-5 h-5" />
              <span>My Group</span>
            </div>
          </Link>

          {/* Members */}
          <Link href="/member/members">
            <div
              className={`flex items-center gap-3 py-3 px-4 rounded-lg text-sm font-medium transition-colors ${
                pathname === '/member/members'
                  ? 'bg-gray-900 dark:bg-gray-100 text-white dark:text-gray-900'
                  : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800'
              }`}
            >
              <UsersIcon className="w-5 h-5" />
              <span>Members</span>
            </div>
          </Link>

          {/* Profile */}
          <Link href="/member/profile">
            <div
              className={`flex items-center gap-3 py-3 px-4 rounded-lg text-sm font-medium transition-colors ${
                pathname === '/member/profile'
                  ? 'bg-gray-900 dark:bg-gray-100 text-white dark:text-gray-900'
                  : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800'
              }`}
            >
              <UserIcon className="w-5 h-5" />
              <span>Profile</span>
            </div>
          </Link>
        </div>
      </div>
    </div>
  );
};

export default MemberSidebar;
