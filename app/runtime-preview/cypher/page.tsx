import { notFound } from "next/navigation";
import CypherGatePreview from "@/components/gullyverse-runtime/CypherGatePreview";
import { hasIsolatedPreviewBackend } from "@/lib/preview-backend";
import { readCypherEvents } from "@/lib/events/cypher-catalog";
import "@/components/gullyverse-runtime/journey.css";

export const dynamic = "force-dynamic";

export default async function CypherPreviewPage({ searchParams }: { searchParams: Promise<{ start?: string; team?: string }> }) {
  if (process.env.GULLYVERSE_RUNTIME_PREVIEW !== "1") notFound();
  const { start, team } = await searchParams;
  const isolated = hasIsolatedPreviewBackend();
  const events = isolated ? await readCypherEvents() : null;
  return <CypherGatePreview
    start={start === "quarry" || start === "approach" || start === "plaza" || start === "contact" ||
      start === "events" || start === "team" || start === "aftermovie" ? start : "market"}
    team={team}
    canSendContact={isolated}
    catalog={events}
  />;
}
