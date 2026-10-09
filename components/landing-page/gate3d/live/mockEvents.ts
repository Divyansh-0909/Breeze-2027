// Draft-1 data source: local mock acts. Times are anchored to load time so
// the draft always opens with something live — the real backend will serve
// fixed UTC times. Never import this from a component directly; go through
// `useTimeline()` so the Supabase swap touches one file.
import type { Announcement, TimelineEvent } from "./types";

function iso(base: number, minOffset: number): string {
  return new Date(base + minOffset * 60000).toISOString();
}

/** Anchor: the current hour, so the set always straddles "now". */
const now = Date.now();
const ANCHOR = Math.floor(now / 3600000) * 3600000;
const T = (isoStr: string) => isoStr; // readability alias below

export const MOCK_UPDATED_AT: string = new Date(now).toISOString();

export const MOCK_EVENTS: TimelineEvent[] = [
  {
    id: "ev-opener",
    title: "Gully Cypher: Open Mic",
    artist: "SNU Hip-Hop Collective",
    stage: "Workshops",
    description:
      "The day starts on the floor — sixteen bars each, crowd judges, winner opens the night stage.",
    startTime: T(iso(ANCHOR, -210)),
    endTime: T(iso(ANCHOR, -150)),
    status: null,
    featured: false,
    sortOrder: 1,
    updatedAt: MOCK_UPDATED_AT,
  },
  {
    id: "ev-sundowner",
    title: "Sundowner Acoustic Set",
    artist: "Osho Jain",
    stage: "Food Court",
    description:
      "Fingerpicked sundowners while the lights come on. Chai recommended.",
    startTime: T(iso(ANCHOR, -140)),
    endTime: T(iso(ANCHOR, -80)),
    status: null,
    featured: false,
    posterUrl: "/performers/osho-jain.jpeg",
    sortOrder: 2,
    updatedAt: MOCK_UPDATED_AT,
  },
  {
    id: "ev-chaar",
    title: "Chaar Diwaari Live",
    artist: "Chaar Diwaari",
    stage: "Main Stage",
    description:
      "Delhi's genre-bending breakout brings the four walls down. Expect unreleased material in the second half.",
    startTime: T(iso(ANCHOR, -25)),
    endTime: T(iso(ANCHOR, 35)),
    status: null,
    featured: false,
    posterUrl: "/performers/chaar-diwaari.jpg",
    sortOrder: 3,
    updatedAt: MOCK_UPDATED_AT,
  },
  {
    id: "ev-decks",
    title: "Decks on the Grass",
    artist: "Lost Stories",
    stage: "Food Court",
    description:
      "Overlapping sunset DJ set across the field — same time, second stage, no clash you can't walk between.",
    startTime: T(iso(ANCHOR, -10)),
    endTime: T(iso(ANCHOR, 50)),
    status: null,
    // overlaps Chaar Diwaari on purpose: exercises the featured hero pick
    featured: true,
    posterUrl: "/performers/lost-stories.jpeg",
    sortOrder: 4,
    updatedAt: MOCK_UPDATED_AT,
  },
  {
    id: "ev-cancelled",
    title: "Beatbox Showcase",
    artist: "Harsh Gujral",
    stage: "Workshops",
    description: "Called off — artist unwell. The cypher winners cover the slot.",
    startTime: T(iso(ANCHOR, 45)),
    endTime: T(iso(ANCHOR, 75)),
    status: "cancelled",
    featured: false,
    sortOrder: 5,
    updatedAt: MOCK_UPDATED_AT,
  },
  {
    id: "ev-ritviz",
    title: "Ritviz (Headliner)",
    artist: "Ritviz",
    stage: "Main Stage",
    description:
      "The finale. Bass, baaja and the whole gully singing back. Gates to the bowl open 15 min before.",
    startTime: T(iso(ANCHOR, 60)),
    endTime: T(iso(ANCHOR, 150)),
    status: null,
    featured: false,
    posterUrl: "/performers/ritviz.jpg",
    sortOrder: 6,
    updatedAt: MOCK_UPDATED_AT,
  },
  {
    id: "ev-afterhours",
    title: "Afterhours: Twin Strings",
    artist: "Twin Strings",
    stage: "Food Court",
    description: "Unplugged wind-down after the headliner. Blankets encouraged.",
    startTime: T(iso(ANCHOR, 160)),
    endTime: T(iso(ANCHOR, 220)),
    status: null,
    featured: false,
    posterUrl: "/performers/twin-strings.jpeg",
    sortOrder: 7,
    updatedAt: MOCK_UPDATED_AT,
  },
  {
    id: "ev-close",
    title: "Gullyverse Anthem Close",
    artist: "All Acts",
    stage: "Main Stage",
    description: "Everyone back on for one last song. Fireworks if the wind agrees.",
    startTime: T(iso(ANCHOR, 230)),
    endTime: T(iso(ANCHOR, 260)),
    status: null,
    featured: false,
    sortOrder: 8,
    updatedAt: MOCK_UPDATED_AT,
  },
];

export const MOCK_ANNOUNCEMENTS: Announcement[] = [
  {
    id: "an-1",
    message: "Gates to the main bowl open 15 min before the headliner.",
    severity: "info",
    active: true,
    createdAt: MOCK_UPDATED_AT,
  },
];

/** Slider bounds for the debug time simulator. */
export const MOCK_RANGE = {
  min: Date.parse(MOCK_EVENTS[0].startTime) - 30 * 60000,
  max:
    Date.parse(MOCK_EVENTS[MOCK_EVENTS.length - 1].endTime) + 30 * 60000,
};
