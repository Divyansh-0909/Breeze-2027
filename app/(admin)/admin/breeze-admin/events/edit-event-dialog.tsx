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
import { EventItem } from "@prisma/client";
import { useEffect, useState } from "react";
import { updateEvent } from "./actions";
import { useRouter } from "next/navigation";
import Image from "next/image";

export function EditEventDialog({
  event,
  open,
  onOpenChange,
}: {
  event: EventItem | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}) {
  const [eventData, setEventData] = useState<EventItem | null>(null);
  const [isMultiDay, setIsMultiDay] = useState(false);
  const [hasPairPricing, setHasPairPricing] = useState(false);
  const [error, setError] = useState("");
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const router = useRouter();

  const MAX_FILE_SIZE = 4 * 1024 * 1024;
  const validateFileSize = (file: File) => file.size <= MAX_FILE_SIZE;

  useEffect(() => {
    setEventData(event);
    setIsMultiDay(!!event?.event_end_date);
    setHasPairPricing(!!event?.event_pair_price);
    setImagePreview(null);
    setError("");
  }, [event]);

  if (!eventData) return null;

  const inputStyle = { background: '#0a0a0a', border: '1px solid #262626', color: '#e5e5e5' };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[520px] max-h-[90vh] overflow-y-auto p-0 gap-0" style={{ background: '#141414', border: '1px solid #1e1e1e', color: '#e5e5e5' }}>
        <DialogHeader className="px-5 py-4" style={{ borderBottom: '1px solid #1e1e1e' }}>
          <DialogTitle className="text-[15px] font-semibold tracking-[-0.01em]" style={{ color: '#e5e5e5' }}>Edit Event</DialogTitle>
          <p className="text-[12px] mt-1" style={{ color: '#666' }}>Update event details (Admin)</p>
        </DialogHeader>

        {error && (
          <div className="mx-5 mt-4 px-3 py-2 rounded-md text-[12px]" style={{ background: 'rgba(239,68,68,0.08)', border: '1px solid rgba(239,68,68,0.15)', color: '#f87171' }}>{error}</div>
        )}

        <form
          onSubmit={async (e) => {
            e.preventDefault();
            setError("");
            const formData = new FormData(e.target as HTMLFormElement);
            const file = formData.get("event_poster") as File;
            if (file && file.size > 0 && !validateFileSize(file)) { setError("Image size must be less than 4MB"); return; }
            const result = await updateEvent(eventData.id, formData);
            if (result.success) { router.refresh(); onOpenChange(false); }
            else { setError(result.error || "Failed to update event"); }
          }}
          className="p-5 space-y-4"
        >
          <div className="space-y-1.5">
            <Label className="text-[12px] font-medium" style={{ color: '#888' }} htmlFor="event_name">Event Name</Label>
            <Input id="event_name" name="event_name" defaultValue={eventData.event_name} className="h-8 text-[13px] rounded-md" style={inputStyle} />
          </div>

          <div className="space-y-1.5">
            <Label className="text-[12px] font-medium" style={{ color: '#888' }} htmlFor="event_description">Description</Label>
            <Input id="event_description" name="event_description" defaultValue={eventData.event_description} className="h-8 text-[13px] rounded-md" style={inputStyle} />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1.5">
              <Label className="text-[12px] font-medium" style={{ color: '#888' }} htmlFor="event_org">Club</Label>
              <Input id="event_org" name="event_org" defaultValue={eventData.event_org || ""} className="h-8 text-[13px] rounded-md" style={inputStyle} />
            </div>
            <div className="space-y-1.5">
              <Label className="text-[12px] font-medium" style={{ color: '#888' }} htmlFor="event_type">Type</Label>
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
            <Input id="event_date" name="event_date" defaultValue={eventData.event_date || ""} className="h-8 text-[13px] rounded-md" style={inputStyle} />
          </div>

          <div className="rounded-md p-3" style={{ background: '#0f0f0f', border: '1px solid #1e1e1e' }}>
            <label className="flex items-center gap-2 cursor-pointer">
              <input type="checkbox" checked={isMultiDay} onChange={(e) => setIsMultiDay(e.target.checked)} className="w-3.5 h-3.5 rounded" style={{ accentColor: '#e5e5e5' }} />
              <span className="text-[12px] font-medium" style={{ color: '#aaa' }}>Multi-day event</span>
            </label>
            {isMultiDay && (
              <div className="mt-3 space-y-1.5">
                <Label className="text-[12px] font-medium" style={{ color: '#888' }}>End Date</Label>
                <Input name="event_end_date" defaultValue={eventData.event_end_date || ""} className="h-8 text-[13px] rounded-md" style={inputStyle} />
              </div>
            )}
          </div>

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

          {/* Image */}
          <div className="rounded-md p-3 space-y-3" style={{ background: '#0f0f0f', border: '1px solid #1e1e1e' }}>
            <Label className="text-[12px] font-medium" style={{ color: '#888' }}>Event Poster</Label>
            {(imagePreview || eventData.image_url) && (
              <div className="relative w-full h-32 rounded-md overflow-hidden" style={{ border: '1px solid #262626' }}>
                <Image src={imagePreview || eventData.image_url || ""} alt="Preview" fill className="object-cover" />
              </div>
            )}
            <Input
              type="file" name="event_poster" accept="image/*"
              className="h-auto py-1.5 text-[12px] rounded-md file:mr-3 file:py-1 file:px-3 file:rounded file:border-0 file:text-[12px] file:font-medium file:cursor-pointer"
              style={{ ...inputStyle, color: '#888' }}
              onChange={(e) => {
                const file = e.target.files?.[0];
                if (file) {
                  if (!validateFileSize(file)) setError("Image size must be less than 4MB");
                  else { setError(""); setImagePreview(URL.createObjectURL(file)); }
                }
              }}
            />
            <p className="text-[11px]" style={{ color: '#555' }}>Leave empty to keep current · Max 4MB</p>
          </div>

          <div className="flex gap-2 pt-2" style={{ borderTop: '1px solid #1e1e1e' }}>
            <Button type="button" onClick={() => onOpenChange(false)} className="flex-1 h-8 text-[13px] font-medium rounded-md cursor-pointer" style={{ background: 'transparent', border: '1px solid #262626', color: '#888' }}>Cancel</Button>
            <Button type="submit" className="flex-1 h-8 text-[13px] font-medium rounded-md cursor-pointer" style={{ background: '#e5e5e5', color: '#0a0a0a' }}>Save Changes</Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}
