/**
 * Past performers who've graced the Gullyverse stage.
 *
 * Edit this list and the gallery rebuilds itself — no other file to touch.
 * `image` paths are for real photos when they land; until then the gallery
 * component generates styled placeholder blocks (artist initial over a
 * graffiti colour swatch).
 */

export interface Performer {
  /** Display name, rendered in the spray-paint display font. */
  name: string;
  /** Year(s) as a display string — "2023", "2023 & 2026", or "TBD". */
  year: string;
  /** Path to the artist photo. Leave as placeholder for now. */
  image: string;
  /** Accent colour for this card's graffiti backdrop — pulled from the
   *  tunnel's own aerosol palette so the posters match the walls. */
  accent: string;
}

/**
 * The six aerosol colours already on the tunnel walls (see graffiti.ts AEROSOL).
 * Cards cycle through them so no two neighbours share a swatch.
 */
const A = {
  red: "#d0392c",
  gold: "#f2b30f",
  blue: "#1f5fd0",
  green: "#2f9e5a",
  pink: "#d6357f",
  cream: "#efe6cf",
} as const;

export const PERFORMERS: Performer[] = [
  { name: "Neha Kakkar", year: "2017", image: "/performers/neha-kakkar.jpeg", accent: A.pink },
  { name: "Local Train", year: "2018", image: "/performers/local-train.jpg", accent: A.blue },
  { name: "Ritviz", year: "2019", image: "/performers/ritviz.jpg", accent: A.green },
  { name: "When Chai Met Toast", year: "2019", image: "/performers/when-chai-met-toast.jpeg", accent: A.gold },
  { name: "Nikhil D'Souza", year: "2020", image: "/performers/nikhil-dsouza.jpg", accent: A.red },
  { name: "Harsh Gujral", year: "2021", image: "/performers/harsh-gujral.jpeg", accent: A.cream },
  { name: "Osho Jain", year: "2021", image: "/performers/osho-jain.jpeg", accent: A.blue },
  { name: "Dream Note", year: "2023", image: "/performers/dream-note.jpeg", accent: A.pink },
  { name: "Twin Strings", year: "2023 & 2026", image: "/performers/twin-strings.jpeg", accent: A.green },
  { name: "Akhil Sachdeva", year: "2024", image: "/performers/akhil-sachdeva.jpg", accent: A.gold },
  { name: "Lost Stories", year: "2024", image: "/performers/lost-stories.jpeg", accent: A.red },
  { name: "Yellow Diaries", year: "2024", image: "/performers/yellow-diaries.jpg", accent: A.gold },
  { name: "Khullar G", year: "2025", image: "/performers/khullar-g.jpeg", accent: A.blue },
  { name: "Nikita Gandhi", year: "2025", image: "/performers/nikita-gandhi.jpg", accent: A.pink },
  { name: "Chaar Diwaari", year: "2026", image: "/performers/chaar-diwaari.jpg", accent: A.green },
];
