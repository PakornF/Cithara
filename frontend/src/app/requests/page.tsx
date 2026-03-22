"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { useAuth } from "@/contexts/AuthContext";
import type { MusicGenerationRequest, User } from "@/lib/types";

const GENRES = ["Pop", "Rock", "Jazz", "Classical", "Hiphop"] as const;
const MOODS = ["Happy", "Sad", "Romantic", "Energetic", "Calm"] as const;
const OCCASIONS = ["Birthday", "Wedding", "Graduation", "Anniversary", "Custom"] as const;
const VOICES = ["Male", "Female"] as const;

export default function RequestsPage() {
  const { user: authUser, isLoading: authLoading } = useAuth();
  const router = useRouter();
  const [requests, setRequests] = useState<MusicGenerationRequest[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(true);
  const [form, setForm] = useState({
    title: "",
    genre: "Pop",
    mood: "Happy",
    occasion: "Birthday",
    voice_type: "Female",
    custom_story: "",
  });
  const [submitting, setSubmitting] = useState(false);

  const [now, setNow] = useState(Date.now());
  useEffect(() => {
    const int = setInterval(() => setNow(Date.now()), 1000);
    return () => clearInterval(int);
  }, []);

  const getProgress = (r: MusicGenerationRequest) => {
    if (r.status === 'Completed') return 100;
    if (r.status === 'Failed' || r.status === 'TimedOut' || r.status === 'Rejected') return 0;
    const elapsedMs = Math.max(0, now - new Date(r.submitted_at).getTime());
    return Math.min(99, Math.floor(elapsedMs / 1200)); 
  };

  const loadRequests = async () => {
    if (!authUser?.id) {
      setRequests([]);
      setLoading(false);
      return;
    }
    try {
      setError(null);
      const data = await api.requests.list(authUser.id);
      setRequests(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load requests");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadRequests();
  }, [authUser?.id]);

  useEffect(() => {
    if (!authUser?.id) return;
    const hasActive = requests.some(r => r.status === "Pending" || r.status === "InProgress");
    if (!hasActive) return;

    const interval = setInterval(async () => {
      try {
        const data = await api.requests.list(authUser.id);
        setRequests(data);
      } catch (e) {
        // ignore errors during background poll
      }
    }, 5000);
    return () => clearInterval(interval);
  }, [authUser?.id, requests]);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!authUser?.id || !form.title.trim()) return;
    setSubmitting(true);
    try {
      await api.requests.create({
        ...form,
        user_id: authUser.id,
        title: form.title.trim(),
        custom_story: form.custom_story || undefined,
      });
      setForm((f) => ({
        ...f,
        title: "",
        custom_story: "",
      }));
      await loadRequests();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to create request");
    } finally {
      setSubmitting(false);
    }
  };

  useEffect(() => {
    if (!authLoading && !authUser) {
      router.push("/");
    }
  }, [authUser, authLoading, router]);

  if (authLoading || loading) {
    return (
      <div className="mx-auto max-w-4xl px-4 py-12">
        <p className="text-stone-400">Loading…</p>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-4xl px-4 py-8 sm:px-6 lg:px-8">
      <div className="mb-6 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <h1 className="font-serif text-3xl font-bold text-amber-400">
          Generate Song
        </h1>
      </div>

      {error && (
        <div className="mb-6 rounded-lg border border-red-800/60 bg-red-950/30 px-4 py-3 text-red-400">
          {error}
        </div>
      )}

      <div className="mb-10 rounded-xl border border-stone-800 bg-stone-900/50 p-6">
        <button
          type="button"
          onClick={() => setShowForm(!showForm)}
          className="mb-4 font-serif text-lg font-semibold text-amber-400 hover:text-amber-300"
        >
          {showForm ? "− Hide form" : "+ New generation request"}
        </button>

        {showForm && (
          <form onSubmit={handleCreate} className="space-y-4">
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
              <div className="sm:col-span-2">
                <label className="mb-1 block text-sm text-stone-400">Title *</label>
                <input
                  type="text"
                  value={form.title}
                  onChange={(e) =>
                    setForm((f) => ({ ...f, title: e.target.value }))
                  }
                  className="w-full rounded-lg border border-stone-700 bg-stone-900 px-3 py-2 text-stone-100 placeholder-stone-500 focus:border-amber-600 focus:outline-none focus:ring-1 focus:ring-amber-600"
                  placeholder="Wedding Waltz"
                  required
                />
              </div>

              <div>
                <label className="mb-1 block text-sm text-stone-400">Genre</label>
                <select
                  value={form.genre}
                  onChange={(e) =>
                    setForm((f) => ({ ...f, genre: e.target.value }))
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
                  onChange={(e) =>
                    setForm((f) => ({ ...f, mood: e.target.value }))
                  }
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
                    setForm((f) => ({ ...f, occasion: e.target.value }))
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
                    setForm((f) => ({ ...f, voice_type: e.target.value }))
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
            <div>
              <label className="mb-1 block text-sm text-stone-400">
                Custom story (optional, max 1000 chars)
              </label>
              <textarea
                value={form.custom_story}
                onChange={(e) =>
                  setForm((f) => ({ ...f, custom_story: e.target.value }))
                }
                rows={3}
                maxLength={1000}
                className="w-full rounded-lg border border-stone-700 bg-stone-900 px-3 py-2 text-stone-100 placeholder-stone-500 focus:border-amber-600 focus:outline-none focus:ring-1 focus:ring-amber-600"
                placeholder="A song for our first dance..."
              />
            </div>
            <button
              type="submit"
              disabled={submitting}
              className="rounded-lg bg-amber-600 px-6 py-2.5 text-sm font-semibold text-stone-950 hover:bg-amber-500 disabled:opacity-50 transition-colors"
            >
              {submitting ? "Submitting…" : "Submit generation request"}
            </button>
          </form>
        )}
      </div>

      <h2 className="mb-4 font-serif text-xl font-semibold text-amber-400">
        Recent requests
      </h2>
      <div className="space-y-4">
        {requests.map((r) => (
          <div
            key={r.id}
            className="rounded-xl border border-stone-800 bg-stone-900/50 p-5"
          >
            <div className="flex flex-wrap items-start justify-between gap-4">
              <div>
                <p className="font-semibold text-stone-100">{r.title}</p>
                <p className="mt-1 text-sm text-stone-400">
                  {r.genre} · {r.mood} · {r.occasion}
                  {r.user__name && ` · ${r.user__name}`}
                </p>
                <span
                  className={`mt-2 inline-block rounded-full px-2 py-0.5 text-xs font-medium ${
                    r.status === "Completed"
                      ? "bg-emerald-900/50 text-emerald-400"
                      : r.status === "Failed" || r.status === "TimedOut"
                        ? "bg-red-900/50 text-red-400"
                        : r.status === "InProgress"
                          ? "bg-blue-900/50 text-blue-400"
                          : "bg-amber-900/50 text-amber-400"
                  }`}
                >
                  {r.status}
                  {(r.status === "InProgress" || r.status === "Pending") && ` (${getProgress(r)}%)`}
                  {r.is_retry && " (retry)"}
                </span>
                {r.error_message && (
                  <p className="mt-2 text-sm text-red-400">{r.error_message}</p>
                )}
              </div>
              <p className="text-xs text-stone-500">
                {new Date(r.submitted_at).toLocaleString()}
              </p>
            </div>
          </div>
        ))}
      </div>
      {requests.length === 0 && (
        <p className="text-center text-stone-500">
          No generation requests yet. Submit one above.
        </p>
      )}
    </div>
  );
}
