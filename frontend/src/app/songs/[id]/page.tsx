"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { api } from "@/lib/api";
import type { SongDetail } from "@/lib/types";

export default function SongDetailPage() {
  const params = useParams();
  const id = Number(params.id);
  const [song, setSong] = useState<SongDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [shareUrl, setShareUrl] = useState<string | null>(null);
  const [creatingShare, setCreatingShare] = useState(false);

  useEffect(() => {
    if (!id || isNaN(id)) return;
    (async () => {
      try {
        setError(null);
        const data = await api.songs.get(id);
        setSong(data);
      } catch (e) {
        setError(e instanceof Error ? e.message : "Failed to load song");
      } finally {
        setLoading(false);
      }
    })();
  }, [id]);

  const handleCreateShare = async () => {
    if (!song) return;
    setCreatingShare(true);
    try {
      const { token } = await api.songs.createShareLink(song.id);
      const url =
        typeof window !== "undefined"
          ? `${window.location.origin}/share/${token}`
          : `/share/${token}`;
      setShareUrl(url);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to create share link");
    } finally {
      setCreatingShare(false);
    }
  };

  const copyShareUrl = () => {
    if (!shareUrl) return;
    navigator.clipboard.writeText(shareUrl);
  };

  if (loading) {
    return (
      <div className="mx-auto max-w-2xl px-4 py-12">
        <p className="text-stone-400">Loading song…</p>
      </div>
    );
  }

  if (error || !song) {
    return (
      <div className="mx-auto max-w-2xl px-4 py-12">
        <p className="text-red-400">{error || "Song not found"}</p>
        <Link href="/songs" className="mt-4 inline-block text-amber-400 hover:underline">
          ← Back to songs
        </Link>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-2xl px-4 py-8 sm:px-6 lg:px-8">
      <Link
        href="/songs"
        className="mb-6 inline-block text-sm text-stone-400 hover:text-amber-400"
      >
        ← Back to songs
      </Link>

      <div className="rounded-xl border border-stone-800 bg-stone-900/50 p-6">
        <h1 className="font-serif text-2xl font-bold text-amber-400">
          {song.title}
        </h1>
        <p className="mt-2 text-stone-400">
          {song.genre} · {song.mood} · {song.occasion} · {song.voice_type}
        </p>
        <span
          className={`mt-3 inline-block rounded-full px-3 py-1 text-sm font-medium ${
            song.status === "Completed"
              ? "bg-emerald-900/50 text-emerald-400"
              : song.status === "Failed" || song.status === "TimedOut"
                ? "bg-red-900/50 text-red-400"
                : "bg-amber-900/50 text-amber-400"
          }`}
        >
          {song.status}
        </span>

        {song.owner && (
          <p className="mt-4 text-sm text-stone-500">
            Owner: {song.owner.name}
          </p>
        )}

        {song.custom_story && (
          <div className="mt-6">
            <h3 className="text-sm font-medium text-stone-400">Custom story</h3>
            <p className="mt-1 text-stone-300">{song.custom_story}</p>
          </div>
        )}

        {song.audio_file_path && (
          <div className="mt-6">
            <h3 className="text-sm font-medium text-stone-400">Audio</h3>
            <p className="mt-1 text-stone-300">{song.audio_file_path}</p>
          </div>
        )}

        <div className="mt-8 border-t border-stone-800 pt-6">
          <h3 className="text-sm font-medium text-stone-400">Share this song</h3>
          {shareUrl ? (
            <div className="mt-2 flex flex-wrap items-center gap-2">
              <input
                type="text"
                readOnly
                value={shareUrl}
                className="flex-1 min-w-0 rounded-lg border border-stone-700 bg-stone-900 px-3 py-2 text-sm text-stone-300"
              />
              <button
                type="button"
                onClick={copyShareUrl}
                className="rounded-lg bg-amber-600 px-4 py-2 text-sm font-semibold text-stone-950 hover:bg-amber-500"
              >
                Copy link
              </button>
            </div>
          ) : (
            <button
              type="button"
              onClick={handleCreateShare}
              disabled={creatingShare}
              className="mt-2 rounded-lg bg-amber-600 px-4 py-2 text-sm font-semibold text-stone-950 hover:bg-amber-500 disabled:opacity-50"
            >
              {creatingShare ? "Creating…" : "Generate share link"}
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
