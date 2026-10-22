"use client";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { EventItem, Roles } from "@prisma/client";
import { useEffect, useState } from "react";
import { updateEvent } from "./actions";
import { useRouter } from "next/navigation";

export function EditEventDialog({
  event,
  open,
  onOpenChange,
  curr_club,
}: {
  event: EventItem | null;
  open: boolean;
  curr_club: Roles;
  onOpenChange: (open: boolean) => void;
}) {
  const [eventData, setEventData] = useState<EventItem | null>(null);
  const [isMultiDay, setIsMultiDay] = useState(false);
  const [hasPairPricing, setHasPairPricing] = useState(false);
  const router = useRouter();

  useEffect(() => {
    setEventData(event);
    setIsMultiDay(!!event?.event_end_date);
    setHasPairPricing(!!event?.event_pair_price);
  }, [event]);

  if (!eventData) return null;

  const inputStyle = {
    background: '#0a0a0a',
    border: '1px solid #262626',
    color: '#e5e5e5',
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[520px] max-h-[90vh] overflow-y-auto p-0 gap-0" style={{ background: '#141414', border: '1px solid #1e1e1e', color: '#e5e5e5' }}>
        <DialogHeader className="px-5 py-4" style={{ borderBottom: '1px solid #1e1e1e' }}>
          <DialogTitle className="text-[15px] font-semibold tracking-[-0.01em]" style={{ color: '#e5e5e5' }}>
            Edit Event
          </DialogTitle>
          <p className="text-[12px] mt-1" style={{ color: '#666' }}>Update event details</p>
        </DialogHeader>

        <form
          onSubmit={async (e) => {
            e.preventDefault();
            const formData = new FormData(e.target as HTMLFormElement);
            await updateEvent(eventData.id, formData);
            router.refresh();
            onOpenChange(false);
          }}
          className="p-5 space-y-4"
        >
          <input type="hidden" name="event_org" value={curr_club.club_name} />

          <div className="space-y-1.5">
            <Label className="text-[12px] font-medium" style={{ color: '#888' }} htmlFor="event_name">Event Name</Label>
            <Input id="event_name" name="event_name" defaultValue={eventData.event_name} className="h-8 text-[13px] rounded-md" style={inputStyle} />
          </div>

          <div className="space-y-1.5">
            <Label className="text-[12px] font-medium" style={{ color: '#888' }} htmlFor="event_description">Description</Label>
            <Textarea id="event_description" name="event_description" defaultValue={eventData.event_description} rows={3} className="text-[13px] rounded-md resize-none" style={inputStyle} />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1.5">
              <Label className="text-[12px] font-medium" style={{ color: '#888' }} htmlFor="event_price">Price (₹)</Label>
              <Input id="event_price" name="event_price" type="number" defaultValue={eventData.event_price} className="h-8 text-[13px] rounded-md" style={inputStyle} />
            </div>
            <div className="space-y-1.5">
              <Label className="text-[12px] font-medium" style={{ color: '#888' }} htmlFor="event_venue">Venue</Label>
              <Input id="event_venue" name="event_venue" defaultValue={eventData.event_venue || ""} className="h-8 text-[13px] rounded-md" style={inputStyle} />
            </div>
          </div>

          <div className="space-y-1.5">
            <Label className="text-[12px] font-medium" style={{ color: '#888' }} htmlFor="event_date">Start Date</Label>
            <Input id="event_date" name="event_date" type="text" defaultValue={eventData.event_date || ""} className="h-8 text-[13px] rounded-md" style={inputStyle} />
          </div>

          {/* Multi-day */}
          <div className="rounded-md p-3" style={{ background: '#0f0f0f', border: '1px solid #1e1e1e' }}>
            <label className="flex items-center gap-2 cursor-pointer">
              <input type="checkbox" checked={isMultiDay} onChange={(e) => setIsMultiDay(e.target.checked)} className="w-3.5 h-3.5 rounded" style={{ accentColor: '#e5e5e5' }} />
              <span className="text-[12px] font-medium" style={{ color: '#aaa' }}>Multi-day event</span>
            </label>
            {isMultiDay && (
              <div className="mt-3 space-y-1.5">
                <Label className="text-[12px] font-medium" style={{ color: '#888' }}>End Date</Label>
                <Input name="event_end_date" type="text" defaultValue={eventData.event_end_date || ""} className="h-8 text-[13px] rounded-md" style={inputStyle} />
              </div>
            )}
          </div>

          {/* Pair pricing */}
          <div className="rounded-md p-3" style={{ background: '#0f0f0f', border: '1px solid #1e1e1e' }}>
            <label className="flex items-center gap-2 cursor-pointer">
              <input type="checkbox" checked={hasPairPricing} onChange={(e) => setHasPairPricing(e.target.checked)} className="w-3.5 h-3.5 rounded" style={{ accentColor: '#e5e5e5' }} />
              <span className="text-[12px] font-medium" style={{ color: '#aaa' }}>Pair ticket pricing</span>
            </label>
            {hasPairPricing && (
              <div className="mt-3 space-y-1.5">
                <Label className="text-[12px] font-medium" style={{ color: '#888' }}>Pair Price (₹)</Label>
                <Input name="event_pair_price" type="number" defaultValue={eventData.event_pair_price || ""} className="h-8 text-[13px] rounded-md" style={inputStyle} />
              </div>
            )}
          </div>

          <div className="space-y-1.5">
            <Label className="text-[12px] font-medium" style={{ color: '#888' }} htmlFor="event_type">Event Type</Label>
            <Select name="event_type" defaultValue={eventData.event_type || "Cultural"}>
              <SelectTrigger className="h-8 text-[13px] rounded-md font-medium border border-[#383842] bg-[#18181c] text-[#f4f4f5]">
                <SelectValue placeholder="Select type" />
              </SelectTrigger>
              <SelectContent className="border border-[#383842] bg-[#18181c] text-[#f4f4f5] shadow-2xl">
                <SelectItem value="Cultural">Cultural</SelectItem>
                <SelectItem value="Technical">Technical</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="flex gap-2 pt-2" style={{ borderTop: '1px solid #1e1e1e' }}>
            <Button type="button" onClick={() => onOpenChange(false)} className="flex-1 h-8 text-[13px] font-medium rounded-md cursor-pointer" style={{ background: 'transparent', border: '1px solid #262626', color: '#888' }}>
              Cancel
            </Button>
            <Button type="submit" className="flex-1 h-8 text-[13px] font-medium rounded-md cursor-pointer" style={{ background: '#e5e5e5', color: '#0a0a0a' }}>
              Save Changes
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}
