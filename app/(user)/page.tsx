import type { Metadata } from "next";
import Link from "next/link";
import CypherGatePreview from "@/components/gullyverse-runtime/CypherGatePreview";
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

// The site is the walkable gully and cypher, starting in the market lane. `?start=<stop>` opens a map stop.
export default async function Home({ searchParams }: { searchParams: Promise<Record<string, string | string[] | undefined>> }) {
  const params = await searchParams;
  const start = params.start, team = typeof params.team === "string" ? params.team : undefined;
  const catalog = await liveCatalog();
  return <>
    <CypherGatePreview start={isCypherStart(start) ? start : "market"} team={team}
      canSendContact live catalog={catalog} />
    <NoScript />
  </>;
}
