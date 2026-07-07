"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";

const DOWNLOAD_OPTIONS = [
  {
    type: "transactions",
    label: "All Transactions",
    description: "Every submitted transaction — pending, approved, and rejected.",
    icon: "📋",
  },
  {
    type: "approved-transactions",
    label: "Approved Transactions",
    description: "Only approved transactions with buyer and cart details.",
    icon: "✅",
  },
  {
    type: "attendees",
    label: "Event Attendees",
    description: "Per-event attendee list with names, emails, phones, and ticket quantities.",
    icon: "🎟️",
  },
  {
    type: "merch-orders",
    label: "Merch Orders",
    description: "Confirmed merch orders with sizes, quantities, and buyer addresses.",
    icon: "👕",
  },
  {
    type: "events",
    label: "Events",
    description: "All event items with pricing, dates, and registration status.",
    icon: "🎭",
  },
  {
    type: "merch",
    label: "Merch Items",
    description: "All merchandise products with pricing and descriptions.",
    icon: "🛍️",
  },
  {
    type: "contacts",
    label: "Contact Submissions",
    description: "Messages submitted through the Get In Touch form.",
    icon: "✉️",
  },
  {
    type: "users",
    label: "Admin Users",
    description: "All roles and admin accounts.",
    icon: "👤",
  },
];

export default function DownloadPage() {
  const [loading, setLoading] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleDownload = async (type: string) => {
    setLoading(type);
    setError(null);
    try {
      const res = await fetch(`/api/breeze-admin/download?type=${type}`);
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.error || "Download failed");
      }
      const blob = await res.blob();
      const disposition = res.headers.get("Content-Disposition") || "";
      const filenameMatch = disposition.match(/filename="(.+)"/);
      const filename = filenameMatch ? filenameMatch[1] : `${type}.csv`;

      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
    } catch (e: unknown) {
      const message = e instanceof Error ? e.message : "Download failed";
      setError(message);
    } finally {
      setLoading(null);
    }
  };

  return (
    <div className="min-h-screen bg-white">
      <div className="container mx-auto px-6 py-12">
        {/* Header */}
        <div className="mb-12">
          <h1 className="text-4xl font-bold text-[#202020] tracking-tight mb-2">
            Data Download
          </h1>
          <p className="text-gray-500 text-sm">
            Export data as CSV files for offline analysis
          </p>
        </div>

        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
            {error}
          </div>
        )}

        {/* Download cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {DOWNLOAD_OPTIONS.map((opt) => (
            <div
              key={opt.type}
              className="border border-[#202020]/10 rounded-lg p-5 flex items-start gap-4 hover:border-[#202020]/25 transition-colors"
            >
              <span className="text-2xl mt-0.5">{opt.icon}</span>
              <div className="flex-1 min-w-0">
                <h3 className="font-semibold text-[#202020] text-sm">
                  {opt.label}
                </h3>
                <p className="text-gray-500 text-xs mt-1 leading-relaxed">
                  {opt.description}
                </p>
              </div>
              <Button
                onClick={() => handleDownload(opt.type)}
                disabled={loading !== null}
                className="shrink-0 bg-[#202020] hover:bg-[#303030] text-white text-xs px-4 py-2"
              >
                {loading === opt.type ? (
                  <span className="flex items-center gap-1.5">
                    <svg
                      className="animate-spin h-3.5 w-3.5"
                      viewBox="0 0 24 24"
                      fill="none"
                    >
                      <circle
                        className="opacity-25"
                        cx="12"
                        cy="12"
                        r="10"
                        stroke="currentColor"
                        strokeWidth="4"
                      />
                      <path
                        className="opacity-75"
                        fill="currentColor"
                        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
                      />
                    </svg>
                    Exporting…
                  </span>
                ) : (
                  "Download CSV"
                )}
              </Button>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
