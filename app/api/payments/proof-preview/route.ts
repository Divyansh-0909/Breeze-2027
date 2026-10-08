import { NextRequest, NextResponse } from "next/server";
import { prisma } from "@/lib/prisma";
import { checkOrigin, PaymentError, paymentError, tokenPattern } from "@/lib/payments/http";
import { bankReferenceFromText } from "@/lib/payments/core";
import { receiptText } from "@/lib/payments/ocr";

export const runtime = "nodejs";
export const maxDuration = 60;
export async function POST(req: NextRequest) {
  try {
    checkOrigin(req);
    const form = await req.formData(), token = String(form.get("token") || ""), file = form.get("file");
    if (!tokenPattern.test(token) || !(file instanceof File) || file.size > 5 * 1024 * 1024 || !["image/jpeg", "image/png", "image/webp"].includes(file.type)) throw new PaymentError("Choose a valid order and a receipt image no larger than 5 MB.");
    const order = await prisma.submittedTransaction.findUnique({ where: { token }, select: { token: true } });
    if (!order) throw new PaymentError("Save your details before sharing a receipt.", 409);
    const data = Buffer.from(await file.arrayBuffer());
    const text = await receiptText(data);
    return NextResponse.json({ reference: bankReferenceFromText(text), requiresCustomerCheck: true }, { headers: { "Cache-Control": "private, no-store" } });
  } catch (error) { return paymentError(error); }
}
