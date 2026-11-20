import { notFound } from "next/navigation";
import CypherGatePreview from "@/components/gullyverse-runtime/CypherGatePreview";
import "@/components/gullyverse-runtime/journey.css";

export const dynamic = "force-dynamic";

export default function CypherPreviewPage() {
  if (process.env.GULLYVERSE_RUNTIME_PREVIEW !== "1") notFound();
  return <CypherGatePreview />;
}
