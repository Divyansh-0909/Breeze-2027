"use client";
import { EventItem, Roles } from "@prisma/client";
import { toggleEventRegistration } from "./actions";
import { useTransition, useState } from "react";
import { useRouter } from "next/navigation";
import { Switch } from "@/components/ui/switch";
import { EditEventDialog } from "./edit-event-dialog";

export default function EventTable({
  curr_club,
  events,
}: {
  curr_club: Roles;
  events: EventItem[];
}) {
  const [isPending, startTransition] = useTransition();
  const router = useRouter();
  const [selectedEvent, setSelectedEvent] = useState<EventItem | null>(null);
  const [dialogOpen, setDialogOpen] = useState(false);

  if (events.length === 0) {
    return (
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
        <p className="text-[12px] mt-1" style={{ color: '#555' }}>Create your first event to get started</p>
      </div>
    );
  }

  return (
    <>
      <div className="rounded-lg overflow-hidden" style={{ border: '1px solid #1e1e1e' }}>
        {/* Table header */}
        <div className="grid grid-cols-[2fr_1.2fr_1fr_1fr_100px] gap-4 px-4 py-2.5 text-[11px] font-medium uppercase tracking-wider" style={{ background: '#141414', color: '#555', borderBottom: '1px solid #1e1e1e' }}>
          <div>Event</div>
          <div>Venue</div>
          <div>Price</div>
          <div>Date</div>
          <div>Status</div>
        </div>

        {/* Table body */}
        {events.map((event) => (
          <div
            key={event.id}
            className="grid grid-cols-[2fr_1.2fr_1fr_1fr_100px] gap-4 px-4 py-3 items-center cursor-pointer transition-colors duration-75"
            style={{ borderBottom: '1px solid #1a1a1a' }}
            onClick={() => { setSelectedEvent(event); setDialogOpen(true); }}
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

            {/* Registration toggle */}
            <div className="flex items-center gap-2" onClick={(e) => e.stopPropagation()}>
              <Switch
                checked={event.registration_open}
                disabled={isPending}
                className="data-[state=checked]:bg-emerald-600 data-[state=unchecked]:bg-[#333] [&>span]:bg-white h-[18px] w-[32px] [&>span]:h-[14px] [&>span]:w-[14px]"
                onCheckedChange={(checked) => {
                  startTransition(async () => {
                    await toggleEventRegistration(event.id, checked);
                    router.refresh();
                  });
                }}
              />
              <span className="text-[11px] font-medium" style={{ color: event.registration_open ? '#34d399' : '#666' }}>
                {event.registration_open ? "Open" : "Closed"}
              </span>
            </div>
          </div>
        ))}
      </div>

      <EditEventDialog
        event={selectedEvent}
        open={dialogOpen}
        onOpenChange={setDialogOpen}
        curr_club={curr_club}
      />
    </>
  );
}
