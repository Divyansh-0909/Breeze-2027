import { NextResponse, type NextRequest } from "next/server";
import { hasIsolatedPreviewBackend } from "@/lib/preview-backend";

export async function POST(request: NextRequest) {
  if (!hasIsolatedPreviewBackend()) {
    return NextResponse.json({ success: false }, { status: 503 });
  }
  const { POST: submitContact } = await import("../contact/route");
  return submitContact(request);
}
