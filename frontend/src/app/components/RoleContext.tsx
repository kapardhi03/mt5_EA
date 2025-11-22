'use client';
import React, { createContext, useContext, useState } from "react";

export type UserRole = "admin" | "master" | "slave" | "user" | null;

interface RoleContextType {
  role: UserRole;
  setRole: (role: UserRole) => void;
}

const RoleContext = createContext<RoleContextType>({
  role: null,
  setRole: () => {},
});

export function RoleProvider({ children }: { children: React.ReactNode }) {
  const [role, setRole] = useState<UserRole>(null);

  return (
    <RoleContext.Provider value={{ role, setRole }}>
      {children}
    </RoleContext.Provider>
  );
}

export function useRole() {
  const context = useContext(RoleContext);
  if (!context) {
    throw new Error('useRole must be used within a RoleProvider');
  }
  return context.role;
}

export function useSetRole() {
  const context = useContext(RoleContext);
  if (!context) {
    throw new Error('useSetRole must be used within a RoleProvider');
  }
  return context.setRole;
}