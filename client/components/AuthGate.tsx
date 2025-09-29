"use client";

import { useUser } from "@auth0/nextjs-auth0";
import { useEffect } from "react";

export default function AuthGate({ children }: { children: React.ReactNode }) {
  const { user, isLoading } = useUser();

  useEffect(() => {
    if (!isLoading && !user) {
      // Редирект на страницу логина
      window.location.href = "/auth/login";
    }
  }, [isLoading, user]);

  // Пока идёт загрузка — показываем "Загрузка..."
  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        Loading...
      </div>
    );
  }

  // Если пользователь авторизован — рендерим приложение
  return <>{children}</>;
}