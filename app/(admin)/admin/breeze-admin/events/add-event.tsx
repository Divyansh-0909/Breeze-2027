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
import { useState, useMemo } from "react";
import { useRouter } from "next/navigation";
import { format } from "date-fns";
import { createEvent } from "./actions";
import { Plus, Loader2, Eye, X } from "lucide-react";

interface Club {
  id: string;
  club_name: string;
  label?: string;
}

export default function AddEvent({ clubs }: { clubs: Club[] }) {
  const [open, setOpen] = useState(false);
  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isMultiDay, setIsMultiDay] = useState(false);
  const [hasPairPricing, setHasPairPricing] = useState(false);
  const [selectedClub, setSelectedClub] = useState("");
  const [eventType, setEventType] = useState("Cultural");
  const [eventName, setEventName] = useState("");
  const [eventDescription, setEventDescription] = useState("");
  const [eventPrice, setEventPrice] = useState("");
  const [eventVenue, setEventVenue] = useState("");
  const [eventDate, setEventDate] = useState("");
  const [eventEndDate, setEventEndDate] = useState("");
  const [eventPairPrice, setEventPairPrice] = useState("");
  const [posterFile, setPosterFile] = useState<File | null>(null);
  const [posterPreviewUrl, setPosterPreviewUrl] = useState<string | null>(null);
  const [showPosterPreview, setShowPosterPreview] = useState(false);
  const router = useRouter();

  const MAX_FILE_SIZE = 4 * 1024 * 1024;
  const validateFileSize = (file: File) => file.size <= MAX_FILE_SIZE;
  const formatDate = (dateString: string) => format(new Date(dateString), "MMM do yyyy");

  // Form validation - all required fields must be filled
  const isFormValid = useMemo(() => {
    const baseValid =
      selectedClub.trim() !== "" &&
      eventName.trim() !== "" &&
      eventDescription.trim() !== "" &&
      eventPrice.trim() !== "" &&
      eventVenue.trim() !== "" &&
      eventDate.trim() !== "" &&
      posterFile !== null;
    
    if (isMultiDay && eventEndDate.trim() === "") return false;
    if (hasPairPricing && eventPairPrice.trim() === "") return false;
    
    return baseValid;
  }, [selectedClub, eventName, eventDescription, eventPrice, eventVenue, eventDate, posterFile, isMultiDay, eventEndDate, hasPairPricing, eventPairPrice]);

  function resetForm() {
    setSelectedClub("");
    setEventType("Cultural");
    setEventName("");
    setEventDescription("");
    setEventPrice("");
    setEventVenue("");
    setEventDate("");
    setEventEndDate("");
    setEventPairPrice("");
    setPosterFile(null);
    setPosterPreviewUrl(null);
    setShowPosterPreview(false);
    setIsMultiDay(false);
    setHasPairPricing(false);
    setError("");
  }

  async function handleSubmit(formData: FormData) {
    if (isSubmitting || !isFormValid) return;
    setIsSubmitting(true);
    setError("");

    try {
      if (!posterFile || posterFile.size === 0) { setError("Please upload an event poster"); return; }
      if (!validateFileSize(posterFile)) { setError("Image size must be less than 4MB"); return; }
      if (!selectedClub) { setError("Please select a club"); return; }

      const rawDate = formData.get("event_date") as string;
      const formattedDate = formatDate(rawDate);
      const rawEndDate = formData.get("event_end_date") as string;
      const formattedEndDate = rawEndDate ? formatDate(rawEndDate) : null;

      const modifiedFormData = new FormData();
      formData.forEach((value, key) => {
        if (key === "event_date") modifiedFormData.append(key, formattedDate);
        else if (key === "event_end_date" && formattedEndDate) modifiedFormData.append(key, formattedEndDate);
        else modifiedFormData.append(key, value);
      });
      modifiedFormData.set("event_org", selectedClub);
      modifiedFormData.set("event_type", eventType);

      const result = await createEvent(modifiedFormData);
      if (result.success) {
        setOpen(false);
        resetForm();
        router.refresh();
      } else {
        setError(result.error || "An error occurred");
      }
    } catch {
      setError("An unexpected error occurred");
    } finally {
      setIsSubmitting(false);
    }
  }

  const inputStyle = { background: '#0a0a0a', border: '1px solid #262626', color: '#e5e5e5' };

  return (
    <>
      <Dialog open={open} onOpenChange={(v) => { setOpen(v); if (!v) resetForm(); }}>
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
            <DialogTitle className="text-[15px] font-semibold tracking-[-0.01em]" style={{ color: '#e5e5e5' }}>Create Event</DialogTitle>
            <p className="text-[12px] mt-1" style={{ color: '#666' }}>Create an event for any club (Admin)</p>
          </DialogHeader>

          {error && (
            <div className="mx-5 mt-4 px-3 py-2 rounded-md text-[12px]" style={{ background: 'rgba(239,68,68,0.08)', border: '1px solid rgba(239,68,68,0.15)', color: '#f87171' }}>
              {error}
            </div>
          )}

          <form action={handleSubmit} className="p-5 space-y-4">
            <div className="space-y-1.5">
              <label className="text-[12px] font-medium" style={{ color: '#aaa' }}>Organizing Club <span style={{ color: '#f87171' }}>*</span></label>
              <Select value={selectedClub} onValueChange={setSelectedClub} disabled={isSubmitting}>
                <SelectTrigger className="h-9 text-[13px] rounded-md font-medium border border-[#383842] bg-[#18181c] text-[#f4f4f5]">
                  <SelectValue placeholder="Select a club" />
                </SelectTrigger>
                <SelectContent className="max-h-[280px] border border-[#383842] bg-[#18181c] text-[#f4f4f5] shadow-2xl">
                  {clubs.map((club) => (
                    <SelectItem key={club.id} value={club.club_name}>
                      {club.label || club.club_name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-1.5">
              <label className="text-[12px] font-medium" style={{ color: '#aaa' }}>Event Name <span style={{ color: '#f87171' }}>*</span></label>
              <Input
                name="event_name"
                placeholder="Enter event name"
                required
                disabled={isSubmitting}
                value={eventName}
                onChange={(e) => setEventName(e.target.value)}
                className="h-8 text-[13px] rounded-md"
                style={inputStyle}
              />
            </div>

            <div className="space-y-1.5">
              <label className="text-[12px] font-medium" style={{ color: '#aaa' }}>Description <span style={{ color: '#f87171' }}>*</span></label>
              <Textarea
                name="event_description"
                placeholder="Enter event description"
                required
                disabled={isSubmitting}
                value={eventDescription}
                onChange={(e) => setEventDescription(e.target.value)}
                className="min-h-[80px] text-[13px] rounded-md resize-none"
                style={inputStyle}
              />
            </div>

            <div className="space-y-1.5">
              <label className="text-[12px] font-medium" style={{ color: '#aaa' }}>Event Type <span style={{ color: '#f87171' }}>*</span></label>
              <Select value={eventType} onValueChange={setEventType} disabled={isSubmitting}>
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
                <label className="text-[12px] font-medium" style={{ color: '#888' }}>Price (₹) <span style={{ color: '#f87171' }}>*</span></label>
                <Input
                  type="number"
                  name="event_price"
                  placeholder="Enter price"
                  min="0"
                  required
                  disabled={isSubmitting}
                  value={eventPrice}
                  onChange={(e) => setEventPrice(e.target.value)}
                  className="h-8 text-[13px] rounded-md"
                  style={inputStyle}
                />
              </div>
              <div className="space-y-1.5">
                <label className="text-[12px] font-medium" style={{ color: '#888' }}>Venue <span style={{ color: '#f87171' }}>*</span></label>
                <Input
                  name="event_venue"
                  placeholder="Enter venue"
                  required
                  disabled={isSubmitting}
                  value={eventVenue}
                  onChange={(e) => setEventVenue(e.target.value)}
                  className="h-8 text-[13px] rounded-md"
                  style={inputStyle}
                />
              </div>
            </div>

            <div className="space-y-1.5">
              <label className="text-[12px] font-medium" style={{ color: '#888' }}>Start Date <span style={{ color: '#f87171' }}>*</span></label>
              <Input
                type="date"
                name="event_date"
                required
                disabled={isSubmitting}
                value={eventDate}
                onChange={(e) => setEventDate(e.target.value)}
                className="h-8 text-[13px] rounded-md"
                style={inputStyle}
              />
            </div>

            <div className="rounded-md p-3" style={{ background: '#0f0f0f', border: '1px solid #1e1e1e' }}>
              <label className="flex items-center gap-2 cursor-pointer">
                <input type="checkbox" checked={isMultiDay} onChange={(e) => setIsMultiDay(e.target.checked)} disabled={isSubmitting} className="w-3.5 h-3.5 rounded" style={{ accentColor: '#e5e5e5' }} />
                <span className="text-[12px] font-medium" style={{ color: '#aaa' }}>Multi-day event</span>
              </label>
              {isMultiDay && (
                <div className="mt-3 space-y-1.5">
                  <label className="text-[12px] font-medium" style={{ color: '#888' }}>End Date <span style={{ color: '#f87171' }}>*</span></label>
                  <Input
                    type="date"
                    name="event_end_date"
                    required={isMultiDay}
                    disabled={isSubmitting}
                    value={eventEndDate}
                    onChange={(e) => setEventEndDate(e.target.value)}
                    className="h-8 text-[13px] rounded-md"
                    style={inputStyle}
                  />
                </div>
              )}
            </div>

            <div className="rounded-md p-3" style={{ background: '#0f0f0f', border: '1px solid #1e1e1e' }}>
              <label className="flex items-center gap-2 cursor-pointer">
                <input type="checkbox" checked={hasPairPricing} onChange={(e) => setHasPairPricing(e.target.checked)} disabled={isSubmitting} className="w-3.5 h-3.5 rounded" style={{ accentColor: '#e5e5e5' }} />
                <span className="text-[12px] font-medium" style={{ color: '#aaa' }}>Pair ticket pricing</span>
              </label>
              {hasPairPricing && (
                <div className="mt-3 space-y-1.5">
                  <label className="text-[12px] font-medium" style={{ color: '#888' }}>Pair Price (₹) <span style={{ color: '#f87171' }}>*</span></label>
                  <Input
                    type="number"
                    name="event_pair_price"
                    placeholder="Enter pair price"
                    min="0"
                    required={hasPairPricing}
                    disabled={isSubmitting}
                    value={eventPairPrice}
                    onChange={(e) => setEventPairPrice(e.target.value)}
                    className="h-8 text-[13px] rounded-md"
                    style={inputStyle}
                  />
                </div>
              )}
            </div>

            <div className="space-y-1.5">
              <label className="text-[12px] font-medium" style={{ color: '#888' }}>Event Poster <span style={{ color: '#f87171' }}>*</span></label>
              <Input
                type="file" name="event_poster" accept="image/*" required
                disabled={isSubmitting}
                className="h-auto py-1.5 text-[12px] rounded-md file:mr-3 file:py-1 file:px-3 file:rounded file:border-0 file:text-[12px] file:font-medium file:cursor-pointer"
                style={{ ...inputStyle, color: '#888' }}
                onChange={(e) => {
                  const file = e.target.files?.[0];
                  if (file) {
                    if (!validateFileSize(file)) {
                      setError("Image size must be less than 4MB");
                      setPosterFile(null);
                      setPosterPreviewUrl(null);
                    } else {
                      setError("");
                      setPosterFile(file);
                      setPosterPreviewUrl(URL.createObjectURL(file));
                    }
                  } else {
                    setPosterFile(null);
                    setPosterPreviewUrl(null);
                  }
                }}
              />
              <p className="text-[11px]" style={{ color: '#555' }}>Max 4MB · JPG, PNG, WEBP</p>
              {posterPreviewUrl && (
                <button
                  type="button"
                  onClick={() => setShowPosterPreview(true)}
                  className="flex items-center gap-1.5 mt-1 px-2.5 py-1 rounded text-[11px] font-medium transition-colors cursor-pointer"
                  style={{ background: 'rgba(129,140,248,0.1)', color: '#818cf8', border: '1px solid rgba(129,140,248,0.2)' }}
                >
                  <Eye size={12} />
                  Preview Poster
                </button>
              )}
            </div>

            <div className="flex gap-2 pt-2" style={{ borderTop: '1px solid #1e1e1e' }}>
              <Button
                type="button"
                onClick={() => setOpen(false)}
                disabled={isSubmitting}
                className="flex-1 h-8 text-[13px] font-medium rounded-md cursor-pointer"
                style={{ background: 'transparent', border: '1px solid #262626', color: '#888' }}
              >
                Cancel
              </Button>
              <Button
                type="submit"
                disabled={isSubmitting || !isFormValid}
                className="flex-1 h-8 text-[13px] font-medium rounded-md transition-all duration-150"
                style={{
                  background: isFormValid && !isSubmitting ? '#e5e5e5' : '#555',
                  color: isFormValid && !isSubmitting ? '#0a0a0a' : '#888',
                  cursor: isFormValid && !isSubmitting ? 'pointer' : 'not-allowed',
                  opacity: isSubmitting ? 0.7 : 1,
                }}
              >
                {isSubmitting ? (
                  <span className="flex items-center gap-2">
                    <Loader2 size={14} className="animate-spin" />
                    Creating…
                  </span>
                ) : (
                  "Create Event"
                )}
              </Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>

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
