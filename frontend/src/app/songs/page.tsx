"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { api } from "@/lib/api";
import { useAuth } from "@/contexts/AuthContext";
import type { Song, User } from "@/lib/types";

const GENRES = ["Pop", "Rock", "Jazz", "Classical", "Hiphop"] as const;
const MOODS = ["Happy", "Sad", "Romantic", "Energetic", "Calm"] as const;
const OCCASIONS = ["Birthday", "Wedding", "Graduation", "Anniversary", "Custom"] as const;
const VOICES = ["Male", "Female"] as const;

export default function SongsPage() {
  const { user: authUser } = useAuth();
  const [songs, setSongs] = useState<Song[]>([]);
  const [users, setUsers] = useState<User[]>([]);
  const [selectedUserId, setSelectedUserId] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({
    owner_id: 0,
    title: "",
    genre: "Pop",
    mood: "Happy",
    occasion: "Birthday",
    voice_type: "Female",
    custom_story: "",
  });
  const [submitting, setSubmitting] = useState(false);

  const loadUsers = async () => {
    const data = await api.users.list();
    setUsers(data);
    const preferred =
      authUser?.id && data.some((u) => u.id === authUser.id)
        ? authUser.id
        : data[0]?.id;
    if (data.length && preferred) {
      setSelectedUserId(preferred);
      setForm((f) => ({ ...f, owner_id: f.owner_id || preferred }));
    }
  };

  const loadSongs = async () => {
    try {
      setError(null);
      const data = selectedUserId
        ? await api.songs.list(selectedUserId)
        : await api.songs.list();
      setSongs(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load songs");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadUsers();
  }, [authUser?.id]);

  useEffect(() => {
    if (users.length) loadSongs();
    else setLoading(false);
  }, [selectedUserId, users.length]);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.owner_id || !form.title.trim()) return;
    setSubmitting(true);
    try {
      await api.songs.create({
        ...form,
        owner_id: form.owner_id,
        title: form.title.trim(),
        custom_story: form.custom_story || undefined,
      });
      setForm({
        ...form,
        title: "",
        custom_story: "",
      });
      setShowForm(false);
      await loadSongs();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to create song");
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm("Permanently delete this song?")) return;
    try {
      await api.songs.delete(id);
      await loadSongs();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to delete");
    }
  };

  if (loading) {
    return (
      <div className="mx-auto max-w-4xl px-4 py-12">
        <p className="text-stone-400">Loading songs…</p>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-4xl px-4 py-8 sm:px-6 lg:px-8">
      <div className="mb-6 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <h1 className="font-serif text-3xl font-bold text-amber-400">Songs</h1>
        <div className="flex flex-wrap items-center gap-3">
          <select
            value={selectedUserId ?? ""}
            onChange={(e) => setSelectedUserId(Number(e.target.value) || null)}
            className="rounded-lg border border-stone-700 bg-stone-900 px-3 py-2 text-sm text-stone-100 focus:border-amber-600 focus:outline-none"
          >
            <option value="">All users</option>
            {users.map((u) => (
              <option key={u.id} value={u.id}>
                {u.name}
              </option>
            ))}
          </select>
          <button
            type="button"
            onClick={() => setShowForm(!showForm)}
            className="rounded-lg bg-amber-600 px-4 py-2 text-sm font-semibold text-stone-950 hover:bg-amber-500 transition-colors"
          >
            {showForm ? "Cancel" : "Add Song"}
          </button>
        </div>
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
            New Song
          </h2>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <div className="sm:col-span-2">
              <label className="mb-1 block text-sm text-stone-400">Title</label>
              <input
                type="text"
                value={form.title}
                onChange={(e) => setForm({ ...form, title: e.target.value })}
                className="w-full rounded-lg border border-stone-700 bg-stone-900 px-3 py-2 text-stone-100 placeholder-stone-500 focus:border-amber-600 focus:outline-none focus:ring-1 focus:ring-amber-600"
                placeholder="My Song"
                required
              />
            </div>
            <div>
              <label className="mb-1 block text-sm text-stone-400">Owner</label>
              <select
                value={form.owner_id}
                onChange={(e) =>
                  setForm({ ...form, owner_id: Number(e.target.value) })
                }
                className="w-full rounded-lg border border-stone-700 bg-stone-900 px-3 py-2 text-stone-100 focus:border-amber-600 focus:outline-none"
                required
              >
                <option value={0}>Select user</option>
                {users.map((u) => (
                  <option key={u.id} value={u.id}>
                    {u.name}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="mb-1 block text-sm text-stone-400">Genre</label>
              <select
                value={form.genre}
                onChange={(e) =>
                  setForm({ ...form, genre: e.target.value })
                }
                className="w-full rounded-lg border border-stone-700 bg-stone-900 px-3 py-2 text-stone-100 focus:border-amber-600 focus:outline-none"
              >
                {GENRES.map((g) => (
                  <option key={g} value={g}>
                    {g}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="mb-1 block text-sm text-stone-400">Mood</label>
              <select
                value={form.mood}
                onChange={(e) => setForm({ ...form, mood: e.target.value })}
                className="w-full rounded-lg border border-stone-700 bg-stone-900 px-3 py-2 text-stone-100 focus:border-amber-600 focus:outline-none"
              >
                {MOODS.map((m) => (
                  <option key={m} value={m}>
                    {m}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="mb-1 block text-sm text-stone-400">Occasion</label>
              <select
                value={form.occasion}
                onChange={(e) =>
                  setForm({ ...form, occasion: e.target.value })
                }
                className="w-full rounded-lg border border-stone-700 bg-stone-900 px-3 py-2 text-stone-100 focus:border-amber-600 focus:outline-none"
              >
                {OCCASIONS.map((o) => (
                  <option key={o} value={o}>
                    {o}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="mb-1 block text-sm text-stone-400">Voice</label>
              <select
                value={form.voice_type}
                onChange={(e) =>
                  setForm({ ...form, voice_type: e.target.value })
                }
                className="w-full rounded-lg border border-stone-700 bg-stone-900 px-3 py-2 text-stone-100 focus:border-amber-600 focus:outline-none"
              >
                {VOICES.map((v) => (
                  <option key={v} value={v}>
                    {v}
                  </option>
                ))}
              </select>
            </div>
          </div>
          <div className="mt-4">
            <label className="mb-1 block text-sm text-stone-400">
              Custom story (optional, max 1000 chars)
            </label>
            <textarea
              value={form.custom_story}
              onChange={(e) =>
                setForm({ ...form, custom_story: e.target.value })
              }
              rows={2}
              maxLength={1000}
              className="w-full rounded-lg border border-stone-700 bg-stone-900 px-3 py-2 text-stone-100 placeholder-stone-500 focus:border-amber-600 focus:outline-none focus:ring-1 focus:ring-amber-600"
              placeholder="Tell the AI about your song..."
            />
          </div>
          <div className="mt-4">
            <button
              type="submit"
              disabled={submitting}
              className="rounded-lg bg-amber-600 px-4 py-2 text-sm font-semibold text-stone-950 hover:bg-amber-500 disabled:opacity-50 transition-colors"
            >
              {submitting ? "Creating…" : "Create Song"}
            </button>
          </div>
        </form>
      )}

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {songs.map((s) => (
          <div
            key={s.id}
            className="group rounded-xl border border-stone-800 bg-stone-900/50 p-5 transition hover:border-amber-800/60"
          >
            <div className="flex items-start justify-between">
              <div>
                <p className="font-semibold text-stone-100">{s.title}</p>
                <p className="mt-1 text-sm text-stone-400">
                  {s.genre} · {s.mood} · {s.occasion}
                </p>
                <span
                  className={`mt-2 inline-block rounded-full px-2 py-0.5 text-xs font-medium ${
                    s.status === "Completed"
                      ? "bg-emerald-900/50 text-emerald-400"
                      : s.status === "Failed" || s.status === "TimedOut"
                        ? "bg-red-900/50 text-red-400"
                        : "bg-amber-900/50 text-amber-400"
                  }`}
                >
                  {s.status}
                </span>
              </div>
              <div className="flex gap-2 opacity-0 group-hover:opacity-100 transition">
                <Link
                  href={`/songs/${s.id}`}
                  className="rounded px-2 py-1 text-xs font-medium text-amber-400 hover:bg-amber-900/30"
                >
                  View
                </Link>
                <button
                  type="button"
                  onClick={() => handleDelete(s.id)}
                  className="rounded px-2 py-1 text-xs font-medium text-red-400 hover:bg-red-900/30"
                >
                  Delete
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
      {songs.length === 0 && !showForm && (
        <p className="text-center text-stone-500">
          No songs yet. Add a song or create a generation request first.
        </p>
      )}
    </div>
  );
}
