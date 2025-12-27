"use client";

import { useUser } from "@auth0/nextjs-auth0";
import { useEffect } from "react";

export default function AuthGate({ children }: { children: React.ReactNode }) {
  const { user, isLoading } = useUser();

  useEffect(() => {
    if (!isLoading && !user) {
      // Redirect to the login page
      window.location.href = "/auth/login";
    }
  }, [isLoading, user]);

  // While loading, show "Loading..."
  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        Loading...
      </div>
    );
  }

  // If the user is authorized, we render the application
  return <>{children}</>;
}