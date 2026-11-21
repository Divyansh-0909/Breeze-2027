import { NextResponse } from "next/server";
import { hasIsolatedPreviewBackend } from "@/lib/preview-backend";

export function GET() {
  return NextResponse.json({ isolated: hasIsolatedPreviewBackend() }, {
    headers: { "Cache-Control": "no-store" },
  });
}
