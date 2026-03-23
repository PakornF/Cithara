"use client";

import { useAuth } from "@/contexts/AuthContext";
import Link from "next/link";
import { useEffect } from "react";
import { useRouter } from "next/navigation";

export default function DashboardIndex() {
  const { user, isLoading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isLoading && !user) {
      router.push("/");
    }
  }, [user, isLoading, router]);

  if (isLoading || !user) {
    return (
      <div className="min-h-[calc(100vh-3.5rem)] flex items-center justify-center">
        <div className="text-amber-400/50">Loading...</div>
      </div>
    );
  }

  return (
    <div className="min-h-[calc(100vh-3.5rem)] relative overflow-hidden bg-stone-950 text-stone-100">
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-amber-900/20 via-stone-950 to-stone-950" />
      
      <div className="relative mx-auto max-w-6xl px-4 py-16 sm:px-6 lg:px-8">
        <header className="mb-12 text-center md:text-left">
          <h1 className="text-4xl md:text-5xl font-serif font-bold tracking-tight text-transparent bg-clip-text bg-gradient-to-r from-amber-200 to-amber-500">
            Welcome back, {user.name}
          </h1>
          <p className="mt-4 text-lg text-stone-400 max-w-2xl">
            This is your Cithara dashboard. Generate amazing AI songs in seconds, manage your library, and share with the world.
          </p>
        </header>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <Link href="/requests" className="group block">
            <div className="h-full relative overflow-hidden rounded-2xl border border-stone-800/50 bg-stone-900/40 p-8 backdrop-blur transition-all duration-300 hover:border-amber-500/50 hover:bg-stone-800/60 hover:-translate-y-1 hover:shadow-[0_0_30px_-5px_var(--tw-shadow-color)] shadow-amber-900/20">
              <div className="absolute top-0 right-0 p-4 opacity-10 transition-opacity group-hover:opacity-20 text-6xl">✨</div>
              <h2 className="text-2xl font-serif font-semibold text-amber-500 mb-2">Create New</h2>
              <p className="text-stone-400 text-sm leading-relaxed">
                Generate a completely new song using state-of-the-art AI. Just type a prompt, choose your mood, and let the magic happen.
              </p>
            </div>
          </Link>

          <Link href="/songs" className="group block">
            <div className="h-full relative overflow-hidden rounded-2xl border border-stone-800/50 bg-stone-900/40 p-8 backdrop-blur transition-all duration-300 hover:border-amber-500/50 hover:bg-stone-800/60 hover:-translate-y-1 hover:shadow-[0_0_30px_-5px_var(--tw-shadow-color)] shadow-amber-900/20">
              <div className="absolute top-0 right-0 p-4 opacity-10 transition-opacity group-hover:opacity-20 text-6xl">🎵</div>
              <h2 className="text-2xl font-serif font-semibold text-amber-500 mb-2">My Library</h2>
              <p className="text-stone-400 text-sm leading-relaxed">
                Browse your collection of generated songs. Listen to your past hits, manage your favorites, or share them with friends.
              </p>
            </div>
          </Link>

          <Link href="/users" className="group block">
            <div className="h-full relative overflow-hidden rounded-2xl border border-stone-800/50 bg-stone-900/40 p-8 backdrop-blur transition-all duration-300 hover:border-amber-500/50 hover:bg-stone-800/60 hover:-translate-y-1 hover:shadow-[0_0_30px_-5px_var(--tw-shadow-color)] shadow-amber-900/20">
              <div className="absolute top-0 right-0 p-4 opacity-10 transition-opacity group-hover:opacity-20 text-6xl">👥</div>
              <h2 className="text-2xl font-serif font-semibold text-amber-500 mb-2">Community</h2>
              <p className="text-stone-400 text-sm leading-relaxed">
                Explore a list of other creators and view public user profiles. Discover new music shared by the community.
              </p>
            </div>
          </Link>
        </div>
      </div>
    </div>
  );
}
