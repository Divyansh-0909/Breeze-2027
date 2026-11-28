/**
 * Accommodation at BREEZE 2027 (Phase 3, mockup 04): one place to open booking and set the tiers. While closed, the
 * gully's accommodation wall shows a pulled-down shutter with "CHECK-IN OPENS SOON"; once open, the shutter rolls up
 * on a dim check-in counter and a chalk rate board lists these tiers.
 */
export type AccommodationTier = { name: string; price: string };

export const accommodation: { isAccommodationOpen: boolean; tiers: AccommodationTier[] } = {
  isAccommodationOpen: false,
  tiers: [
    { name: "DORM PASS", price: "TBA" },
    { name: "SHARED ROOM", price: "TBA" },
    { name: "3-DAY STAY", price: "TBA" },
  ],
};
