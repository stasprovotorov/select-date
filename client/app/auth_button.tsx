"use client";
import Link from "next/link";

export default function AuthButton() {
  return (
    <Link href="/api/auth/login">
      <button>Войти через Auth0</button>
    </Link>
  );
}