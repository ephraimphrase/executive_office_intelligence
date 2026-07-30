"use client";

import React from "react";
import Image from "next/image";
import Link from "next/link";
import { usePathname } from "next/navigation";

export default function Sidebar() {
  const pathname = usePathname();

  const isActive = (path: string) => {
    if (path === "/" && pathname === "/") return true;
    if (path !== "/" && pathname.startsWith(path)) return true;
    return false;
  };

  const linkBaseClass = "flex items-center gap-4 px-4 py-3 rounded-lg cursor-pointer active:scale-95 transition-all duration-200";
  const linkActiveClass = "bg-secondary-container text-on-secondary-container";
  const linkInactiveClass = "text-on-primary/70 hover:text-on-primary hover:bg-primary-container/50";

  return (
    <nav className="hidden md:flex h-screen w-64 fixed left-0 top-0 bg-primary text-on-primary flex-col border-r border-outline-variant/10 shadow-sm z-50">
      <div className="flex flex-col h-full py-margin-desktop px-4">
        {/* Header/Brand */}
        <div className="flex flex-col items-center mb-12">
          <div className="w-16 h-16 mb-4 rounded-lg overflow-hidden bg-white/10 flex items-center justify-center">
            <Image
              alt="EOIS Logo"
              className="w-full h-full object-contain"
              src="https://lh3.googleusercontent.com/aida-public/AB6AXuAL6cH3SGcqXte3jn-yeCrmOECusuPvkhw1jljN8xxxYHsbfRh3hOWG36TEYoe6aOFkYdI0AOxY8goTpd3mRRJYvDIdiDg25D_QKgjvh33tpTb0yKgyrqsNKSbCweD6S1DW9gY0C0l6Ejjsc02H5rujnwvhec13xlYlkY6YogJJcGAyI41sk5UKXaEurXkpmva1--gHHgB03OqA7o_KArRe8HboZJDh5Enko5tB_M2CPB6jJAtBFsQnGKhSDkjMrlvMfMCBjJyC678"
              width={64}
              height={64}
              unoptimized
            />
          </div>
          <h1 className="font-display-lg text-display-lg font-bold text-on-primary tracking-tight text-center">
            EOIS
          </h1>
          <p className="font-label-sm text-label-sm text-on-primary/70 tracking-widest uppercase mt-1">
            Executive Intelligence
          </p>
        </div>

        {/* Navigation Links */}
        <ul className="flex flex-col gap-2 flex-grow">
          <li>
            <Link
              href="/"
              className={`${linkBaseClass} ${isActive("/") ? linkActiveClass : linkInactiveClass}`}
            >
              <span className={`material-symbols-outlined ${isActive("/") ? "active-icon" : ""}`}>
                dashboard
              </span>
              <span className="font-label-md text-label-md">Dashboard</span>
            </Link>
          </li>
          <li>
            <Link
              href="/calendar"
              className={`${linkBaseClass} ${isActive("/calendar") ? linkActiveClass : linkInactiveClass}`}
            >
              <span className={`material-symbols-outlined ${isActive("/calendar") ? "active-icon" : ""}`}>calendar_today</span>
              <span className="font-label-md text-label-md">Calendar</span>
            </Link>
          </li>
          <li>
            <Link
              href="/tasks"
              className={`${linkBaseClass} ${isActive("/tasks") ? linkActiveClass : linkInactiveClass}`}
            >
              <span className={`material-symbols-outlined ${isActive("/tasks") ? "active-icon" : ""}`}>fact_check</span>
              <span className="font-label-md text-label-md">Tasks</span>
            </Link>
          </li>
          <li>
            <Link
              href="/communications"
              className={`${linkBaseClass} ${isActive("/communications") ? linkActiveClass : linkInactiveClass}`}
            >
              <span className={`material-symbols-outlined ${isActive("/communications") ? "active-icon" : ""}`}>chat</span>
              <span className="font-label-md text-label-md">Communications</span>
            </Link>
          </li>
          <li>
            <Link
              href="/documents"
              className={`${linkBaseClass} ${isActive("/documents") ? linkActiveClass : linkInactiveClass}`}
            >
              <span className={`material-symbols-outlined ${isActive("/documents") ? "active-icon" : ""}`}>description</span>
              <span className="font-label-md text-label-md">Documents</span>
            </Link>
          </li>
          <li>
            <Link
              href="/ai-assistant"
              className={`${linkBaseClass} ${isActive("/ai-assistant") ? linkActiveClass : linkInactiveClass}`}
            >
              <span className={`material-symbols-outlined ${isActive("/ai-assistant") ? "active-icon" : ""}`}>smart_toy</span>
              <span className="font-label-md text-label-md">AI Assistant</span>
            </Link>
          </li>
          <li>
            <Link
              href="/settings"
              className={`${linkBaseClass} ${isActive("/settings") ? linkActiveClass : linkInactiveClass}`}
            >
              <span className={`material-symbols-outlined ${isActive("/settings") ? "active-icon" : ""}`}>settings</span>
              <span className="font-label-md text-label-md">Settings</span>
            </Link>
          </li>
        </ul>

        {/* CTA */}
        <div className="mt-auto pt-6">
          <button className="w-full bg-white text-primary font-label-md text-label-md py-3 rounded-lg flex items-center justify-center gap-2 hover:bg-slate-100 transition-colors shadow-sm">
            <span className="material-symbols-outlined text-[18px]">bolt</span>
            Quick Insight
          </button>
        </div>
      </div>
    </nav>
  );
}
