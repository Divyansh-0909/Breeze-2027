"use client";

import { useEffect, useState } from "react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Mail } from "lucide-react";

interface ContactSubmission {
  id: string;
  created_at: string;
  name: string;
  email: string;
  phone: string;
  message: string;
}

export default function ContactSubmissionsPage() {
  const [submissions, setSubmissions] = useState<ContactSubmission[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedSubmission, setSelectedSubmission] = useState<ContactSubmission | null>(null);

  useEffect(() => { fetchSubmissions(); }, []);

  const fetchSubmissions = async () => {
    try {
      const response = await fetch("/api/contact");
      const data = await response.json();
      setSubmissions(data);
    } catch (error) {
      console.error("Failed to fetch submissions:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="px-8 py-6 max-w-[1200px]">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-[18px] font-semibold tracking-[-0.02em]" style={{ color: '#e5e5e5' }}>Contact</h1>
        <p className="text-[13px] mt-0.5" style={{ color: '#666' }}>Messages from the contact form</p>
      </div>

      {/* Stats */}
      <div className="flex items-center gap-6 mb-6 px-4 py-3 rounded-lg" style={{ background: '#141414', border: '1px solid #1e1e1e' }}>
        <div>
          <p className="text-[11px] font-medium uppercase tracking-wider" style={{ color: '#555' }}>Total Messages</p>
          <p className="text-[20px] font-semibold" style={{ color: '#e5e5e5' }}>{submissions.length}</p>
        </div>
      </div>

      {loading ? (
        <div className="flex items-center justify-center py-16">
          <p className="text-[13px]" style={{ color: '#555' }}>Loading submissions…</p>
        </div>
      ) : submissions.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-16">
          <div className="w-10 h-10 rounded-lg flex items-center justify-center mb-3" style={{ background: '#1a1a1a', border: '1px solid #262626' }}>
            <Mail size={18} style={{ color: '#555' }} />
          </div>
          <p className="text-[13px]" style={{ color: '#555' }}>No contact submissions yet</p>
        </div>
      ) : (
        <div className="rounded-lg overflow-hidden" style={{ border: '1px solid #1e1e1e' }}>
          {/* Header */}
          <div className="grid grid-cols-[1fr_1.2fr_1.5fr_1fr_2fr] gap-3 px-4 py-2.5 text-[11px] font-medium uppercase tracking-wider" style={{ background: '#141414', color: '#555', borderBottom: '1px solid #1e1e1e' }}>
            <div>Date</div>
            <div>Name</div>
            <div>Email</div>
            <div>Phone</div>
            <div>Message</div>
          </div>

          {/* Rows */}
          {submissions.map((submission) => (
            <div
              key={submission.id}
              className="grid grid-cols-[1fr_1.2fr_1.5fr_1fr_2fr] gap-3 px-4 py-3 items-center cursor-pointer transition-colors duration-75"
              style={{ borderBottom: '1px solid #1a1a1a' }}
              onClick={() => setSelectedSubmission(submission)}
              onMouseEnter={(e) => { e.currentTarget.style.background = '#141414'; }}
              onMouseLeave={(e) => { e.currentTarget.style.background = 'transparent'; }}
            >
              <div className="text-[12px]" style={{ color: '#666' }}>
                {new Date(submission.created_at).toLocaleDateString("en-IN", {
                  day: "numeric", month: "short", year: "numeric",
                })}
              </div>
              <div className="text-[13px] font-medium truncate" style={{ color: '#e5e5e5' }}>
                {submission.name}
              </div>
              <div className="text-[13px] truncate" style={{ color: '#888' }}>
                {submission.email}
              </div>
              <div className="text-[13px]" style={{ color: '#888' }}>
                {submission.phone}
              </div>
              <div className="text-[13px] truncate" style={{ color: '#666' }}>
                {submission.message}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Detail dialog */}
      <Dialog open={!!selectedSubmission} onOpenChange={() => setSelectedSubmission(null)}>
        <DialogContent className="max-w-[480px] p-0 gap-0" style={{ background: '#141414', border: '1px solid #1e1e1e', color: '#e5e5e5' }}>
          <DialogHeader className="px-5 py-4" style={{ borderBottom: '1px solid #1e1e1e' }}>
            <DialogTitle className="text-[15px] font-semibold" style={{ color: '#e5e5e5' }}>
              Message from {selectedSubmission?.name}
            </DialogTitle>
          </DialogHeader>
          <div className="p-5 space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-[11px] font-medium uppercase tracking-wider mb-1" style={{ color: '#555' }}>Email</p>
                <a href={`mailto:${selectedSubmission?.email}`} className="text-[13px] hover:underline" style={{ color: '#888' }}>
                  {selectedSubmission?.email}
                </a>
              </div>
              <div>
                <p className="text-[11px] font-medium uppercase tracking-wider mb-1" style={{ color: '#555' }}>Phone</p>
                <p className="text-[13px]" style={{ color: '#888' }}>{selectedSubmission?.phone}</p>
              </div>
            </div>
            <div>
              <p className="text-[11px] font-medium uppercase tracking-wider mb-1.5" style={{ color: '#555' }}>Message</p>
              <p className="text-[13px] leading-relaxed whitespace-pre-wrap p-3 rounded-md" style={{ background: '#0f0f0f', border: '1px solid #1e1e1e', color: '#ccc' }}>
                {selectedSubmission?.message}
              </p>
            </div>
            <div>
              <p className="text-[11px] font-medium uppercase tracking-wider mb-1" style={{ color: '#555' }}>Submitted</p>
              <p className="text-[13px]" style={{ color: '#888' }}>
                {selectedSubmission && new Date(selectedSubmission.created_at).toLocaleDateString("en-IN", {
                  day: "numeric", month: "long", year: "numeric", hour: "2-digit", minute: "2-digit",
                })}
              </p>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
