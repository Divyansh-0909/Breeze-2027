import { notFound } from "next/navigation";
import CypherGatePreview from "@/components/gullyverse-runtime/CypherGatePreview";
import "@/components/gullyverse-runtime/journey.css";

export const dynamic = "force-dynamic";

export default async function CypherPreviewPage({ searchParams }: { searchParams: Promise<{ start?: string }> }) {
  if (process.env.GULLYVERSE_RUNTIME_PREVIEW !== "1") notFound();
  const { start } = await searchParams;
  return <CypherGatePreview start={start === "quarry" || start === "approach" ? start : "market"} />;
}
