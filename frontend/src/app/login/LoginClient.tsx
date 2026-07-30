"use client";

import React from "react";
import LoginPanel from "@/components/auth/LoginPanel";

export default function LoginClient() {
  return (
    <div className="relative min-h-screen w-full flex items-center justify-center overflow-hidden antialiased text-on-surface">
      {/* Background Layer */}
      <div className="absolute inset-0 z-0">
        <div
          className="w-full h-full bg-cover bg-center absolute inset-0"
          style={{
            backgroundImage:
              "url('https://lh3.googleusercontent.com/aida-public/AB6AXuDONB0Mm1acU1IVPWJg5bl01viVVHUKnMoRu9o8jwcczJmqAnXZl_9yfagpbRakqXBqHOUpZxNyQYkxvQZAgELmsqsBPqa4oZFCRU4eLfB5R8QUugSpFyHVAAaqisHtUxtPm_czHj8ovwyqWyRjRjHAENpKYCUV8OrSmwTJhfGvc1s35Q9PyjQDAhl8oCcwMSZwHwxUtXs8qphFCaKkypJgvgZe9PeUs0xbzPtkWCo5Dz48VIs5m5yYPelCAN0u6ri4JY6HzqgF8Zc')",
          }}
        ></div>
        <div className="absolute inset-0 bg-primary/10 backdrop-blur-sm"></div>
      </div>

      {/* Login Panel Container */}
      <div className="relative z-10 w-full max-w-md px-margin-mobile md:px-0">
        <LoginPanel />
      </div>
    </div>
  );
}
