import { notFound } from "next/navigation";
import SoundBoard from "./SoundBoard";

export const dynamic = "force-dynamic";

/** Private: every sound the gully plays, one at a time, for review. */
export default function SoundsPreviewPage() {
  if (process.env.GULLYVERSE_RUNTIME_PREVIEW !== "1") notFound();
  return <SoundBoard />;
}
