"use client";

import React, { useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useAuth } from "@/context/AuthContext";
import { exchangeMicrosoftCode } from "@/lib/api";

export default function MicrosoftAuthCallbackPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { login } = useAuth();
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const run = async () => {
      const code = searchParams.get("code");
      const ssoError = searchParams.get("error_description") || searchParams.get("error");

      if (ssoError) {
        setError(ssoError);
        return;
      }
      if (!code) {
        setError("No authorization code was returned by Microsoft.");
        return;
      }

      // Must exactly match the redirect_uri used to start the flow (see login/page.tsx).
      const redirectUri = `${window.location.origin}/auth/callback`;
      const result = await exchangeMicrosoftCode(code, redirectUri);
      if (result.ok) {
        await login();
      } else {
        setError(result.message || "Could not complete Microsoft sign-in.");
      }
    };
    run();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div className="min-h-screen flex items-center justify-center bg-background">
      <div className="w-full max-w-md p-8 bg-surface border border-outline-variant/30 rounded-3xl shadow-xl text-center">
        {error ? (
          <>
            <div className="w-14 h-14 mx-auto bg-error/10 text-error rounded-2xl flex items-center justify-center mb-4">
              <span className="material-symbols-outlined text-3xl">error</span>
            </div>
            <h1 className="text-xl font-bold text-on-surface mb-2">Sign-in failed</h1>
            <p className="text-sm text-on-surface-variant mb-6">{error}</p>
            <button
              onClick={() => router.push("/login")}
              className="w-full py-3 bg-primary text-on-primary font-semibold rounded-xl hover:bg-primary/90 transition-all"
            >
              Back to sign in
            </button>
          </>
        ) : (
          <>
            <span className="material-symbols-outlined text-4xl text-primary animate-spin mb-4 inline-block">
              progress_activity
            </span>
            <h1 className="text-xl font-bold text-on-surface">Completing sign-in…</h1>
            <p className="text-sm text-on-surface-variant mt-1">Verifying your Microsoft account.</p>
          </>
        )}
      </div>
    </div>
  );
}
