import { notFound } from "next/navigation";
import JourneyHost from "@/components/gullyverse-runtime/JourneyHost";
import "@/components/gullyverse-runtime/journey.css";
export const dynamic = "force-dynamic";
export default function RuntimePreview(){
  if(process.env.GULLYVERSE_RUNTIME_PREVIEW!=="1")notFound();
  return <JourneyHost/>;
}
