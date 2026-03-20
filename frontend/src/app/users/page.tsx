"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import type { User } from "@/lib/types";

export default function UsersPage() {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [email, setEmail] = useState("");
  const [name, setName] = useState("");
  const [submitting, setSubmitting] = useState(false);

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

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email.trim() || !name.trim()) return;
    setSubmitting(true);
    try {
      await api.users.create({
        email: email.trim(),
        name: name.trim(),
        google_id: `demo-${Date.now()}`,
      });
      setEmail("");
      setName("");
      setShowForm(false);
      await load();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to create user");
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
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
        <button
          type="button"
          onClick={() => setShowForm(!showForm)}
          className="rounded-lg bg-amber-600 px-4 py-2 text-sm font-semibold text-stone-950 hover:bg-amber-500 transition-colors"
        >
          {showForm ? "Cancel" : "Add User"}
        </button>
      </div>

      {error && (
        <div className="mb-6 rounded-lg border border-red-800/60 bg-red-950/30 px-4 py-3 text-red-400">
          {error}
        </div>
      )}

      {showForm && (
        <form
          onSubmit={handleCreate}
          className="mb-8 rounded-xl border border-stone-800 bg-stone-900/50 p-6"
        >
          <h2 className="mb-4 font-serif text-lg font-semibold text-amber-400">
            New User
          </h2>
          <div className="grid gap-4 sm:grid-cols-2">
            <div>
              <label className="mb-1 block text-sm text-stone-400">Name</label>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="w-full rounded-lg border border-stone-700 bg-stone-900 px-3 py-2 text-stone-100 placeholder-stone-500 focus:border-amber-600 focus:outline-none focus:ring-1 focus:ring-amber-600"
                placeholder="Alice"
                required
              />
            </div>
            <div>
              <label className="mb-1 block text-sm text-stone-400">Email</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full rounded-lg border border-stone-700 bg-stone-900 px-3 py-2 text-stone-100 placeholder-stone-500 focus:border-amber-600 focus:outline-none focus:ring-1 focus:ring-amber-600"
                placeholder="alice@example.com"
                required
              />
            </div>
          </div>
          <div className="mt-4">
            <button
              type="submit"
              disabled={submitting}
              className="rounded-lg bg-amber-600 px-4 py-2 text-sm font-semibold text-stone-950 hover:bg-amber-500 disabled:opacity-50 transition-colors"
            >
              {submitting ? "Creating…" : "Create User"}
            </button>
          </div>
        </form>
      )}

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {users.map((u) => (
          <div
            key={u.id}
            className="rounded-xl border border-stone-800 bg-stone-900/50 p-5"
          >
            <p className="font-semibold text-stone-100">{u.name}</p>
            <p className="mt-1 text-sm text-stone-400">{u.email}</p>
            <p className="mt-2 text-xs text-stone-500">
              ID: {u.id} · Created {new Date(u.created_at).toLocaleDateString()}
            </p>
          </div>
        ))}
      </div>
      {users.length === 0 && !showForm && (
        <p className="text-center text-stone-500">No users yet. Add one to get started.</p>
      )}
    </div>
  );
}
