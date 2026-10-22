"use client";

import { useState } from "react";
import { Download } from "lucide-react";

const DOWNLOAD_OPTIONS = [
  { type: "transactions", label: "All Transactions", description: "Every submitted transaction (pending, approved, and rejected)." },
  { type: "approved-transactions", label: "Approved Transactions", description: "Only approved transactions with buyer and cart details." },
  { type: "attendees", label: "Event Attendees", description: "Per-event attendee list with names, emails, phones, and ticket quantities." },
  { type: "merch-orders", label: "Merch Orders", description: "Confirmed merch orders with sizes, quantities, and buyer addresses." },
  { type: "events", label: "Events", description: "All event items with pricing, dates, and registration status." },
  { type: "merch", label: "Merch Items", description: "All merchandise products with pricing and descriptions." },
  { type: "contacts", label: "Contact Submissions", description: "Messages submitted through the Get In Touch form." },
  { type: "users", label: "Admin Users", description: "All roles and admin accounts." },
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
    <div className="px-8 py-6 max-w-[1200px]">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-[18px] font-semibold tracking-[-0.02em]" style={{ color: '#e5e5e5' }}>Downloads</h1>
        <p className="text-[13px] mt-0.5" style={{ color: '#666' }}>Export data as CSV files for offline analysis</p>
      </div>

      {error && (
        <div className="mb-4 px-3 py-2 rounded-md text-[12px]" style={{ background: 'rgba(239,68,68,0.08)', border: '1px solid rgba(239,68,68,0.15)', color: '#f87171' }}>
          {error}
        </div>
      )}

      {/* Download grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {DOWNLOAD_OPTIONS.map((opt) => (
          <div
            key={opt.type}
            className="flex items-center justify-between gap-4 px-4 py-3.5 rounded-lg transition-colors duration-75 group"
            style={{ border: '1px solid #1e1e1e' }}
            onMouseEnter={(e) => { e.currentTarget.style.borderColor = '#2a2a2a'; e.currentTarget.style.background = '#111'; }}
            onMouseLeave={(e) => { e.currentTarget.style.borderColor = '#1e1e1e'; e.currentTarget.style.background = 'transparent'; }}
          >
            <div className="min-w-0">
              <h3 className="text-[13px] font-medium" style={{ color: '#e5e5e5' }}>{opt.label}</h3>
              <p className="text-[12px] mt-0.5 leading-relaxed" style={{ color: '#555' }}>{opt.description}</p>
            </div>
            <button
              onClick={() => handleDownload(opt.type)}
              disabled={loading !== null}
              className="shrink-0 flex items-center gap-1.5 px-3 py-[6px] rounded-md text-[12px] font-medium transition-colors duration-100 cursor-pointer"
              style={{
                background: '#1a1a1a',
                border: '1px solid #262626',
                color: '#888',
                opacity: loading !== null ? 0.5 : 1,
              }}
              onMouseEnter={(e) => { if (!loading) { e.currentTarget.style.background = '#222'; e.currentTarget.style.color = '#e5e5e5'; } }}
              onMouseLeave={(e) => { e.currentTarget.style.background = '#1a1a1a'; e.currentTarget.style.color = '#888'; }}
            >
              {loading === opt.type ? (
                <span className="flex items-center gap-1.5">
                  <svg className="animate-spin h-3 w-3" viewBox="0 0 24 24" fill="none">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                  </svg>
                  Exporting…
                </span>
              ) : (
                <>
                  <Download size={12} />
                  CSV
                </>
              )}
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
