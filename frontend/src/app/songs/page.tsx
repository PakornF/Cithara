"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { useAuth } from "@/contexts/AuthContext";
import type { Song, User } from "@/lib/types";
import AudioPlayer from "@/components/AudioPlayer";

const GENRES = ["Pop", "Rock", "Jazz", "Classical", "Hiphop"] as const;
const MOODS = ["Happy", "Sad", "Romantic", "Energetic", "Calm"] as const;
const OCCASIONS = ["Birthday", "Wedding", "Graduation", "Anniversary", "Custom"] as const;
const VOICES = ["Male", "Female"] as const;

export default function SongsPage() {
  const { user: authUser, isLoading: authLoading } = useAuth();
  const router = useRouter();
  const [songs, setSongs] = useState<Song[]>([]);
  const [targetUserId, setTargetUserId] = useState<number | undefined>();
  const [isOwnLibrary, setIsOwnLibrary] = useState(true);
  const [activeTab, setActiveTab] = useState<"library" | "unsaved">("library");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);


  useEffect(() => {
    if (typeof window !== "undefined" && authUser) {
      const params = new URLSearchParams(window.location.search);
      const uid = params.get("user_id");
      const target = uid ? Number(uid) : authUser.id;
      setTargetUserId(target);
      setIsOwnLibrary(!uid || target === authUser.id);
    }
  }, [authUser]);

  const loadSongs = async (userId: number) => {
    try {
      setError(null);
      const data = await api.songs.list(userId);
      setSongs(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load songs");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (targetUserId) {
      loadSongs(targetUserId);
    }
  }, [targetUserId]);

  const displayedSongs = songs.filter((s) => {
    if (!isOwnLibrary) {
      return s.is_saved;
    }
    return activeTab === "library" ? s.is_saved : !s.is_saved;
  });

  const handleSaveToLibrary = async (id: number) => {
    try {
      if (targetUserId) {
        await api.songs.update(id, { is_saved: true });
        await loadSongs(targetUserId);
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to save to library");
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm("Permanently delete this song?")) return;
    try {
      if (targetUserId) {
        await api.songs.delete(id);
        await loadSongs(targetUserId);
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to delete");
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
        <p className="text-stone-400">Loading songs…</p>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-4xl px-4 py-8 sm:px-6 lg:px-8">
      <div className="mb-6 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <h1 className="font-serif text-3xl font-bold text-amber-400">
          {isOwnLibrary ? "My Songs" : "User Library"}
        </h1>
        <div className="flex flex-wrap items-center gap-3">
          <Link
            href="/requests"
            className="rounded-lg bg-amber-600 px-4 py-2 text-sm font-semibold text-stone-950 hover:bg-amber-500 transition-colors"
          >
            Add Song
          </Link>
        </div>
      </div>

      {isOwnLibrary && (
        <div className="mb-6 flex gap-4 border-b border-stone-800">
          <button
            onClick={() => setActiveTab("library")}
            className={`pb-2 text-sm font-medium transition-colors ${
              activeTab === "library"
                ? "border-b-2 border-amber-500 text-amber-500"
                : "text-stone-400 hover:text-stone-300"
            }`}
          >
            My Library
          </button>
          <button
            onClick={() => setActiveTab("unsaved")}
            className={`pb-2 text-sm font-medium transition-colors ${
              activeTab === "unsaved"
                ? "border-b-2 border-amber-500 text-amber-500"
                : "text-stone-400 hover:text-stone-300"
            }`}
          >
            Unsaved Generations
          </button>
        </div>
      )}

      {error && (
        <div className="mb-6 rounded-lg border border-red-800/60 bg-red-950/30 px-4 py-3 text-red-400">
          {error}
        </div>
      )}



      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {displayedSongs.map((s) => (
          <div
            key={s.id}
            className="group rounded-xl border border-stone-800 bg-stone-900/50 p-5 transition hover:border-amber-800/60 flex flex-col"
          >
            <div className="flex items-start justify-between">
              <div>
                <p className="font-semibold text-stone-100">{s.title}</p>
                <p className="mt-1 text-sm text-stone-400">
                  {s.genre} · {s.mood} · {s.occasion}{s.owner__name ? ` · ${s.owner__name}` : ''}
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

            {activeTab === "unsaved" && s.status === "Completed" && s.audio_file_path && (
              <div className="mt-4 border-t border-stone-800 pt-4 flex flex-col gap-3 flex-1 justify-end">
                <AudioPlayer src={s.audio_file_path} />
                <button
                  type="button"
                  onClick={() => handleSaveToLibrary(s.id)}
                  className="w-full rounded-lg bg-emerald-600/90 py-2 text-sm font-semibold text-stone-50 hover:bg-emerald-500 transition-colors"
                >
                  Save to Library
                </button>
              </div>
            )}
          </div>
        ))}
      </div>
      {displayedSongs.length === 0 && (
        <p className="text-center text-stone-500">
          No songs found in this library.
        </p>
      )}
    </div>
  );
}
