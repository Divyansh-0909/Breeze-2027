export interface ClubOption {
  id: string;
  club_name: string;
  label: string;
}

export const CANONICAL_CLUBS: string[] = [
  "BREEZE",
  "ACM",
  "ADVENTURE CLUB",
  "AURA",
  "CELESTIA EXPLORA",
  "CINEU",
  "DESIGN CLUB",
  "E-CELL",
  "FEEDING INDIA SNIOE CHAPTER",
  "FINVEST",
  "GDSC",
  "GIRLUP",
  "IMPRINTS",
  "INFERNO",
  "KALAKRITI",
  "MUNSOC",
  "MYTHIYA",
  "NEXUS",
  "PIXELS",
  "SIGREE",
  "SNU QUEER COLLECTIVE",
  "SNUPHORIA",
  "SPIC MACAY",
  "THE ACTIVE DREAMS",
  "THE CHEMISTRY SOCIETY",
  "THE ECONOMICS SOCIETY",
  "THE MATHEMATICS SOCIETY",
  "WORDS.INK",
  "WULA",
];

export function formatClubName(name: string): string {
  if (!name) return "";
  const trimmed = name.trim();
  const upper = trimmed.toUpperCase();

  // If already uppercase acronym
  if (["ACM", "GDSC", "MUNSOC", "WULA", "E-CELL", "BREEZE"].includes(upper)) {
    return upper;
  }

  // Capitalize words for readability
  return trimmed
    .split(/\s+/)
    .map((w) => w.charAt(0).toUpperCase() + w.slice(1).toLowerCase())
    .join(" ");
}

/**
 * Merge canonical clubs with any custom clubs present in database roles
 */
export function mergeClubs(existingClubNames: string[] = []): ClubOption[] {
  const set = new Set<string>();

  // Add canonical
  for (const c of CANONICAL_CLUBS) {
    set.add(c.toUpperCase());
  }

  // Add existing
  for (const c of existingClubNames) {
    if (c && c.trim()) {
      set.add(c.trim().toUpperCase());
    }
  }

  return Array.from(set)
    .sort((a, b) => {
      // Keep BREEZE at the top
      if (a === "BREEZE") return -1;
      if (b === "BREEZE") return 1;
      return a.localeCompare(b);
    })
    .map((name) => ({
      id: name,
      club_name: name,
      label: formatClubName(name),
    }));
}
