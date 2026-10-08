import { NextRequest, NextResponse } from "next/server";
import { z } from "zod";
import { prisma } from "@/lib/prisma";
import { accountSchema } from "@/lib/payments/validation";
import { paymentAdmin, paymentError, PaymentError } from "@/lib/payments/http";

export async function GET(req: NextRequest) {
  try {
    const auth = await paymentAdmin(req); if (auth.authorized === false) return auth.response;
    const accounts = await prisma.paymentAccount.findMany({ orderBy: { createdAt: "desc" }, include: { _count: { select: { transactions: true } } } });
    return NextResponse.json({ accounts }, { headers: { "Cache-Control": "private, no-store" } });
  } catch (error) { return paymentError(error); }
}

export async function POST(req: NextRequest) {
  try {
    const auth = await paymentAdmin(req); if (auth.authorized === false) return auth.response;
    const data = accountSchema.parse(await req.json()) as Required<z.infer<typeof accountSchema>>;
    const account = await prisma.paymentAccount.create({ data: { ...data, createdBy: auth.userId } });
    return NextResponse.json({ account }, { status: 201 });
  } catch (error) { return paymentError(error); }
}

export async function PATCH(req: NextRequest) {
  try {
    const auth = await paymentAdmin(req); if (auth.authorized === false) return auth.response;
    const body = z.object({ id: z.string().min(1), action: z.enum(["activate", "deactivate", "verifyNotes", "disableNotes"]), confirmed: z.boolean().optional() }).parse(await req.json());
    if (body.action === "verifyNotes" && !body.confirmed) throw new PaymentError("Confirm a real test payment's complete order code is present in this account's bank statement.");
    const account = await prisma.$transaction(async tx => {
      await tx.$executeRaw`SELECT pg_advisory_xact_lock(271027)`;
      if (!(await tx.paymentAccount.findUnique({ where: { id: body.id } }))) throw new PaymentError("Account not found.", 404);
      if (body.action === "activate") await tx.paymentAccount.updateMany({ where: { active: true }, data: { active: false } });
      return tx.paymentAccount.update({ where: { id: body.id }, data: body.action === "activate" ? { active: true } : body.action === "deactivate" ? { active: false } : { noteMatchingVerified: body.action === "verifyNotes", noteVerifiedBy: auth.userId, noteVerifiedAt: new Date() } });
    });
    return NextResponse.json({ account });
  } catch (error) { return paymentError(error); }
}
