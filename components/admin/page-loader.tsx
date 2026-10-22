"use client";

import { Loader2 } from "lucide-react";

export default function AdminPageLoader({
  title = "Loading...",
  subtitle = "Fetching latest records from database",
}: {
  title?: string;
  subtitle?: string;
}) {
  return (
    <div className="px-8 py-6 max-w-[1400px] w-full animate-in fade-in-50 duration-200">
      {/* Top Header Skeleton */}
      <div className="flex items-center justify-between mb-6 pb-4" style={{ borderBottom: "1px solid #1a1a1a" }}>
        <div className="space-y-1.5">
          <div className="flex items-center gap-2.5">
            <div className="h-5 w-32 rounded bg-neutral-800/60 animate-pulse" />
            <div className="flex items-center gap-1.5 px-2 py-0.5 rounded-full text-[11px] font-medium" style={{ background: "#161616", border: "1px solid #222", color: "#888" }}>
              <Loader2 className="animate-spin" size={11} />
              <span>Syncing</span>
            </div>
          </div>
          <div className="h-3.5 w-52 rounded bg-neutral-900/80 animate-pulse" />
        </div>
        <div className="h-8 w-24 rounded bg-neutral-800/40 animate-pulse" />
      </div>

      {/* Metrics Row Skeleton */}
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-3 mb-6">
        {[1, 2, 3, 4].map((i) => (
          <div
            key={i}
            className="p-3.5 rounded-lg space-y-2"
            style={{ background: "#111111", border: "1px solid #1a1a1a" }}
          >
            <div className="h-3 w-16 rounded bg-neutral-800/40 animate-pulse" />
            <div className="h-6 w-24 rounded bg-neutral-800/70 animate-pulse" />
          </div>
        ))}
      </div>

      {/* Filter / Search Bar Skeleton */}
      <div className="flex items-center justify-between gap-3 mb-4">
        <div className="h-8 w-64 rounded bg-neutral-900/90 animate-pulse" style={{ border: "1px solid #1a1a1a" }} />
        <div className="flex items-center gap-2">
          <div className="h-8 w-20 rounded bg-neutral-900/70 animate-pulse" />
          <div className="h-8 w-20 rounded bg-neutral-900/70 animate-pulse" />
        </div>
      </div>

      {/* Table Skeleton */}
      <div className="rounded-lg overflow-hidden" style={{ border: "1px solid #1a1a1a", background: "#0d0d0d" }}>
        {/* Table Header */}
        <div className="h-9 px-4 flex items-center gap-6" style={{ background: "#121212", borderBottom: "1px solid #1a1a1a" }}>
          <div className="h-3 w-20 rounded bg-neutral-800/50 animate-pulse" />
          <div className="h-3 w-28 rounded bg-neutral-800/50 animate-pulse" />
          <div className="h-3 w-24 rounded bg-neutral-800/50 animate-pulse" />
          <div className="h-3 w-20 rounded bg-neutral-800/50 animate-pulse" />
          <div className="h-3 w-16 rounded bg-neutral-800/50 animate-pulse ml-auto" />
        </div>

        {/* Table Rows */}
        <div className="divide-y divide-[#161616]">
          {[1, 2, 3, 4, 5, 6].map((i) => (
            <div key={i} className="px-4 py-3.5 flex items-center gap-6">
              <div className="h-3.5 w-24 rounded bg-neutral-800/60 animate-pulse" />
              <div className="h-3.5 w-36 rounded bg-neutral-800/40 animate-pulse" />
              <div className="h-3.5 w-28 rounded bg-neutral-800/30 animate-pulse" />
              <div className="h-5 w-16 rounded-full bg-neutral-800/50 animate-pulse" />
              <div className="h-3.5 w-16 rounded bg-neutral-800/40 animate-pulse ml-auto" />
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
