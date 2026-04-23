"use client";

import Link from "next/link";
import { useAuth } from "@/contexts/AuthContext";
import { usePathname } from "next/navigation";

export function AuthNav() {
  const { user, logout } = useAuth();
  const pathname = usePathname();

  if (pathname === "/") {
    return (
      <nav className="border-b border-amber-900/40 bg-stone-900/80 backdrop-blur">
        <div className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8">
          <div className="flex h-14 items-center justify-between">
            <Link
              href="/"
              className="text-xl font-serif font-bold tracking-tight text-amber-400 hover:text-amber-300"
            >
              Cithara
            </Link>

          </div>
        </div>
      </nav>
    );
  }

  return (
    <nav className="border-b border-amber-900/40 bg-stone-900/80 backdrop-blur">
      <div className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8">
        <div className="flex h-14 items-center justify-between">
          <Link
            href="/dashboard"
            className="text-xl font-serif font-bold tracking-tight text-amber-400 hover:text-amber-300"
          >
            Cithara
          </Link>
          <div className="flex items-center gap-6">
            <Link
              href="/dashboard"
              className="text-sm font-medium text-stone-400 hover:text-amber-400"
            >
              Dashboard
            </Link>
            <Link
              href="/users"
              className="text-sm font-medium text-stone-400 hover:text-amber-400"
            >
              Users
            </Link>
            <Link
              href="/songs"
              className="text-sm font-medium text-stone-400 hover:text-amber-400"
            >
              Songs
            </Link>
            <Link
              href="/requests"
              className="text-sm font-medium text-stone-400 hover:text-amber-400"
            >
              Generate
            </Link>
            {user ? (
              <div className="flex items-center gap-3">
                <span className="text-sm text-stone-400">{user.name}</span>
                <button
                  type="button"
                  onClick={() => {
                    logout();
                    window.location.href = "/";
                  }}
                  className="text-sm text-stone-500 hover:text-red-400"
                >
                  Logout
                </button>
              </div>
            ) : (
              <Link
                href="/"
                className="text-sm font-medium text-amber-400 hover:text-amber-300"
              >
                Login
              </Link>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
}
