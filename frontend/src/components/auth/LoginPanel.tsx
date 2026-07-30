"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import Image from "next/image";

export default function LoginPanel() {
  const [showPassword, setShowPassword] = useState(false);
  const router = useRouter();

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    // Normally handle authentication here.
    // For now, redirect to dashboard.
    router.push("/");
  };

  return (
    <div className="glass-panel rounded-xl p-card-padding flex flex-col space-y-8 animate-in zoom-in duration-500">
      {/* Branding Header */}
      <div className="flex flex-col items-center text-center space-y-2">
        <div className="w-16 h-16 bg-primary rounded-lg flex items-center justify-center mb-2 shadow-sm overflow-hidden p-2">
          <Image
            src="https://lh3.googleusercontent.com/aida-public/AB6AXuAL6cH3SGcqXte3jn-yeCrmOECusuPvkhw1jljN8xxxYHsbfRh3hOWG36TEYoe6aOFkYdI0AOxY8goTpd3mRRJYvDIdiDg25D_QKgjvh33tpTb0yKgyrqsNKSbCweD6S1DW9gY0C0l6Ejjsc02H5rujnwvhec13xlYlkY6YogJJcGAyI41sk5UKXaEurXkpmva1--gHHgB03OqA7o_KArRe8HboZJDh5Enko5tB_M2CPB6jJAtBFsQnGKhSDkjMrlvMfMCBjJyC678"
            alt="EOIS Logo"
            width={48}
            height={48}
            className="w-full h-full object-contain"
          />
        </div>
        <h1 className="font-headline-md text-headline-md text-primary tracking-tight">EOIS</h1>
        <p className="font-body-md text-body-md text-on-surface-variant">Executive Intelligence</p>
      </div>

      {/* Form */}
      <form className="flex flex-col space-y-6" onSubmit={handleLogin}>
        {/* Corporate ID Input */}
        <div className="relative floating-input bg-surface-container-lowest rounded-DEFAULT border border-outline-variant focus-within:border-primary transition-colors duration-200">
          <input
            autoComplete="username"
            className="block w-full px-4 pt-6 pb-2 bg-transparent border-none text-on-surface font-body-md text-body-md focus:ring-0 focus:outline-none"
            id="corporate_id"
            placeholder=" "
            required
            type="text"
          />
          <label
            className="absolute top-4 left-4 font-body-md text-body-md text-on-surface-variant transition-all duration-200 pointer-events-none origin-left"
            htmlFor="corporate_id"
          >
            Corporate ID
          </label>
        </div>

        {/* Passphrase Input */}
        <div className="relative floating-input bg-surface-container-lowest rounded-DEFAULT border border-outline-variant focus-within:border-primary transition-colors duration-200">
          <input
            autoComplete="current-password"
            className="block w-full px-4 pt-6 pb-2 bg-transparent border-none text-on-surface font-body-md text-body-md focus:ring-0 focus:outline-none"
            id="passphrase"
            placeholder=" "
            required
            type={showPassword ? "text" : "password"}
          />
          <label
            className="absolute top-4 left-4 font-body-md text-body-md text-on-surface-variant transition-all duration-200 pointer-events-none origin-left"
            htmlFor="passphrase"
          >
            Secure Passphrase
          </label>
          <button
            aria-label="Toggle password visibility"
            className="absolute right-4 top-1/2 transform -translate-y-1/2 text-on-surface-variant hover:text-primary transition-colors"
            type="button"
            onClick={() => setShowPassword(!showPassword)}
          >
            <span className="material-symbols-outlined text-[20px]">
              {showPassword ? "visibility" : "visibility_off"}
            </span>
          </button>
        </div>

        {/* Actions */}
        <div className="flex flex-col space-y-3 pt-2">
          <button
            className="w-full bg-primary hover:bg-primary-container text-on-primary font-label-md text-label-md py-3 rounded-DEFAULT transition-colors duration-200 flex items-center justify-center space-x-2"
            type="submit"
          >
            <span>Authenticate</span>
            <span className="material-symbols-outlined text-[18px]">arrow_forward</span>
          </button>
          <button
            className="w-full bg-surface-container-lowest hover:bg-surface-container border border-outline-variant text-on-surface font-label-md text-label-md py-3 rounded-DEFAULT transition-colors duration-200 flex items-center justify-center space-x-2"
            type="button"
          >
            <svg className="w-5 h-5" fill="none" viewBox="0 0 21 21" xmlns="http://www.w3.org/2000/svg">
              <path d="M10 0H0V10H10V0Z" fill="#F25022"></path>
              <path d="M21 0H11V10H21V0Z" fill="#7FBA00"></path>
              <path d="M10 11H0V21H10V11Z" fill="#00A4EF"></path>
              <path d="M21 11H11V21H21V11Z" fill="#FFB900"></path>
            </svg>
            <span>Sign in with SSO</span>
          </button>
        </div>
      </form>

      {/* Footer Security Note */}
      <div className="pt-4 border-t border-outline-variant/30 flex items-center justify-center space-x-1.5 text-on-surface-variant opacity-80">
        <span className="material-symbols-outlined text-[14px]">lock</span>
        <span className="font-label-sm text-label-sm uppercase tracking-wider">
          End-to-End Encrypted • Tier 1 Access Only
        </span>
      </div>
    </div>
  );
}
