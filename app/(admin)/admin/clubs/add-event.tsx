"use client";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Roles } from "@prisma/client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { format } from "date-fns";
import { createEvent } from "./actions";
import { Plus } from "lucide-react";

export default function AddEvent({ curr_club }: { curr_club: Roles }) {
  const [open, setOpen] = useState(false);
  const [error, setError] = useState("");
  const [isMultiDay, setIsMultiDay] = useState(false);
  const [hasPairPricing, setHasPairPricing] = useState(false);
  const [eventType, setEventType] = useState("Cultural");
  const router = useRouter();

  const MAX_FILE_SIZE = 4 * 1024 * 1024;

  const validateFileSize = (file: File) => file.size <= MAX_FILE_SIZE;

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return format(date, "MMM do yyyy");
  };

  async function handleSubmit(formData: FormData) {
    const posterFile = formData.get("event_poster") as File;
    if (!validateFileSize(posterFile)) {
      setError("Image size must be less than 4MB");
      return;
    }

    const rawDate = formData.get("event_date") as string;
    const formattedDate = formatDate(rawDate);
    const rawEndDate = formData.get("event_end_date") as string;
    const formattedEndDate = rawEndDate ? formatDate(rawEndDate) : null;

    const modifiedFormData = new FormData();
    formData.forEach((value, key) => {
      if (key === "event_date") {
        modifiedFormData.append(key, formattedDate);
      } else if (key === "event_end_date" && formattedEndDate) {
        modifiedFormData.append(key, formattedEndDate);
      } else {
        modifiedFormData.append(key, value);
      }
    });
    modifiedFormData.set("event_type", eventType);

    const result = await createEvent(modifiedFormData);
    if (result.success) {
      setOpen(false);
      setError("");
      setIsMultiDay(false);
      setHasPairPricing(false);
      setEventType("Cultural");
      router.refresh();
    } else {
      setError(result.error || "An error occurred");
    }
  }

  const inputStyle = {
    background: '#0a0a0a',
    border: '1px solid #262626',
    color: '#e5e5e5',
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <button
          className="flex items-center gap-1.5 px-3 py-[6px] rounded-md text-[13px] font-medium transition-colors duration-100 cursor-pointer"
          style={{ background: '#e5e5e5', color: '#0a0a0a' }}
          onMouseEnter={(e) => { e.currentTarget.style.background = '#d4d4d4'; }}
          onMouseLeave={(e) => { e.currentTarget.style.background = '#e5e5e5'; }}
        >
          <Plus size={14} strokeWidth={2} />
          Create Event
        </button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-[520px] max-h-[90vh] overflow-y-auto p-0 gap-0" style={{ background: '#141414', border: '1px solid #1e1e1e', color: '#e5e5e5' }}>
        <DialogHeader className="px-5 py-4" style={{ borderBottom: '1px solid #1e1e1e' }}>
          <DialogTitle className="text-[15px] font-semibold tracking-[-0.01em]" style={{ color: '#e5e5e5' }}>
            Create Event
          </DialogTitle>
          <p className="text-[12px] mt-1" style={{ color: '#666' }}>
            Add a new event for {curr_club.club_name}
          </p>
        </DialogHeader>

        {error && (
          <div className="mx-5 mt-4 px-3 py-2 rounded-md text-[12px]" style={{ background: 'rgba(239,68,68,0.08)', border: '1px solid rgba(239,68,68,0.15)', color: '#f87171' }}>
            {error}
          </div>
        )}

        <form action={handleSubmit} className="p-5 space-y-4">
          <input type="hidden" name="event_org" value={curr_club.club_name} />

          <div className="space-y-1.5">
            <label className="text-[12px] font-medium" style={{ color: '#aaa' }}>Event Name</label>
            <Input name="event_name" placeholder="e.g., Annual Music Concert" required className="h-8 text-[13px] rounded-md" style={inputStyle} />
          </div>

          <div className="space-y-1.5">
            <label className="text-[12px] font-medium" style={{ color: '#aaa' }}>Description</label>
            <Textarea name="event_description" placeholder="Describe the event..." required className="min-h-[80px] text-[13px] rounded-md resize-none" style={inputStyle} />
          </div>

          <div className="space-y-1.5">
            <label className="text-[12px] font-medium" style={{ color: '#aaa' }}>Event Type</label>
            <Select value={eventType} onValueChange={setEventType}>
              <SelectTrigger className="h-9 text-[13px] rounded-md font-medium border border-[#383842] bg-[#18181c] text-[#f4f4f5]">
                <SelectValue placeholder="Select type" />
              </SelectTrigger>
              <SelectContent className="border border-[#383842] bg-[#18181c] text-[#f4f4f5] shadow-2xl">
                <SelectItem value="Cultural">Cultural</SelectItem>
                <SelectItem value="Technical">Technical</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1.5">
              <label className="text-[12px] font-medium" style={{ color: '#888' }}>Price (₹)</label>
              <Input type="number" name="event_price" placeholder="500" min="0" required className="h-8 text-[13px] rounded-md" style={inputStyle} />
            </div>
            <div className="space-y-1.5">
              <label className="text-[12px] font-medium" style={{ color: '#888' }}>Venue</label>
              <Input name="event_venue" placeholder="Main Auditorium" required className="h-8 text-[13px] rounded-md" style={inputStyle} />
            </div>
          </div>

          <div className="space-y-1.5">
            <label className="text-[12px] font-medium" style={{ color: '#888' }}>Start Date</label>
            <Input type="date" name="event_date" required className="h-8 text-[13px] rounded-md" style={inputStyle} />
          </div>

          {/* Multi-day toggle */}
          <div className="rounded-md p-3" style={{ background: '#0f0f0f', border: '1px solid #1e1e1e' }}>
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={isMultiDay}
                onChange={(e) => setIsMultiDay(e.target.checked)}
                className="w-3.5 h-3.5 rounded"
                style={{ accentColor: '#e5e5e5' }}
              />
              <span className="text-[12px] font-medium" style={{ color: '#aaa' }}>Multi-day event</span>
            </label>
            {isMultiDay && (
              <div className="mt-3 space-y-1.5">
                <label className="text-[12px] font-medium" style={{ color: '#888' }}>End Date</label>
                <Input type="date" name="event_end_date" required={isMultiDay} className="h-8 text-[13px] rounded-md" style={inputStyle} />
              </div>
            )}
          </div>

          {/* Pair pricing toggle */}
          <div className="rounded-md p-3" style={{ background: '#0f0f0f', border: '1px solid #1e1e1e' }}>
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={hasPairPricing}
                onChange={(e) => setHasPairPricing(e.target.checked)}
                className="w-3.5 h-3.5 rounded"
                style={{ accentColor: '#e5e5e5' }}
              />
              <span className="text-[12px] font-medium" style={{ color: '#aaa' }}>Pair ticket pricing</span>
            </label>
            {hasPairPricing && (
              <div className="mt-3 space-y-1.5">
                <label className="text-[12px] font-medium" style={{ color: '#888' }}>Pair Price (₹)</label>
                <Input type="number" name="event_pair_price" placeholder="800" min="0" required={hasPairPricing} className="h-8 text-[13px] rounded-md" style={inputStyle} />
              </div>
            )}
          </div>

          <div className="space-y-1.5">
            <label className="text-[12px] font-medium" style={{ color: '#888' }}>Event Poster</label>
            <Input
              type="file"
              name="event_poster"
              accept="image/*"
              required
              className="h-auto py-1.5 text-[12px] rounded-md file:mr-3 file:py-1 file:px-3 file:rounded file:border-0 file:text-[12px] file:font-medium file:cursor-pointer"
              style={{ ...inputStyle, color: '#888' }}
              onChange={(e) => {
                const file = e.target.files?.[0];
                if (file && !validateFileSize(file)) setError("Image size must be less than 4MB");
                else setError("");
              }}
            />
            <p className="text-[11px]" style={{ color: '#555' }}>Max 4MB · JPG, PNG, WEBP</p>
          </div>

          <div className="flex gap-2 pt-2" style={{ borderTop: '1px solid #1e1e1e' }}>
            <Button
              type="button"
              onClick={() => setOpen(false)}
              className="flex-1 h-8 text-[13px] font-medium rounded-md cursor-pointer"
              style={{ background: 'transparent', border: '1px solid #262626', color: '#888' }}
            >
              Cancel
            </Button>
            <Button
              type="submit"
              className="flex-1 h-8 text-[13px] font-medium rounded-md cursor-pointer"
              style={{ background: '#e5e5e5', color: '#0a0a0a' }}
            >
              Create Event
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}
