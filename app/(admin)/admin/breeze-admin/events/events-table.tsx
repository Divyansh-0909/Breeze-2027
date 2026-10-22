"use client";
import { EventItem } from "@prisma/client";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import { deleteEvent, toggleEventRegistration } from "./actions";
import { Button } from "@/components/ui/button";
import { useTransition } from "react";
import { useRouter } from "next/navigation";
import { EditEventDialog } from "./edit-event-dialog";
import { useState } from "react";
import { Switch } from "@/components/ui/switch";
import { Pencil, Trash2, Filter } from "lucide-react";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

export default function EventsTable({
  allEvents,
  culturalEvents,
  technicalEvents,
}: {
  allEvents: EventItem[];
  culturalEvents: EventItem[];
  technicalEvents: EventItem[];
}) {
  const [isPending, startTransition] = useTransition();
  const router = useRouter();
  const [selectedEvent, setSelectedEvent] = useState<EventItem | null>(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [eventToDelete, setEventToDelete] = useState<EventItem | null>(null);
  const [activeTab, setActiveTab] = useState<"all" | "cultural" | "technical">("all");
  const [selectedClub, setSelectedClub] = useState<string>("all");

  const clubList = Array.from(
    new Set(allEvents.map((e) => e.event_org).filter(Boolean))
  ).sort() as string[];

  const baseEvents = activeTab === "all" ? allEvents : activeTab === "cultural" ? culturalEvents : technicalEvents;
  const events = selectedClub === "all" ? baseEvents : baseEvents.filter((e) => e.event_org === selectedClub);

  const renderList = (eventsList: EventItem[]) => {
    if (eventsList.length === 0) {
      return (
        <div className="flex flex-col items-center justify-center py-16">
          <p className="text-[13px]" style={{ color: '#555' }}>No events found</p>
        </div>
      );
    }

    return (
      <div className="rounded-lg overflow-hidden" style={{ border: '1px solid #1e1e1e' }}>
        {/* Header */}
        <div className="grid grid-cols-[1.8fr_1fr_0.6fr_0.8fr_0.8fr_0.8fr_100px] gap-3 px-4 py-2.5 text-[11px] font-medium uppercase tracking-wider" style={{ background: '#141414', color: '#555', borderBottom: '1px solid #1e1e1e' }}>
          <div>Event</div>
          <div>Club</div>
          <div>Type</div>
          <div>Price</div>
          <div>Date</div>
          <div>Status</div>
          <div className="text-right">Actions</div>
        </div>

        {/* Rows */}
        {eventsList.map((event) => (
          <div
            key={event.id}
            className="grid grid-cols-[1.8fr_1fr_0.6fr_0.8fr_0.8fr_0.8fr_100px] gap-3 px-4 py-3 items-center transition-colors duration-75"
            style={{ borderBottom: '1px solid #1a1a1a' }}
            onMouseEnter={(e) => { e.currentTarget.style.background = '#141414'; }}
            onMouseLeave={(e) => { e.currentTarget.style.background = 'transparent'; }}
          >
            {/* Name */}
            <div className="min-w-0">
              <p className="text-[13px] font-medium truncate" style={{ color: '#e5e5e5' }}>
                {event.event_name}
              </p>
            </div>

            {/* Club */}
            <div className="text-[13px] truncate" style={{ color: '#888' }}>
              {event.event_org}
            </div>

            {/* Type badge */}
            <div>
              <span className="text-[11px] px-2 py-0.5 rounded-full font-medium" style={{
                background: event.event_type === "Cultural" ? 'rgba(129,140,248,0.1)' : 'rgba(56,189,248,0.1)',
                color: event.event_type === "Cultural" ? '#818cf8' : '#38bdf8',
                border: `1px solid ${event.event_type === "Cultural" ? 'rgba(129,140,248,0.2)' : 'rgba(56,189,248,0.2)'}`,
              }}>
                {event.event_type}
              </span>
            </div>

            {/* Price */}
            <div>
              <span className="text-[13px] font-medium" style={{ color: '#e5e5e5' }}>₹{event.event_price}</span>
              {event.event_pair_price && (
                <span className="text-[11px] block" style={{ color: '#555' }}>Pair: ₹{event.event_pair_price}</span>
              )}
            </div>

            {/* Date */}
            <div>
              <span className="text-[13px]" style={{ color: '#888' }}>{event.event_date}</span>
              {event.event_end_date && (
                <span className="text-[11px] block" style={{ color: '#555' }}>→ {event.event_end_date}</span>
              )}
            </div>

            {/* Registration toggle */}
            <div className="flex items-center gap-2">
              <Switch
                checked={event.registration_open}
                disabled={isPending}
                className="data-[state=checked]:bg-emerald-600 data-[state=unchecked]:bg-[#333] h-[18px] w-[32px] [&>span]:h-[14px] [&>span]:w-[14px] [&>span]:bg-white"
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

            {/* Actions */}
            <div className="flex items-center gap-1.5 justify-end">
              <button
                onClick={() => { setSelectedEvent(event); setDialogOpen(true); }}
                className="p-1.5 rounded transition-colors duration-100 cursor-pointer"
                style={{ color: '#666' }}
                onMouseEnter={(e) => { e.currentTarget.style.background = '#1e1e1e'; e.currentTarget.style.color = '#e5e5e5'; }}
                onMouseLeave={(e) => { e.currentTarget.style.background = 'transparent'; e.currentTarget.style.color = '#666'; }}
              >
                <Pencil size={13} />
              </button>
              <button
                disabled={isPending}
                onClick={() => { setEventToDelete(event); setDeleteDialogOpen(true); }}
                className="p-1.5 rounded transition-colors duration-100 cursor-pointer"
                style={{ color: '#666' }}
                onMouseEnter={(e) => { e.currentTarget.style.background = 'rgba(248,113,113,0.1)'; e.currentTarget.style.color = '#f87171'; }}
                onMouseLeave={(e) => { e.currentTarget.style.background = 'transparent'; e.currentTarget.style.color = '#666'; }}
              >
                <Trash2 size={13} />
              </button>
            </div>
          </div>
        ))}
      </div>
    );
  };

  return (
    <>
      {/* Controls: Tabs & Club Filter */}
      <div className="flex items-center justify-between gap-4 mb-4 flex-wrap">
        {/* Tab switcher */}
        <div className="flex items-center gap-1 p-0.5 rounded-lg w-fit" style={{ background: '#141414', border: '1px solid #1e1e1e' }}>
          {([
            { key: "all" as const, label: "All", count: allEvents.length },
            { key: "cultural" as const, label: "Cultural", count: culturalEvents.length },
            { key: "technical" as const, label: "Technical", count: technicalEvents.length },
          ]).map((tab) => (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key)}
              className="flex items-center gap-2 px-4 py-1.5 rounded-md text-[13px] font-medium transition-all duration-100 cursor-pointer"
              style={{
                background: activeTab === tab.key ? '#1e1e1e' : 'transparent',
                color: activeTab === tab.key ? '#e5e5e5' : '#666',
              }}
            >
              {tab.label}
              <span className="text-[11px] px-1.5 py-0.5 rounded-full" style={{
                background: activeTab === tab.key ? '#333' : '#1a1a1a',
                color: activeTab === tab.key ? '#e5e5e5' : '#555',
              }}>
                {tab.count}
              </span>
            </button>
          ))}
        </div>

        {/* Club filter dropdown */}
        <div className="flex items-center gap-2">
          <span className="text-[12px] font-medium" style={{ color: '#aaa' }}>Filter Club:</span>
          <Select value={selectedClub} onValueChange={setSelectedClub}>
            <SelectTrigger className="h-8 min-w-[170px] text-[12px] rounded-md font-medium border border-[#383842] bg-[#18181c] text-[#f4f4f5]">
              <SelectValue placeholder="All Clubs" />
            </SelectTrigger>
            <SelectContent className="max-h-[280px] border border-[#383842] bg-[#18181c] text-[#f4f4f5] shadow-2xl">
              <SelectItem value="all">
                All Clubs ({baseEvents.length})
              </SelectItem>
              {clubList.map((club) => {
                const count = baseEvents.filter((e) => e.event_org === club).length;
                return (
                  <SelectItem key={club} value={club}>
                    {club} ({count})
                  </SelectItem>
                );
              })}
            </SelectContent>
          </Select>
        </div>
      </div>

      {renderList(events)}

      <EditEventDialog
        event={selectedEvent}
        open={dialogOpen}
        onOpenChange={setDialogOpen}
      />

      <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <AlertDialogContent className="max-w-[400px] p-0 gap-0" style={{ background: '#141414', border: '1px solid #1e1e1e', color: '#e5e5e5' }}>
          <AlertDialogHeader className="px-5 py-4" style={{ borderBottom: '1px solid #1e1e1e' }}>
            <AlertDialogTitle className="text-[15px] font-semibold" style={{ color: '#e5e5e5' }}>Delete Event</AlertDialogTitle>
            <AlertDialogDescription className="text-[12px] mt-1" style={{ color: '#666' }}>
              Are you sure you want to delete <strong style={{ color: '#e5e5e5' }}>{eventToDelete?.event_name}</strong>? This action cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter className="px-5 py-3 gap-2" style={{ borderTop: '1px solid #1e1e1e' }}>
            <AlertDialogCancel className="h-8 text-[13px] font-medium rounded-md cursor-pointer" style={{ background: 'transparent', border: '1px solid #262626', color: '#888' }}>
              Cancel
            </AlertDialogCancel>
            <AlertDialogAction
              className="h-8 text-[13px] font-medium rounded-md cursor-pointer"
              style={{ background: 'rgba(239,68,68,0.9)', color: '#fff' }}
              onClick={() => {
                if (eventToDelete) {
                  startTransition(async () => {
                    await deleteEvent(eventToDelete.id);
                    router.refresh();
                    setDeleteDialogOpen(false);
                    setEventToDelete(null);
                  });
                }
              }}
            >
              Delete Event
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </>
  );
}
