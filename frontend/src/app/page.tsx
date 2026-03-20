"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { GoogleLogin } from "@react-oauth/google";
import Link from "next/link";
import { api } from "@/lib/api";
import { useAuth } from "@/contexts/AuthContext";

type Tab = "login" | "register";

export default function LoginPage() {
  const { login } = useAuth();
  const router = useRouter();

  const [tab, setTab] = useState<Tab>("login");
  const [email, setEmail] = useState("");
  const [name, setName] = useState("");
  const [password, setPassword] = useState("");
  const [code, setCode] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [verificationSent, setVerificationSent] = useState(false);

  const googleClientId =
    (process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID || "").trim();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const user = await api.auth.login({ email, password });
      login(user);
      router.push("/songs");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Login failed");
    } finally {
      setLoading(false);
    }
  };

  const handleRequestVerification = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await api.auth.requestVerification({ email, name, password });
      setVerificationSent(true);
      setCode("");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to send code");
    } finally {
      setLoading(false);
    }
  };

  const handleVerifyAndRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const user = await api.auth.verifyAndRegister({
        email,
        name,
        password,
        code,
      });
      login(user);
      router.push("/songs");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Verification failed");
    } finally {
      setLoading(false);
    }
  };

  const handleGoogleSuccess = async (credential: string) => {
    setError("");
    setLoading(true);
    try {
      const user = await api.auth.google(credential);
      login(user);
      router.push("/songs");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Google sign-in failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="relative min-h-[calc(100vh-3.5rem)] flex items-center justify-center px-4">
      <div className="absolute inset-0 bg-gradient-to-br from-amber-950/20 via-transparent to-violet-950/20" />
      <div className="relative w-full max-w-md">
        <div className="rounded-2xl border border-stone-800 bg-stone-900/80 backdrop-blur p-8 shadow-xl">
          <h1 className="font-serif text-3xl font-bold text-amber-400 text-center">
            Cithara
          </h1>
          <p className="mt-1 text-center text-sm text-stone-400">
            AI-powered song generation
          </p>

          {/* Tabs */}
          <div className="mt-6 flex rounded-lg bg-stone-800/80 p-1">
            <button
              type="button"
              onClick={() => {
                setTab("login");
                setError("");
                setVerificationSent(false);
              }}
              className={`flex-1 rounded-md py-2 text-sm font-medium transition ${
                tab === "login"
                  ? "bg-amber-600 text-stone-950"
                  : "text-stone-400 hover:text-stone-200"
              }`}
            >
              Login
            </button>
            <button
              type="button"
              onClick={() => {
                setTab("register");
                setError("");
                setVerificationSent(false);
              }}
              className={`flex-1 rounded-md py-2 text-sm font-medium transition ${
                tab === "register"
                  ? "bg-amber-600 text-stone-950"
                  : "text-stone-400 hover:text-stone-200"
              }`}
            >
              Create Account
            </button>
          </div>

          {error && (
            <div className="mt-4 rounded-lg border border-red-800/60 bg-red-950/30 px-3 py-2 text-sm text-red-400">
              {error}
            </div>
          )}

          {/* Google OAuth */}
          {googleClientId ? (
            <div className="mt-6">
              <div className="w-full [&>div]:!w-full [&>iframe]:!w-full">
                <GoogleLogin
                  onSuccess={(res) => {
                    if (res.credential) handleGoogleSuccess(res.credential);
                  }}
                  onError={() => setError("Google sign-in was cancelled or failed")}
                  useOneTap={false}
                  theme="filled_black"
                  size="large"
                  width="400"
                  text="continue_with"
                />
              </div>
              <div className="mt-4 flex items-center gap-3">
                <div className="flex-1 h-px bg-stone-700" />
                <span className="text-xs text-stone-500">or</span>
                <div className="flex-1 h-px bg-stone-700" />
              </div>
            </div>
          ) : (
            <p className="mt-4 text-center text-xs text-stone-500">
              Add <code className="rounded bg-stone-800 px-1">NEXT_PUBLIC_GOOGLE_CLIENT_ID</code> for Google sign-in
            </p>
          )}

          {/* Manual Login */}
          {tab === "login" && (
            <form onSubmit={handleLogin} className="mt-4 space-y-4">
              <div>
                <label className="mb-1 block text-sm text-stone-400">Email</label>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full rounded-lg border border-stone-700 bg-stone-900 px-3 py-2 text-stone-100 placeholder-stone-500 focus:border-amber-600 focus:outline-none focus:ring-1 focus:ring-amber-600"
                  placeholder="you@example.com"
                  required
                />
              </div>
              <div>
                <label className="mb-1 block text-sm text-stone-400">Password</label>
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full rounded-lg border border-stone-700 bg-stone-900 px-3 py-2 text-stone-100 placeholder-stone-500 focus:border-amber-600 focus:outline-none focus:ring-1 focus:ring-amber-600"
                  placeholder="••••••••"
                  required
                />
              </div>
              <button
                type="submit"
                disabled={loading}
                className="w-full rounded-lg bg-amber-600 py-2.5 text-sm font-semibold text-stone-950 hover:bg-amber-500 disabled:opacity-50"
              >
                {loading ? "Signing in…" : "Login"}
              </button>
            </form>
          )}

          {/* Create Account */}
          {tab === "register" && (
            <form
              onSubmit={
                verificationSent
                  ? handleVerifyAndRegister
                  : handleRequestVerification
              }
              className="mt-4 space-y-4"
            >
              {!verificationSent ? (
                <>
                  <div>
                    <label className="mb-1 block text-sm text-stone-400">Name</label>
                    <input
                      type="text"
                      value={name}
                      onChange={(e) => setName(e.target.value)}
                      className="w-full rounded-lg border border-stone-700 bg-stone-900 px-3 py-2 text-stone-100 placeholder-stone-500 focus:border-amber-600 focus:outline-none focus:ring-1 focus:ring-amber-600"
                      placeholder="Your name"
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
                      placeholder="you@example.com"
                      required
                    />
                  </div>
                  <div>
                    <label className="mb-1 block text-sm text-stone-400">Password (min 6 chars)</label>
                    <input
                      type="password"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      className="w-full rounded-lg border border-stone-700 bg-stone-900 px-3 py-2 text-stone-100 placeholder-stone-500 focus:border-amber-600 focus:outline-none focus:ring-1 focus:ring-amber-600"
                      placeholder="••••••••"
                      required
                      minLength={6}
                    />
                  </div>
                  <button
                    type="submit"
                    disabled={loading}
                    className="w-full rounded-lg bg-amber-600 py-2.5 text-sm font-semibold text-stone-950 hover:bg-amber-500 disabled:opacity-50"
                  >
                    {loading ? "Sending…" : "Send verification code"}
                  </button>
                </>
              ) : (
                <>
                  <p className="text-sm text-stone-400">
                    We sent a 6-digit code to <strong className="text-stone-200">{email}</strong>.
                    Check your inbox (and spam).
                  </p>
                  <p className="text-xs text-stone-500">
                    Dev mode: code is also printed in the Django terminal.
                  </p>
                  <div>
                    <label className="mb-1 block text-sm text-stone-400">Verification code</label>
                    <input
                      type="text"
                      value={code}
                      onChange={(e) => setCode(e.target.value.replace(/\D/g, "").slice(0, 6))}
                      className="w-full rounded-lg border border-stone-700 bg-stone-900 px-3 py-2 text-stone-100 text-center text-lg tracking-widest placeholder-stone-500 focus:border-amber-600 focus:outline-none focus:ring-1 focus:ring-amber-600"
                      placeholder="000000"
                      maxLength={6}
                      required
                    />
                  </div>
                  <button
                    type="submit"
                    disabled={loading || code.length !== 6}
                    className="w-full rounded-lg bg-amber-600 py-2.5 text-sm font-semibold text-stone-950 hover:bg-amber-500 disabled:opacity-50"
                  >
                    {loading ? "Verifying…" : "Verify & create account"}
                  </button>
                  <button
                    type="button"
                    onClick={() => setVerificationSent(false)}
                    className="w-full text-sm text-stone-400 hover:text-amber-400"
                  >
                    ← Use a different email
                  </button>
                </>
              )}
            </form>
          )}
        </div>
        <p className="mt-6 text-center text-sm text-stone-500">
          <Link href="/songs" className="text-amber-400 hover:underline">
            Continue without logging in
          </Link>{" "}
          (demo mode)
        </p>
      </div>
    </div>
  );
}
