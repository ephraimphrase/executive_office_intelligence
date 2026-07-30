"use client";

import React, { useState } from "react";
import { useAuth } from "@/context/AuthContext";
import { verifyMfaCode } from "@/lib/api";

// Populated once an Azure AD App Registration exists (see docs/BACKUP_AND_DR.md's
// sibling setup doc, or ask for the tenant/client IDs) — until then this stays
// unset and the Microsoft button explains why it's disabled rather than failing silently.
const AZURE_TENANT_ID = process.env.NEXT_PUBLIC_AZURE_TENANT_ID;
const AZURE_CLIENT_ID = process.env.NEXT_PUBLIC_AZURE_CLIENT_ID;

function buildMicrosoftAuthorizeUrl(): string | null {
  if (!AZURE_TENANT_ID || !AZURE_CLIENT_ID) return null;
  const redirectUri = `${window.location.origin}/auth/callback`;
  const params = new URLSearchParams({
    client_id: AZURE_CLIENT_ID,
    response_type: "code",
    redirect_uri: redirectUri,
    response_mode: "query",
    scope: "openid profile email User.Read",
  });
  return `https://login.microsoftonline.com/${AZURE_TENANT_ID}/oauth2/v2.0/authorize?${params.toString()}`;
}

export default function LoginPage() {
  const { login } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  // Set once /login responds with an MFA challenge instead of a session.
  const [mfaChallengeToken, setMfaChallengeToken] = useState<string | null>(null);
  const [mfaCode, setMfaCode] = useState("");
  const [mfaLoading, setMfaLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      const res = await fetch("http://localhost:8000/api/auth/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        credentials: "include", // For setting the cookie
        body: JSON.stringify({ email, password }),
      });

      const data = await res.json().catch(() => ({}));

      if (res.ok && data.mfa_required) {
        // Password was correct, but the account has MFA enabled — no session
        // cookie has been set yet, one more step is needed.
        setMfaChallengeToken(data.challenge_token);
      } else if (res.ok) {
        await login();
      } else {
        setError(data.detail || "Invalid email or password");
      }
    } catch {
      setError("Failed to connect to the server. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const handleMfaSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!mfaChallengeToken) return;
    setError(null);
    setMfaLoading(true);

    const result = await verifyMfaCode(mfaChallengeToken, mfaCode);
    if (result.ok) {
      await login();
    } else {
      setError(result.message || "Invalid authentication code");
    }
    setMfaLoading(false);
  };

  const handleMicrosoftSignIn = () => {
    const url = buildMicrosoftAuthorizeUrl();
    if (!url) {
      setError(
        "Microsoft sign-in isn't configured yet — NEXT_PUBLIC_AZURE_TENANT_ID / NEXT_PUBLIC_AZURE_CLIENT_ID are unset."
      );
      return;
    }
    window.location.href = url;
  };

  return (
    <div
      className="min-h-screen flex items-center justify-center bg-cover bg-center relative"
      style={{
        backgroundImage: "url('https://images.unsplash.com/photo-1497215728101-856f4ea42174?auto=format&fit=crop&q=80&w=2560')",
      }}
    >
      <div className="absolute inset-0 bg-gradient-to-br from-primary/90 to-primary/40 backdrop-blur-sm z-0"></div>

      <div className="relative z-10 w-full max-w-md p-8 bg-surface/80 backdrop-blur-xl border border-outline-variant/30 rounded-3xl shadow-2xl">
        <div className="flex flex-col items-center mb-8">
          <div className="w-16 h-16 bg-primary text-on-primary rounded-2xl flex items-center justify-center shadow-lg mb-4">
            <span className="material-symbols-outlined text-3xl">insights</span>
          </div>
          <h1 className="text-3xl font-bold text-on-surface tracking-tight">EOIS</h1>
          <p className="text-on-surface-variant font-medium mt-1">Executive Office Intelligence System</p>
        </div>

        {error && (
          <div className="mb-5 p-4 bg-error/10 border border-error/20 text-error rounded-xl flex items-start gap-3">
            <span className="material-symbols-outlined shrink-0 text-[20px]">error</span>
            <p className="text-sm font-medium">{error}</p>
          </div>
        )}

        {mfaChallengeToken ? (
          <form onSubmit={handleMfaSubmit} className="space-y-5">
            <p className="text-sm text-on-surface-variant">
              Enter the 6-digit code from your authenticator app, or one of your backup codes.
            </p>
            <div>
              <label className="block text-sm font-semibold text-on-surface mb-2">Authentication code</label>
              <div className="relative">
                <span className="absolute left-4 top-1/2 -translate-y-1/2 material-symbols-outlined text-on-surface-variant">
                  password
                </span>
                <input
                  type="text"
                  required
                  autoFocus
                  inputMode="numeric"
                  className="w-full pl-12 pr-4 py-3 bg-surface border border-outline-variant rounded-xl text-on-surface focus:border-primary focus:ring-1 focus:ring-primary outline-none transition-all"
                  placeholder="123456"
                  value={mfaCode}
                  onChange={(e) => setMfaCode(e.target.value)}
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={mfaLoading}
              className="w-full py-3.5 bg-primary text-on-primary font-semibold rounded-xl shadow-md hover:bg-primary/90 focus:ring-4 focus:ring-primary/20 transition-all disabled:opacity-70 flex items-center justify-center gap-2"
            >
              {mfaLoading ? (
                <span className="material-symbols-outlined animate-spin">progress_activity</span>
              ) : (
                "Verify"
              )}
            </button>

            <button
              type="button"
              className="w-full text-sm text-on-surface-variant hover:text-primary transition-colors"
              onClick={() => {
                setMfaChallengeToken(null);
                setMfaCode("");
                setError(null);
              }}
            >
              Back to sign in
            </button>
          </form>
        ) : (
          <>
            <form onSubmit={handleSubmit} className="space-y-5">
              <div>
                <label className="block text-sm font-semibold text-on-surface mb-2">Email address</label>
                <div className="relative">
                  <span className="absolute left-4 top-1/2 -translate-y-1/2 material-symbols-outlined text-on-surface-variant">
                    mail
                  </span>
                  <input
                    type="email"
                    required
                    className="w-full pl-12 pr-4 py-3 bg-surface border border-outline-variant rounded-xl text-on-surface focus:border-primary focus:ring-1 focus:ring-primary outline-none transition-all"
                    placeholder="admin@eois.local"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-semibold text-on-surface mb-2">Password</label>
                <div className="relative">
                  <span className="absolute left-4 top-1/2 -translate-y-1/2 material-symbols-outlined text-on-surface-variant">
                    lock
                  </span>
                  <input
                    type="password"
                    required
                    className="w-full pl-12 pr-4 py-3 bg-surface border border-outline-variant rounded-xl text-on-surface focus:border-primary focus:ring-1 focus:ring-primary outline-none transition-all"
                    placeholder="••••••••"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                  />
                </div>
              </div>

              <div className="flex items-center justify-between text-sm">
                <label className="flex items-center gap-2 cursor-pointer">
                  <input type="checkbox" className="w-4 h-4 rounded border-outline-variant text-primary focus:ring-primary" />
                  <span className="text-on-surface-variant font-medium">Remember me</span>
                </label>
                <a href="#" className="text-primary font-semibold hover:underline">
                  Forgot password?
                </a>
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full py-3.5 bg-primary text-on-primary font-semibold rounded-xl shadow-md hover:bg-primary/90 focus:ring-4 focus:ring-primary/20 transition-all disabled:opacity-70 flex items-center justify-center gap-2"
              >
                {loading ? (
                  <span className="material-symbols-outlined animate-spin">progress_activity</span>
                ) : (
                  "Sign In"
                )}
              </button>
            </form>

            <div className="mt-8 relative">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-outline-variant"></div>
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="px-4 bg-surface/0 text-on-surface-variant font-medium">Single Sign-On</span>
              </div>
            </div>

            <button
              type="button"
              onClick={handleMicrosoftSignIn}
              className="mt-6 w-full py-3 bg-surface border border-outline-variant text-on-surface font-semibold rounded-xl hover:bg-surface-variant/50 transition-all flex items-center justify-center gap-3"
            >
              <img src="https://learn.microsoft.com/en-us/entra/identity-platform/media/howto-add-branding-in-apps/ms-symbollockup_mssymbol_19.svg" alt="Microsoft" className="h-5" />
              Continue with Microsoft
            </button>
          </>
        )}
      </div>
    </div>
  );
}
