"use client";

import React, { ReactNode } from "react";
import { useAuth } from "@/context/AuthContext";
import { usePathname } from "next/navigation";

export function ProtectedRoute({ children }: { children: ReactNode }) {
  const { isAuthenticated, isLoading } = useAuth();
  const pathname = usePathname();

  if (pathname === "/login") {
    return <>{children}</>;
  }

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="flex flex-col items-center">
          <span className="material-symbols-outlined animate-spin text-primary text-4xl mb-4">
            progress_activity
          </span>
          <p className="text-on-surface-variant font-medium animate-pulse">Loading EOIS Workspace...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return null; // The redirect is handled in AuthContext, so we just render nothing to avoid flashing content
  }

  return <>{children}</>;
}
