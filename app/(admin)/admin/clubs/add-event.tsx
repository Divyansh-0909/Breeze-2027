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
import { prisma } from "@/lib/prisma";
import { revalidatePath } from "next/cache";
import { Roles } from "@prisma/client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { format } from "date-fns";

import { createEvent } from "./actions";

export default function AddEvent({ curr_club }: { curr_club: Roles }) {
  const [open, setOpen] = useState(false);
  const [error, setError] = useState("");
  const [isMultiDay, setIsMultiDay] = useState(false);
  const [hasPairPricing, setHasPairPricing] = useState(false);
  const router = useRouter();

  const MAX_FILE_SIZE = 4 * 1024 * 1024; // 5MB in bytes

  const validateFileSize = (file: File) => {
    if (file.size > MAX_FILE_SIZE) {
      return false;
    }
    return true;
  };

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

    // Handle end date for multi-day events
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

    const result = await createEvent(modifiedFormData);
    if (result.success) {
      setOpen(false);
      router.refresh();
    } else {
      setError(result.error || "An error occurred");
    }
  }

  return (
    <div className="flex justify-end mb-8">
      <Dialog open={open} onOpenChange={setOpen}>
        <DialogTrigger asChild>
          <Button className="bg-[#202020] hover:bg-[#303030] text-white font-medium px-6 py-2.5 rounded-lg transition-all">
            + Create Event
          </Button>
        </DialogTrigger>
        <DialogContent className="sm:max-w-[600px] max-h-[90vh] overflow-y-auto bg-white border-[#202020]/10">
          <DialogHeader className="pb-4 border-b border-[#202020]/10">
            <DialogTitle className="text-3xl font-bold text-[#202020] tracking-tight">
              Create New Event
            </DialogTitle>
            <p className="text-sm text-gray-500 mt-2">
              Fill in the details to create a new event for your club
            </p>
          </DialogHeader>
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded-lg text-sm font-medium">
              {error}
            </div>
          )}
          <form action={handleSubmit} className="space-y-5 pt-4">
            <input type="hidden" name="event_org" value={curr_club.club_name} />

            <div className="space-y-2">
              <label className="text-sm font-semibold text-[#202020]">
                Event Name *
              </label>
              <Input
                name="event_name"
                className="w-full border-[#202020]/20 focus:border-[#202020] focus:ring-[#202020] bg-gray-50"
                placeholder="e.g., Annual Music Concert"
                required
              />
            </div>

            <div className="space-y-2">
              <label className="text-sm font-semibold text-[#202020]">
                Description *
              </label>
              <Textarea
                name="event_description"
                className="w-full min-h-[100px] border-[#202020]/20 focus:border-[#202020] focus:ring-[#202020] bg-gray-50 resize-none"
                placeholder="Describe what attendees can expect from this event..."
                required
              />
            </div>

            <div className="space-y-2">
              <label className="text-sm font-semibold text-[#202020]">
                Event Type *
              </label>
              <select
                name="event_type"
                className="w-full h-10 px-3 border border-[#202020]/20 rounded-md focus:border-[#202020] focus:ring-[#202020] focus:ring-1 bg-gray-50 text-sm"
                required
              >
                <option value="">Select event type</option>
                <option value="Cultural">Cultural</option>
                <option value="Technical">Technical</option>
              </select>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <label className="text-sm font-semibold text-[#202020]">
                  Price (₹) *
                </label>
                <Input
                  type="number"
                  name="event_price"
                  className="w-full border-[#202020]/20 focus:border-[#202020] focus:ring-[#202020] bg-gray-50"
                  placeholder="500"
                  min="0"
                  required
                />
              </div>

              <div className="space-y-2">
                <label className="text-sm font-semibold text-[#202020]">
                  Venue *
                </label>
                <Input
                  name="event_venue"
                  className="w-full border-[#202020]/20 focus:border-[#202020] focus:ring-[#202020] bg-gray-50"
                  placeholder="Main Auditorium"
                  required
                />
              </div>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-semibold text-[#202020]">
                Start Date *
              </label>
              <Input
                type="date"
                name="event_date"
                className="w-full border-[#202020]/20 focus:border-[#202020] focus:ring-[#202020] bg-gray-50"
                required
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
                  Multi-day Event (up to 3 days)
                </label>
              </div>
              {isMultiDay && (
                <div className="space-y-2 mt-3">
                  <label className="text-sm font-semibold text-[#202020]">
                    End Date *
                  </label>
                  <Input
                    type="date"
                    name="event_end_date"
                    className="w-full border-[#202020]/20 focus:border-[#202020] focus:ring-[#202020] bg-gray-50"
                    required={isMultiDay}
                  />
                  <span className="text-xs text-gray-500">
                    Maximum 3 days from start date
                  </span>
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
                  <label className="text-sm font-semibold text-[#202020]">
                    Pair Price (₹) *
                  </label>
                  <Input
                    type="number"
                    name="event_pair_price"
                    className="w-full border-[#202020]/20 focus:border-[#202020] focus:ring-[#202020] bg-gray-50"
                    placeholder="800"
                    min="0"
                    required={hasPairPricing}
                  />
                  <span className="text-xs text-gray-500">
                    Price for a pair of tickets (usually discounted)
                  </span>
                </div>
              )}
            </div>

            <div className="space-y-2">
              <label className="text-sm font-semibold text-[#202020]">
                Event Poster *
              </label>
              <Input
                type="file"
                name="event_poster"
                className="w-full border-[#202020]/20 focus:border-[#202020] file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-[#202020] file:text-white hover:file:bg-[#303030] file:cursor-pointer bg-gray-50"
                accept="image/*"
                required
                onChange={(e) => {
                  const file = e.target.files?.[0];
                  if (file && !validateFileSize(file)) {
                    setError("Image size must be less than 4MB");
                  } else {
                    setError("");
                  }
                }}
              />
              <span className="text-xs text-gray-500">
                Max file size: 4MB • Recommended: 1200×800px • JPG, PNG, WEBP
              </span>
            </div>

            <div className="flex gap-3 pt-4 border-t border-[#202020]/10">
              <Button
                type="button"
                variant="outline"
                onClick={() => setOpen(false)}
                className="flex-1 border-[#202020]/20 text-gray-600 hover:bg-gray-50"
              >
                Cancel
              </Button>
              <Button
                type="submit"
                className="flex-1 bg-[#202020] hover:bg-[#303030] text-white font-semibold"
              >
                Create Event
              </Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
}
