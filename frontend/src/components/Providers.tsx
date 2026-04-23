"use client";

import { GoogleOAuthProvider } from "@react-oauth/google";
import { AuthProvider } from "@/contexts/AuthContext";

const googleClientId = (process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID || "").trim();

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <AuthProvider>
      {googleClientId ? (
        <GoogleOAuthProvider clientId={googleClientId}>
          {children}
        </GoogleOAuthProvider>
      ) : (
        children
      )}
    </AuthProvider>
  );
}
