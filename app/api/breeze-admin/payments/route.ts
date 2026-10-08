import { NextRequest, NextResponse } from "next/server";
import { z } from "zod";
import { prisma } from "@/lib/prisma";
import { paymentAdmin, paymentError } from "@/lib/payments/http";
import { reconcileAccount } from "@/lib/payments/service";
import { deliverPaymentEmail, drainPaymentEmails } from "@/lib/payments/email";

export const maxDuration = 300;
export async function GET(req: NextRequest) {
  try {
    const auth = await paymentAdmin(req); if (auth.authorized === false) return auth.response;
    const accountId = req.nextUrl.searchParams.get("accountId") || undefined;
    const orders = await prisma.submittedTransaction.findMany({ where: { ...(accountId ? { paymentAccountId: accountId } : {}) }, orderBy: { created_at: "desc" }, take: 100, include: {
      paymentAccount: { select: { label: true } }, paymentEmails: { select: { kind: true, status: true, attempts: true } },
      paymentAudits: { orderBy: { createdAt: "desc" }, take: 5, select: { action: true, actor: true, createdAt: true, details: true } },
    } });
    const statements = await prisma.bankStatement.findMany({ where: { ...(accountId ? { accountId } : {}) }, take: 30, orderBy: { importedAt: "desc" }, select: { id: true, filename: true, format: true, reviewed: true, importedAt: true, account: { select: { label: true } } } });
    return NextResponse.json({ orders: orders.map(order => ({ ...order, amount: order.amount.toString(), accommodation_price: order.accommodation_price.toString() })), statements, jevConfigured: Boolean(process.env.TYPESAFE_API_KEY) }, { headers: { "Cache-Control": "private, no-store" } });
  } catch (error) { return paymentError(error); }
}

export async function POST(req: NextRequest) {
  try {
    const auth = await paymentAdmin(req); if (auth.authorized === false) return auth.response;
    const body = z.discriminatedUnion("action", [
      z.object({ action: z.literal("reconcile"), accountId: z.string().min(1), afterToken: z.string().optional() }),
      z.object({ action: z.literal("emails") }),
      z.object({ action: z.literal("retryEmail"), token: z.string().min(1), kind: z.enum(["APPROVED", "PREPARED", "REJECTED"]) }),
    ]).parse(await req.json());
    if (body.action === "reconcile") return NextResponse.json(await reconcileAccount(body.accountId, auth.userId, body.afterToken));
    if (body.action === "emails") return NextResponse.json(await drainPaymentEmails());
    return NextResponse.json(await deliverPaymentEmail(body.token, body.kind));
  } catch (error) { return paymentError(error); }
}
