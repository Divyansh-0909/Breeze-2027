import { NextRequest, NextResponse } from "next/server";
import { ZodError } from "zod";
import { requireBreezeAdmin } from "@/lib/auth";

export class PaymentError extends Error {
  constructor(message: string, public status = 400) { super(message); }
}

export function checkOrigin(req: NextRequest) {
  const origin = req.headers.get("origin");
  const allowed = [req.nextUrl.origin, process.env.NEXT_PUBLIC_APP_URL].filter(Boolean);
  if (origin && !allowed.includes(origin)) throw new PaymentError("Request origin is not allowed.", 403);
}

export async function paymentAdmin(req: NextRequest) {
  checkOrigin(req);
  return requireBreezeAdmin();
}

export function paymentError(error: unknown) {
  if (error instanceof PaymentError) return NextResponse.json({ error: error.message }, { status: error.status });
  if (error instanceof ZodError) return NextResponse.json({ error: error.issues.map(issue => issue.message).join(" ") }, { status: 400 });
  console.error("Payment operation failed:", error instanceof Error ? error.name : "Unknown error");
  return NextResponse.json({ error: "Payment service is unavailable. Please try again or contact the team." }, { status: 503 });
}

export const tokenPattern = /^[a-f0-9]{64}$/;
