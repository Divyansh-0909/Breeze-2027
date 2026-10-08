import { NextRequest, NextResponse } from "next/server";
import { z } from "zod";
import { prisma } from "@/lib/prisma";
import { paymentAdmin, paymentError, PaymentError } from "@/lib/payments/http";
import { approvePayment } from "@/lib/payments/service";
import { deliverPaymentEmail } from "@/lib/payments/email";
export async function POST(req: NextRequest) {
  try {
    const auth = await paymentAdmin(req);
    if (auth.authorized === false) return auth.response;
    const body = z.object({ transactionId: z.string().min(1).max(128), status: z.enum(["APPROVED", "REJECTED"]), rejectionReason: z.string().trim().max(1000).optional() }).parse(await req.json());
    if (body.status === "APPROVED") return NextResponse.json({ message: "Transaction approved successfully", ...await approvePayment(body.transactionId, auth.userId) });
    if (!body.rejectionReason) throw new PaymentError("A rejection reason is required.");
    await prisma.$transaction(async tx => {
      await tx.$queryRaw`SELECT token FROM "SubmittedTransaction" WHERE token = ${body.transactionId} FOR UPDATE`;
      const order = await tx.submittedTransaction.findUnique({ where: { token: body.transactionId } });
      if (!order) throw new PaymentError("Order not found.", 404);
      if (order.approved) throw new PaymentError("A confirmed order cannot be rejected. Review its refund or reversal separately.", 409);
      await tx.submittedTransaction.update({ where: { token: order.token }, data: { rejected: true, approved: false, rejection_reason: body.rejectionReason, paymentStatus: "REJECTED" } });
      await tx.paymentAudit.create({ data: { token: order.token, action: "REJECTED", actor: auth.userId, details: { reason: body.rejectionReason } } });
      await tx.paymentEmail.upsert({ where: { token_kind: { token: order.token, kind: "REJECTED" } }, create: { token: order.token, kind: "REJECTED" }, update: {} });
    });
    return NextResponse.json({ message: "Transaction rejected successfully", ...await deliverPaymentEmail(body.transactionId, "REJECTED") });
  } catch (error) { return paymentError(error); }
}
