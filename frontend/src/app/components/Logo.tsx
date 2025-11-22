"use client";

interface LogoProps {
  className?: string;
  size?: "sm" | "md" | "lg";
  showText?: boolean;
  userType?: "admin" | "master" | "user";
}

export default function Logo({ 
  className = "", 
  size = "md", 
  showText = true, 
  userType = "user" 
}: LogoProps) {
  const sizeClasses = {
    sm: "w-5 h-5",
    md: "w-7 h-7", 
    lg: "w-8 h-8"
  };

  const textSizeClasses = {
    sm: "text-sm",
    md: "text-base",
    lg: "text-lg"
  };

  const userTypeLabels = {
    admin: "Admin",
    master: "Master User", 
    user: "User"
  };

  return (
    <div className={`flex items-center gap-3 ${className}`}>
      {/* Logo Icon */}
      <div className={`${sizeClasses[size]} flex items-center justify-center`}>
        <svg 
          viewBox="0 0 24 24" 
          fill="none" 
          stroke="currentColor" 
          strokeWidth="2" 
          strokeLinecap="round" 
          strokeLinejoin="round"
          className="w-full h-full"
        >
          <path d="M3 17V7a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2v10a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2Z" />
          <path d="M7 15V9m5 6V9m5 6V9" />
        </svg>
      </div>
      
      {/* Logo Text */}
      {showText && (
        <div className="flex flex-col">
          <span className={`font-semibold text-gray-900 dark:text-white ${textSizeClasses[size]}`}>
            EA Platform
          </span>
          <span className={`text-xs text-gray-500 dark:text-gray-400 ${size === "sm" ? "text-xs" : "text-sm"}`}>
            {userTypeLabels[userType]}
          </span>
        </div>
      )}
    </div>
  );
}
