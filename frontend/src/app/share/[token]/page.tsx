"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { api } from "@/lib/api";
import type { SharedSong } from "@/lib/types";
import AudioPlayer from "@/components/AudioPlayer";

export default function SharePage() {
  const params = useParams();
  const token = params.token as string;
  const [song, setSong] = useState<SharedSong | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!token) return;
    (async () => {
      try {
        setError(null);
        const data = await api.share.get(token);
        setSong(data);
      } catch (e) {
        setError(e instanceof Error ? e.message : "Failed to load shared song");
      } finally {
        setLoading(false);
      }
    })();
  }, [token]);

  if (loading) {
    return (
      <div className="mx-auto max-w-2xl px-4 py-24 text-center">
        <p className="text-stone-400">Loading shared song…</p>
      </div>
    );
  }

  if (error || !song) {
    return (
      <div className="mx-auto max-w-2xl px-4 py-24 text-center">
        <div className="rounded-xl border border-red-900/50 bg-red-950/30 p-8">
          <h1 className="font-serif text-2xl font-bold text-red-400">
            Song unavailable
          </h1>
          <p className="mt-2 text-stone-400">
            {error || "This song may have been deleted or the share link is no longer active."}
          </p>
          <Link
            href="/"
            className="mt-6 inline-block rounded-lg bg-amber-600 px-6 py-2 text-sm font-semibold text-stone-950 hover:bg-amber-500"
          >
            Go home
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-2xl px-4 py-16 sm:px-6 lg:px-8">
      <div className="rounded-xl border border-amber-800/40 bg-gradient-to-br from-amber-950/30 to-stone-900/80 p-8 text-center">
        <p className="text-sm uppercase tracking-wider text-amber-500">
          Shared with you
        </p>
        <h1 className="mt-4 font-serif text-4xl font-bold text-amber-400">
          {song.title}
        </h1>
        <p className="mt-2 text-stone-400">
          {song.genre} · {song.mood}
        </p>
        {song.audio_file_path ? (
          <div className="mt-8 text-left">
            <AudioPlayer src={song.audio_file_path} />
          </div>
        ) : (
          <p className="mt-8 text-sm text-stone-500">
            This song does not have audio attached yet.
          </p>
        )}
        <Link
          href="/"
          className="mt-10 inline-block rounded-lg border border-amber-700/60 px-6 py-2 text-sm font-semibold text-amber-400 hover:bg-amber-900/30"
        >
          Create your own with Cithara
        </Link>
      </div>
    </div>
  );
}
