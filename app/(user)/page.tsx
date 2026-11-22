import type { Metadata } from "next";
import Link from "next/link";
import CypherGatePreview from "@/components/gullyverse-runtime/CypherGatePreview";
import { wantsClassicHub } from "@/lib/classic-hub";
import { isCypherStart } from "@/components/gullyverse-runtime/cypher-map";
import { readCypherEvents, type CypherCatalog } from "@/lib/events/cypher-catalog";
import "@/components/gullyverse-runtime/journey.css";

export const metadata: Metadata = { title: "Gullyverse · Breeze 2027" };
export const dynamic = "force-dynamic";

async function liveCatalog(): Promise<CypherCatalog | null> {
  try {
    return await readCypherEvents();
  } catch (error) {
    // Without a catalog the Events wall keeps its authored posters and hides
    // its action; the rest of the cypher stays walkable.
    console.error("Cypher events catalog failed:", error);
    return null;
  }
}

function NoScript() {
  return <noscript>Gullyverse requires JavaScript. <a href="/after-movie.mp4">Watch the Aftermovie</a> or <Link href="/events">browse festival information</Link>.</noscript>;
}

// Visitors enter through the original quarry, then walk the gully and cypher on
// the same canvas. `?start=` reopens a map stop; `?hub=classic` keeps the old hub.
export default async function Home({ searchParams }: { searchParams: Promise<Record<string, string | string[] | undefined>> }) {
  const params = await searchParams;
  // The layout mounts the original hub for these URLs.
  if (wantsClassicHub(params)) return <NoScript />;
  const start = params.start, team = typeof params.team === "string" ? params.team : undefined;
  const catalog = await liveCatalog();
  return <>
    <CypherGatePreview start={isCypherStart(start) ? start : "quarry"} team={team} canSendContact live catalog={catalog} />
    <NoScript />
  </>;
}
