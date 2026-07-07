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

  const MAX_FILE_SIZE = 4 * 1024 * 1024; // 4MB

  const validateFileSize = (file: File) => {
    return file.size <= MAX_FILE_SIZE;
  };

  useEffect(() => {
    setEventData(event);
    // Set toggles based on existing event data
    setIsMultiDay(!!event?.event_end_date);
    setHasPairPricing(!!event?.event_pair_price);
    setImagePreview(null);
    setError("");
  }, [event]);

  if (!eventData) return null;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[600px] max-h-[90vh] overflow-y-auto bg-white border-[#202020]/10">
        <DialogHeader className="pb-4 border-b border-[#202020]/10">
          <DialogTitle className="text-3xl font-bold text-[#202020] tracking-tight">
            Edit Event
          </DialogTitle>
          <p className="text-sm text-gray-500 mt-2">
            Update event details (Admin)
          </p>
        </DialogHeader>
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded-lg text-sm font-medium">
            {error}
          </div>
        )}
        <form
          onSubmit={async (e) => {
            e.preventDefault();
            setError("");
            const formData = new FormData(e.target as HTMLFormElement);
            
            // Check file size if file is provided
            const file = formData.get("event_poster") as File;
            if (file && file.size > 0 && !validateFileSize(file)) {
              setError("Image size must be less than 4MB");
              return;
            }

            const result = await updateEvent(eventData.id, formData);
            if (result.success) {
              router.refresh();
              onOpenChange(false);
            } else {
              setError(result.error || "Failed to update event");
            }
          }}
          className="space-y-5 pt-4"
        >
          <div className="space-y-2">
            <Label
              className="text-sm font-semibold text-[#202020]"
              htmlFor="event_name"
            >
              Event Name
            </Label>
            <Input
              id="event_name"
              name="event_name"
              defaultValue={eventData.event_name}
              className="w-full border-[#202020]/20 focus:border-[#202020] focus:ring-[#202020] bg-gray-50"
            />
          </div>

          <div className="space-y-2">
            <Label
              className="text-sm font-semibold text-[#202020]"
              htmlFor="event_description"
            >
              Description
            </Label>
            <Input
              id="event_description"
              name="event_description"
              defaultValue={eventData.event_description}
              className="w-full border-[#202020]/20 focus:border-[#202020] focus:ring-[#202020] bg-gray-50"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label
                className="text-sm font-semibold text-[#202020]"
                htmlFor="event_org"
              >
                Organizing Club
              </Label>
              <Input
                id="event_org"
                name="event_org"
                defaultValue={eventData.event_org || ""}
                className="w-full border-[#202020]/20 focus:border-[#202020] focus:ring-[#202020] bg-gray-50"
              />
            </div>

            <div className="space-y-2">
              <Label
                className="text-sm font-semibold text-[#202020]"
                htmlFor="event_type"
              >
                Event Type
              </Label>
              <Select
                name="event_type"
                defaultValue={eventData.event_type || "Cultural"}
              >
                <SelectTrigger className="w-full border-[#202020]/20 focus:border-[#202020] focus:ring-[#202020] bg-gray-50">
                  <SelectValue placeholder="Select event type" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="Cultural">Cultural</SelectItem>
                  <SelectItem value="Technical">Technical</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label
                className="text-sm font-semibold text-[#202020]"
                htmlFor="event_price"
              >
                Single Price (₹)
              </Label>
              <Input
                id="event_price"
                name="event_price"
                type="number"
                defaultValue={eventData.event_price}
                className="w-full border-[#202020]/20 focus:border-[#202020] focus:ring-[#202020] bg-gray-50"
              />
            </div>

            <div className="space-y-2">
              <Label
                className="text-sm font-semibold text-[#202020]"
                htmlFor="event_venue"
              >
                Venue
              </Label>
              <Input
                id="event_venue"
                name="event_venue"
                defaultValue={eventData.event_venue || ""}
                className="w-full border-[#202020]/20 focus:border-[#202020] focus:ring-[#202020] bg-gray-50"
              />
            </div>
          </div>

          <div className="space-y-2">
            <Label
              className="text-sm font-semibold text-[#202020]"
              htmlFor="event_date"
            >
              Start Date
            </Label>
            <Input
              id="event_date"
              name="event_date"
              defaultValue={eventData.event_date || ""}
              className="w-full border-[#202020]/20 focus:border-[#202020] focus:ring-[#202020] bg-gray-50"
            />
          </div>

          {/* Multi-day Event Toggle */}
          <div className="space-y-3 p-4 bg-gray-50 rounded-lg border border-[#202020]/10">
            <div className="flex items-center gap-3">
              <input
                type="checkbox"
                id="is_multi_day"
                checked={isMultiDay}
                onChange={(e) => setIsMultiDay(e.target.checked)}
                className="w-4 h-4 rounded border-[#202020]/20"
              />
              <label htmlFor="is_multi_day" className="text-sm font-semibold text-[#202020]">
                Multi-day Event
              </label>
            </div>
            {isMultiDay && (
              <div className="space-y-2 mt-3">
                <Label className="text-sm font-semibold text-[#202020]">
                  End Date
                </Label>
                <Input
                  name="event_end_date"
                  defaultValue={eventData.event_end_date || ""}
                  className="w-full border-[#202020]/20 focus:border-[#202020] focus:ring-[#202020] bg-gray-50"
                />
              </div>
            )}
          </div>

          {/* Pair Pricing Toggle */}
          <div className="space-y-3 p-4 bg-gray-50 rounded-lg border border-[#202020]/10">
            <div className="flex items-center gap-3">
              <input
                type="checkbox"
                id="has_pair_pricing"
                checked={hasPairPricing}
                onChange={(e) => setHasPairPricing(e.target.checked)}
                className="w-4 h-4 rounded border-[#202020]/20"
              />
              <label htmlFor="has_pair_pricing" className="text-sm font-semibold text-[#202020]">
                Enable Pair Ticket Pricing
              </label>
            </div>
            {hasPairPricing && (
              <div className="space-y-2 mt-3">
                <Label className="text-sm font-semibold text-[#202020]">
                  Pair Price (₹)
                </Label>
                <Input
                  name="event_pair_price"
                  type="number"
                  defaultValue={eventData.event_pair_price || ""}
                  className="w-full border-[#202020]/20 focus:border-[#202020] focus:ring-[#202020] bg-gray-50"
                />
              </div>
            )}
          </div>

          {/* Event Image Upload */}
          <div className="space-y-3 p-4 bg-gray-50 rounded-lg border border-[#202020]/10">
            <Label className="text-sm font-semibold text-[#202020]">
              Event Poster
            </Label>
            
            {/* Current image preview */}
            {(imagePreview || eventData.image_url) && (
              <div className="relative w-full h-40 rounded-lg overflow-hidden border border-[#202020]/10">
                <Image
                  src={imagePreview || eventData.image_url || ""}
                  alt="Event poster preview"
                  fill
                  className="object-cover"
                />
              </div>
            )}

            <Input
              type="file"
              name="event_poster"
              accept="image/*"
              className="w-full border-[#202020]/20 focus:border-[#202020] file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-[#202020] file:text-white hover:file:bg-[#303030] file:cursor-pointer bg-white"
              onChange={(e) => {
                const file = e.target.files?.[0];
                if (file) {
                  if (!validateFileSize(file)) {
                    setError("Image size must be less than 4MB");
                  } else {
                    setError("");
                    // Create preview URL
                    const url = URL.createObjectURL(file);
                    setImagePreview(url);
                  }
                }
              }}
            />
            <span className="text-xs text-gray-500">
              Leave empty to keep current image • Max: 4MB • JPG, PNG, WEBP
            </span>
          </div>

          <div className="flex gap-3 pt-4 border-t border-[#202020]/10">
            <Button
              type="button"
              variant="outline"
              onClick={() => onOpenChange(false)}
              className="flex-1 border-[#202020]/20 text-gray-600 hover:bg-gray-50"
            >
              Cancel
            </Button>
            <Button
              type="submit"
              className="flex-1 bg-[#202020] hover:bg-[#303030] text-white font-semibold"
            >
              Save Changes
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}
