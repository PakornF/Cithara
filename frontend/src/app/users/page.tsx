"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { useAuth } from "@/contexts/AuthContext";
import { useRouter } from "next/navigation";
import type { User } from "@/lib/types";
import Link from "next/link";

export default function UsersPage() {
  const { user: authUser, isLoading: authLoading } = useAuth();
  const router = useRouter();
  const [users, setUsers] = useState<User[]>([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);


  const load = async () => {
    try {
      setError(null);
      const data = await api.users.list();
      setUsers(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load users");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);



  useEffect(() => {
    if (!authLoading && !authUser) {
      router.push("/");
    }
  }, [authUser, authLoading, router]);

  if (authLoading || loading) {
    return (
      <div className="mx-auto max-w-4xl px-4 py-12">
        <p className="text-stone-400">Loading users…</p>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-4xl px-4 py-8 sm:px-6 lg:px-8">
      <div className="mb-8 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <h1 className="font-serif text-3xl font-bold text-amber-400">Users</h1>
        <input
          type="search"
          placeholder="Search by username..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="rounded-lg border border-stone-700 bg-stone-900 px-3 py-2 text-sm text-stone-100 focus:border-amber-600 focus:outline-none w-64"
        />
      </div>

      {error && (
        <div className="mb-6 rounded-lg border border-red-800/60 bg-red-950/30 px-4 py-3 text-red-400">
          {error}
        </div>
      )}



      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {users.filter(u => 
          u.name.toLowerCase().includes(searchQuery.toLowerCase()) || 
          u.email.toLowerCase().includes(searchQuery.toLowerCase())
        ).map((u) => (
          <Link
            key={u.id}
            href={`/songs?user_id=${u.id}`}
            className="block rounded-xl border border-stone-800 bg-stone-900/50 p-5 hover:border-amber-600 transition-colors"
          >
            <p className="font-semibold text-stone-100">{u.name}</p>
            <p className="mt-1 text-sm text-stone-400">{u.email}</p>
          </Link>
        ))}
      </div>
      {users.length === 0 && (
        <p className="text-center text-stone-500">No users yet.</p>
      )}
    </div>
  );
}
