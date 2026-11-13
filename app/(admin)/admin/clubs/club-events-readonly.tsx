"use client";
import { EventItem } from "@prisma/client";
import { useState } from "react";
import { Eye, X, DollarSign, Ticket, TrendingUp } from "lucide-react";
import {
  Dialog,
  DialogContent,
  DialogTitle,
} from "@/components/ui/dialog";

interface ApprovedTransaction {
  token: string;
  name: string;
  email: string;
  amount: number;
  created_at: Date;
  events: { name: string; quantity: number; price: number }[];
}

export default function ClubEventsReadOnly({
  clubName,
  events,
  totalTicketsSold,
  totalRevenue,
  approvedTransactions,
}: {
  clubName: string;
  events: EventItem[];
  totalTicketsSold: number;
  totalRevenue: number;
  approvedTransactions: ApprovedTransaction[];
}) {
  const [posterPreviewUrl, setPosterPreviewUrl] = useState<string | null>(null);
  const [showPosterPreview, setShowPosterPreview] = useState(false);
  const [activeTab, setActiveTab] = useState<"events" | "transactions">("events");

  return (
    <>
      <div className="px-8 py-6 max-w-[1200px]">
        {/* Header */}
        <div className="mb-6">
          <h1 className="text-[18px] font-semibold tracking-[-0.02em]" style={{ color: '#e5e5e5' }}>
            {clubName}
          </h1>
          <p className="text-[13px] mt-0.5" style={{ color: '#666' }}>
            View your club&apos;s events, tickets, and revenue
          </p>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-3 gap-4 mb-6">
          <div className="px-4 py-3 rounded-lg" style={{ background: '#141414', border: '1px solid #1e1e1e' }}>
            <div className="flex items-center gap-2 mb-1">
              <div className="w-6 h-6 rounded flex items-center justify-center" style={{ background: 'rgba(129,140,248,0.1)' }}>
                <TrendingUp size={13} style={{ color: '#818cf8' }} />
              </div>
              <p className="text-[11px] font-medium uppercase tracking-wider" style={{ color: '#555' }}>Total Events</p>
            </div>
            <p className="text-[22px] font-semibold" style={{ color: '#e5e5e5' }}>{events.length}</p>
          </div>
          <div className="px-4 py-3 rounded-lg" style={{ background: '#141414', border: '1px solid #1e1e1e' }}>
            <div className="flex items-center gap-2 mb-1">
              <div className="w-6 h-6 rounded flex items-center justify-center" style={{ background: 'rgba(52,211,153,0.1)' }}>
                <Ticket size={13} style={{ color: '#34d399' }} />
              </div>
              <p className="text-[11px] font-medium uppercase tracking-wider" style={{ color: '#555' }}>Tickets Sold</p>
            </div>
            <p className="text-[22px] font-semibold" style={{ color: '#34d399' }}>{totalTicketsSold}</p>
          </div>
          <div className="px-4 py-3 rounded-lg" style={{ background: '#141414', border: '1px solid #1e1e1e' }}>
            <div className="flex items-center gap-2 mb-1">
              <div className="w-6 h-6 rounded flex items-center justify-center" style={{ background: 'rgba(251,191,36,0.1)' }}>
                <DollarSign size={13} style={{ color: '#fbbf24' }} />
              </div>
              <p className="text-[11px] font-medium uppercase tracking-wider" style={{ color: '#555' }}>Approved Revenue</p>
            </div>
            <p className="text-[22px] font-semibold" style={{ color: '#fbbf24' }}>₹{totalRevenue.toLocaleString()}</p>
          </div>
        </div>

        {/* Tab Switcher */}
        <div className="flex items-center gap-1 mb-4 p-0.5 rounded-lg w-fit" style={{ background: '#141414', border: '1px solid #1e1e1e' }}>
          <button
            onClick={() => setActiveTab("events")}
            className="flex items-center gap-2 px-4 py-1.5 rounded-md text-[13px] font-medium transition-all duration-100 cursor-pointer"
            style={{
              background: activeTab === "events" ? '#1e1e1e' : 'transparent',
              color: activeTab === "events" ? '#e5e5e5' : '#666',
            }}
          >
            Events
            <span className="text-[11px] px-1.5 py-0.5 rounded-full" style={{
              background: activeTab === "events" ? '#333' : '#1a1a1a',
              color: activeTab === "events" ? '#e5e5e5' : '#555',
            }}>
              {events.length}
            </span>
          </button>
          <button
            onClick={() => setActiveTab("transactions")}
            className="flex items-center gap-2 px-4 py-1.5 rounded-md text-[13px] font-medium transition-all duration-100 cursor-pointer"
            style={{
              background: activeTab === "transactions" ? '#1e1e1e' : 'transparent',
              color: activeTab === "transactions" ? '#e5e5e5' : '#666',
            }}
          >
            Approved Transactions
            <span className="text-[11px] px-1.5 py-0.5 rounded-full" style={{
              background: activeTab === "transactions" ? '#333' : '#1a1a1a',
              color: activeTab === "transactions" ? '#34d399' : '#555',
            }}>
              {approvedTransactions.length}
            </span>
          </button>
        </div>

        {/* Events Tab */}
        {activeTab === "events" && (
          events.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-16">
              <div className="w-10 h-10 rounded-lg flex items-center justify-center mb-3" style={{ background: '#1a1a1a', border: '1px solid #262626' }}>
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#555" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
                  <rect x="3" y="4" width="18" height="18" rx="2" ry="2" />
                  <line x1="16" y1="2" x2="16" y2="6" />
                  <line x1="8" y1="2" x2="8" y2="6" />
                  <line x1="3" y1="10" x2="21" y2="10" />
                </svg>
              </div>
              <p className="text-[13px] font-medium" style={{ color: '#888' }}>No events yet</p>
              <p className="text-[12px] mt-1" style={{ color: '#555' }}>Contact Breeze Admin to create events for your club</p>
            </div>
          ) : (
            <div className="rounded-lg overflow-hidden" style={{ border: '1px solid #1e1e1e' }}>
              {/* Table header */}
              <div className="grid grid-cols-[2fr_1fr_0.8fr_1fr_0.6fr_0.8fr] gap-4 px-4 py-2.5 text-[11px] font-medium uppercase tracking-wider" style={{ background: '#141414', color: '#555', borderBottom: '1px solid #1e1e1e' }}>
                <div>Event</div>
                <div>Venue</div>
                <div>Price</div>
                <div>Date</div>
                <div>Poster</div>
                <div>Status</div>
              </div>

              {/* Table body */}
              {events.map((event) => (
                <div
                  key={event.id}
                  className="grid grid-cols-[2fr_1fr_0.8fr_1fr_0.6fr_0.8fr] gap-4 px-4 py-3 items-center transition-colors duration-75"
                  style={{ borderBottom: '1px solid #1a1a1a' }}
                  onMouseEnter={(e) => { e.currentTarget.style.background = '#141414'; }}
                  onMouseLeave={(e) => { e.currentTarget.style.background = 'transparent'; }}
                >
                  {/* Event name + description */}
                  <div className="min-w-0">
                    <p className="text-[13px] font-medium truncate" style={{ color: '#e5e5e5' }}>
                      {event.event_name}
                    </p>
                    <p className="text-[12px] truncate mt-0.5" style={{ color: '#555' }}>
                      {event.event_description}
                    </p>
                  </div>

                  {/* Venue */}
                  <div className="text-[13px]" style={{ color: '#888' }}>
                    {event.event_venue || "-"}
                  </div>

                  {/* Price */}
                  <div>
                    <span className="text-[13px] font-medium" style={{ color: '#e5e5e5' }}>
                      ₹{event.event_price}
                    </span>
                    {event.event_pair_price && (
                      <span className="text-[11px] ml-1.5" style={{ color: '#555' }}>
                        / ₹{event.event_pair_price} pair
                      </span>
                    )}
                  </div>

                  {/* Date */}
                  <div>
                    <span className="text-[13px]" style={{ color: '#888' }}>{event.event_date}</span>
                    {event.event_end_date && (
                      <span className="text-[11px] block" style={{ color: '#555' }}>
                        → {event.event_end_date}
                      </span>
                    )}
                  </div>

                  {/* Poster Preview */}
                  <div>
                    {event.image_url ? (
                      <button
                        onClick={() => { setPosterPreviewUrl(event.image_url); setShowPosterPreview(true); }}
                        className="flex items-center gap-1 px-2 py-1 rounded text-[11px] font-medium transition-colors cursor-pointer"
                        style={{ background: 'rgba(129,140,248,0.1)', color: '#818cf8', border: '1px solid rgba(129,140,248,0.2)' }}
                      >
                        <Eye size={11} />
                        View
                      </button>
                    ) : (
                      <span className="text-[11px]" style={{ color: '#444' }}>None</span>
                    )}
                  </div>

                  {/* Status (read-only) */}
                  <div>
                    <span className="text-[11px] px-2 py-0.5 rounded-full font-medium" style={{
                      background: event.registration_open ? 'rgba(52,211,153,0.1)' : 'rgba(248,113,113,0.1)',
                      color: event.registration_open ? '#34d399' : '#f87171',
                      border: `1px solid ${event.registration_open ? 'rgba(52,211,153,0.2)' : 'rgba(248,113,113,0.2)'}`,
                    }}>
                      {event.registration_open ? "Open" : "Closed"}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )
        )}

        {/* Transactions Tab */}
        {activeTab === "transactions" && (
          approvedTransactions.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-16">
              <p className="text-[13px]" style={{ color: '#555' }}>No approved transactions yet</p>
            </div>
          ) : (
            <div className="rounded-lg overflow-hidden" style={{ border: '1px solid #1e1e1e' }}>
              {/* Table header */}
              <div className="grid grid-cols-[1.2fr_1.5fr_2fr_0.8fr] gap-4 px-4 py-2.5 text-[11px] font-medium uppercase tracking-wider" style={{ background: '#141414', color: '#555', borderBottom: '1px solid #1e1e1e' }}>
                <div>Buyer</div>
                <div>Email</div>
                <div>Events</div>
                <div className="text-right">Amount</div>
              </div>

              {/* Table body */}
              {approvedTransactions.map((tx) => (
                <div
                  key={tx.token}
                  className="grid grid-cols-[1.2fr_1.5fr_2fr_0.8fr] gap-4 px-4 py-3 items-center transition-colors duration-75"
                  style={{ borderBottom: '1px solid #1a1a1a' }}
                  onMouseEnter={(e) => { e.currentTarget.style.background = '#141414'; }}
                  onMouseLeave={(e) => { e.currentTarget.style.background = 'transparent'; }}
                >
                  <div className="text-[13px] font-medium truncate" style={{ color: '#e5e5e5' }}>
                    {tx.name}
                  </div>
                  <div className="text-[13px] truncate" style={{ color: '#888' }}>
                    {tx.email}
                  </div>
                  <div className="space-y-0.5">
                    {tx.events.map((ev, i) => (
                      <div key={i} className="text-[12px]" style={{ color: '#aaa' }}>
                        {ev.name} <span style={{ color: '#555' }}>×{ev.quantity}</span>
                      </div>
                    ))}
                  </div>
                  <div className="text-[13px] font-medium text-right" style={{ color: '#34d399' }}>
                    ₹{tx.amount.toLocaleString()}
                  </div>
                </div>
              ))}
            </div>
          )
        )}
      </div>

      {/* Poster Preview Modal */}
      {showPosterPreview && posterPreviewUrl && (
        <Dialog open={showPosterPreview} onOpenChange={setShowPosterPreview}>
          <DialogContent className="sm:max-w-[600px] max-h-[90vh] p-0 gap-0 overflow-hidden" style={{ background: '#141414', border: '1px solid #1e1e1e' }}>
            <div className="flex items-center justify-between px-4 py-3" style={{ borderBottom: '1px solid #1e1e1e' }}>
              <DialogTitle className="text-[13px] font-medium" style={{ color: '#e5e5e5' }}>Poster Preview</DialogTitle>
              <button
                onClick={() => setShowPosterPreview(false)}
                className="p-1 rounded transition-colors cursor-pointer"
                style={{ color: '#888' }}
              >
                <X size={16} />
              </button>
            </div>
            <div className="p-4 flex items-center justify-center" style={{ maxHeight: 'calc(90vh - 60px)', overflow: 'auto' }}>
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img
                src={posterPreviewUrl}
                alt="Event poster preview"
                style={{ maxWidth: '100%', maxHeight: '70vh', objectFit: 'contain', borderRadius: '8px' }}
              />
            </div>
          </DialogContent>
        </Dialog>
      )}
    </>
  );
}
