"use client";

import React, { ReactNode, useEffect } from "react";
import { useAuth } from "@/context/AuthContext";
import { usePathname, useRouter } from "next/navigation";

export function ProtectedRoute({ children }: { children: ReactNode }) {
  const { isAuthenticated, isLoading } = useAuth();
  const pathname = usePathname();
  const router = useRouter();

  useEffect(() => {
    if (!isLoading && !isAuthenticated && pathname !== "/login") {
      router.replace("/login");
    }
  }, [isLoading, isAuthenticated, pathname, router]);

  if (pathname === "/login") {
    return <>{children}</>;
  }

  if (isLoading || !isAuthenticated) {
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

  return <>{children}</>;
}
