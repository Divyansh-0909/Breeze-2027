import { NextRequest, NextResponse } from "next/server";
import { prisma } from "@/lib/prisma";
import { tokenPattern } from "@/lib/payments/http";
export async function GET(req: NextRequest) {
  const token = req.nextUrl.searchParams.get("token") || "";
  if (!tokenPattern.test(token)) return NextResponse.json({ error: "Invalid order link." }, { status: 400 });
  try {
    const order = await prisma.submittedTransaction.findUnique({ where: { token }, select: { paymentStatus: true, paymentReference: true, approved: true, rejected: true } });
    if (!order) return NextResponse.json({ error: "Order not found." }, { status: 404 });
    return NextResponse.json(order, { headers: { "Cache-Control": "private, no-store" } });
  } catch { return NextResponse.json({ error: "Order status is temporarily unavailable." }, { status: 503 }); }
}
