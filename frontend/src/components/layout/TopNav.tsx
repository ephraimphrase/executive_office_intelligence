"use client";

import React, { useState, useEffect, useRef } from "react";
import Image from "next/image";
import Link from "next/link";
import { searchAll, SearchResult } from "@/lib/api";
import { useAuth } from "@/context/AuthContext";

interface TopNavProps {
  title?: string;
  subtitle?: string;
}

export default function TopNav({ title = "Executive Office Intelligence System", subtitle }: TopNavProps) {
  const [searchQuery, setSearchQuery] = useState("");
  const [results, setResults] = useState<SearchResult[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [showDropdown, setShowDropdown] = useState(false);
  const [showProfileDropdown, setShowProfileDropdown] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const profileDropdownRef = useRef<HTMLDivElement>(null);
  const { user, logout } = useAuth();

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setShowDropdown(false);
      }
      if (profileDropdownRef.current && !profileDropdownRef.current.contains(event.target as Node)) {
        setShowProfileDropdown(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  useEffect(() => {
    const delayDebounceFn = setTimeout(async () => {
      if (searchQuery.length >= 2) {
        setIsSearching(true);
        try {
          const res = await searchAll(searchQuery);
          setResults(res);
          setShowDropdown(true);
        } catch (e) {
          console.error("Search error", e);
        } finally {
          setIsSearching(false);
        }
      } else {
        setResults([]);
        setShowDropdown(false);
      }
    }, 300);

    return () => clearTimeout(delayDebounceFn);
  }, [searchQuery]);

  return (
    <header className="fixed top-0 right-0 left-0 md:left-64 h-20 bg-surface/80 backdrop-blur-xl border-b border-outline-variant/20 z-40 flex justify-between items-center px-margin-mobile md:px-margin-desktop w-full md:w-[calc(100%-16rem)]">
      {/* Search/Product Name (Desktop) */}
      <div className="hidden md:flex items-center gap-6 flex-1">
        <div className="flex flex-col">
          <h2 className="font-headline-md text-headline-md font-bold text-primary truncate max-w-md">
            {title}
          </h2>
          {subtitle && <p className="text-sm text-on-surface-variant">{subtitle}</p>}
        </div>
        <div className="relative w-64 md:w-96" ref={dropdownRef}>
          <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-on-surface-variant text-[20px]">
            search
          </span>
          <input
            className="w-full pl-10 pr-4 py-2 bg-surface-container-low border border-slate-200 rounded-full font-label-md text-label-md focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-colors"
            placeholder="Search insights..."
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onFocus={() => { if (results.length > 0) setShowDropdown(true); }}
          />
          
          {/* Dropdown Results */}
          {showDropdown && (
            <div className="absolute top-full mt-2 w-full bg-surface border border-outline-variant/30 rounded-xl shadow-lg z-50 max-h-96 overflow-y-auto">
              {isSearching ? (
                <div className="p-4 text-center text-on-surface-variant text-sm">Searching...</div>
              ) : results.length > 0 ? (
                <ul className="py-2">
                  {results.map((r, idx) => (
                    <li key={`${r.id}-${idx}`} className="px-4 py-3 hover:bg-surface-container cursor-pointer border-b border-outline-variant/10 last:border-0">
                      <div className="flex items-center gap-3">
                        <span className="material-symbols-outlined text-[18px] text-primary">
                          {r.type === 'document' ? 'description' : r.type === 'email' ? 'mail' : r.type === 'task' ? 'task_alt' : r.type === 'event' ? 'event' : 'label'}
                        </span>
                        <div>
                          <p className="font-label-md text-primary line-clamp-1">{r.title}</p>
                          {r.snippet && <p className="text-[11px] text-on-surface-variant line-clamp-1">{r.snippet}</p>}
                        </div>
                      </div>
                    </li>
                  ))}
                </ul>
              ) : (
                <div className="p-4 text-center text-on-surface-variant text-sm">No results found</div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Search (Mobile) */}
      <div className="flex md:hidden flex-1">
        <div className="relative w-full max-w-[200px]">
          <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-on-surface-variant text-[20px]">
            search
          </span>
          <input
            className="w-full pl-10 pr-4 py-2 bg-surface-container-low border border-slate-200 rounded-full font-label-md text-label-md focus:outline-none focus:border-primary transition-colors"
            placeholder="Search..."
            type="text"
          />
        </div>
      </div>

      {/* Trailing Actions */}
      <div className="flex items-center gap-4">
        <Link href="/notifications" className="p-2 text-on-surface-variant hover:text-primary transition-all duration-300 relative">
          <span className="material-symbols-outlined text-[20px]">notifications</span>
          <span className="absolute top-2 right-2 w-2 h-2 bg-error rounded-full border border-surface"></span>
        </Link>
        <Link href="/settings" className="p-2 text-on-surface-variant hover:text-primary transition-all duration-300">
          <span className="material-symbols-outlined text-[20px]">settings</span>
        </Link>
        <div className="h-8 w-[1px] bg-outline-variant/30 mx-2"></div>
        <div className="relative" ref={profileDropdownRef}>
          <button 
            className="w-10 h-10 rounded-full overflow-hidden border border-slate-200 hover:border-primary transition-colors flex items-center justify-center bg-primary-container text-on-primary-container font-semibold"
            onClick={() => setShowProfileDropdown(!showProfileDropdown)}
          >
            {user?.avatar_url ? (
              <Image
                alt={user?.full_name || "Avatar"}
                className="w-full h-full object-cover"
                src={user.avatar_url}
                width={40}
                height={40}
                unoptimized
              />
            ) : (
              <span>{user?.full_name?.charAt(0) || "U"}</span>
            )}
          </button>
          
          {showProfileDropdown && (
            <div className="absolute right-0 top-full mt-2 w-56 bg-surface border border-outline-variant/30 rounded-xl shadow-lg z-50 py-2">
              <div className="px-4 py-2 border-b border-outline-variant/10">
                <p className="font-semibold text-on-surface line-clamp-1">{user?.full_name}</p>
                <p className="text-xs text-on-surface-variant line-clamp-1">{user?.email}</p>
                <p className="text-[10px] uppercase font-bold text-primary mt-1">{user?.role?.replace('_', ' ')}</p>
              </div>
              <button 
                onClick={() => logout()}
                className="w-full text-left px-4 py-2 mt-1 text-error hover:bg-error/10 transition-colors flex items-center gap-2 font-medium text-sm"
              >
                <span className="material-symbols-outlined text-[18px]">logout</span>
                Sign Out
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
