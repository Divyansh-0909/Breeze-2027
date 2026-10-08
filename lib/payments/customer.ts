import { NextRequest, NextResponse } from "next/server";
import { randomBytes } from "node:crypto";
import { z } from "zod";
import { prisma } from "@/lib/prisma";
import { createAdminClient } from "@/utils/supabase/admin";
import { customerSchema } from "./validation";
import { checkOrigin, PaymentError, paymentError, tokenPattern } from "./http";
import { newPaymentReference, normalizeBankReference, upiPaymentUrl } from "./core";
import { approvePayment, reconcileAccount } from "./service";
import { deliverPaymentEmail } from "./email";

const cartSchema = z.object({ cart: z.record(z.string().uuid(), z.record(z.string().min(1).max(20), z.number().int().min(1).max(20))) });

export async function createCheckout(req: NextRequest) {
  try {
    checkOrigin(req);
    const { cart } = cartSchema.parse(await req.json());
    const ids = Object.keys(cart);
    if (!ids.length || ids.length > 30) throw new PaymentError("Choose between one and thirty items before checkout.");
    const [merch, events, account] = await Promise.all([
      prisma.merchItem.findMany({ where: { id: { in: ids } } }), prisma.eventItem.findMany({ where: { id: { in: ids } } }),
      prisma.paymentAccount.findFirst({ where: { active: true } }),
    ]);
    const merchMap = new Map(merch.map(item => [item.id, item]));
    const eventMap = new Map(events.map(item => [item.id, item]));
    let total = 0;
    const pricingSnapshot: Record<string, Record<string, number>> = {};
    for (const [id, variants] of Object.entries(cart)) {
      if (!Object.keys(variants).length) throw new PaymentError("An item has no selected ticket or size.");
      for (const [variant, quantity] of Object.entries(variants)) {
        const product = merchMap.get(id), event = eventMap.get(id);
        if (product) {
          if (!["XS", "S", "M", "L", "XL", "XXL", "XXXL", "2XL", "3XL", "NA", "FREE"].includes(variant)) throw new PaymentError("A merchandise size is invalid.");
          pricingSnapshot[id] = { ...pricingSnapshot[id], [variant]: product.product_price };
          total += product.product_price * quantity;
        } else if (event) {
          if (!event.registration_open) throw new PaymentError(`Registration for ${event.event_name} is closed.`);
          if (!["SINGLE", "PAIR", "NA"].includes(variant)) throw new PaymentError("An event ticket type is invalid.");
          if (variant === "PAIR" && !event.event_pair_price) throw new PaymentError("Pair tickets are not available for this event.");
          const price = variant === "PAIR" ? event.event_pair_price : event.event_price;
          pricingSnapshot[id] = { ...pricingSnapshot[id], [variant]: price };
          total += price * quantity;
        } else throw new PaymentError("An item in your cart is no longer available.");
      }
    }
    if (!Number.isSafeInteger(total) || total < 0) throw new PaymentError("The order amount is invalid.");
    if (total > 0 && !account) throw new PaymentError("The team has not opened payments yet. Please try again later.", 503);
    const id = randomBytes(32).toString("hex");
    await prisma.pendingTransaction.create({ data: {
      id, cart, pricingSnapshot, amount: total, accommodation: [], accommodation_price: 0,
      paymentReference: newPaymentReference(), paymentAccountId: total ? account.id : null,
      paymentUpiId: total ? account.upiId : null, paymentPayeeName: total ? account.payeeName : null,
    } });
    return NextResponse.json({ message: "Order created", id });
  } catch (error) { return paymentError(error); }
}

export async function submitPayment(req: NextRequest) {
  try {
    checkOrigin(req);
    const form = await req.formData();
    const token = String(form.get("token") || "");
    if (!tokenPattern.test(token)) throw new PaymentError("The checkout link is invalid.");
    const stage = String(form.get("stage") || "");
    if (stage === "prepare") {
      const customer = customerSchema.parse(Object.fromEntries(form.entries()));
      const order = await prisma.$transaction(async tx => {
        await tx.$queryRaw`SELECT id FROM "PendingTransaction" WHERE id = ${token} FOR UPDATE`;
        const existing = await tx.submittedTransaction.findUnique({ where: { token } });
        if (existing) return existing;
        const pending = await tx.pendingTransaction.findUnique({ where: { id: token } });
        if (!pending) throw new PaymentError("Order not found. Return to your cart.", 404);
        if (pending.amount > BigInt(0) && !pending.paymentAccountId) throw new PaymentError("This older checkout has no assigned receiving account. Create a new checkout from your cart.");
        // Serialize registrations for one email, including simultaneous checkout tabs.
        await tx.$executeRaw`SELECT pg_advisory_xact_lock(hashtextextended(${customer.email}, 0))`;
        const eventIds = (await tx.eventItem.findMany({ where: { id: { in: Object.keys(pending.cart as object) } }, select: { id: true } })).map(event => event.id);
        const prior = await tx.submittedTransaction.findMany({ where: { email: customer.email, rejected: false }, select: { cart: true } });
        if (prior.some(order => eventIds.some(id => Object.prototype.hasOwnProperty.call(order.cart, id)))) throw new PaymentError("You already have a registration or pending order for an event in this cart.", 409);
        const saved = await tx.submittedTransaction.create({ data: {
          token, name: customer.name, email: customer.email, phone: customer.phone, address: customer.rollNumber,
          student_details: customer.college_status, amount: pending.amount, cart: pending.cart, pricingSnapshot: pending.pricingSnapshot || undefined,
          accommodation: pending.accommodation, accommodation_price: pending.accommodation_price,
          paymentReference: pending.paymentReference, paymentAccountId: pending.paymentAccountId,
          paymentUpiId: pending.paymentUpiId, paymentPayeeName: pending.paymentPayeeName, paymentStatus: "AWAITING_PAYMENT",
        } });
        await tx.paymentAudit.create({ data: { token, action: "ORDER_PREPARED", actor: "CUSTOMER", details: { reference: saved.paymentReference, accountId: saved.paymentAccountId, amount: saved.amount.toString() } } });
        await tx.paymentEmail.create({ data: { token, kind: "PREPARED" } });
        return saved;
      }, { timeout: 15000 });
      if (order.amount === BigInt(0)) await approvePayment(token, "SYSTEM_FREE_REGISTRATION");
      else await deliverPaymentEmail(token, "PREPARED");
      return NextResponse.json({ prepared: true, reference: order.paymentReference,
        paymentUrl: order.amount > BigInt(0) ? upiPaymentUrl({ upiId: order.paymentUpiId, payeeName: order.paymentPayeeName, amount: order.amount.toString(), reference: order.paymentReference }) : null,
      });
    }
    if (stage !== "paid") throw new PaymentError("Save your customer details before reporting payment.");
    const order = await prisma.submittedTransaction.findUnique({ where: { token } });
    if (!order) throw new PaymentError("Save your details before paying.", 409);
    if (order.approved) return NextResponse.json({ approved: true });
    if (order.rejected) throw new PaymentError("This order was rejected. Contact the team before making another payment.", 409);
    const reference = String(form.get("bankReference") || "").trim();
    const claimedBankReference = reference ? normalizeBankReference(reference) : null;
    const proof = form.get("proofImage");
    let proofPath: string | undefined;
    if (proof instanceof File && proof.size) {
      if (proof.size > 5 * 1024 * 1024 || !["image/jpeg", "image/png", "image/webp"].includes(proof.type)) throw new PaymentError("Upload a JPEG, PNG, or WebP receipt no larger than 5 MB.");
      const supabase = createAdminClient();
      const { data, error } = await supabase.storage.from("transaction-proofs").upload(`${token}/${crypto.randomUUID()}`, proof);
      if (error) throw new PaymentError("Receipt upload failed. You can submit the bank reference instead, or try again.", 503);
      proofPath = data.path;
    }
    await prisma.$transaction(async tx => {
      await tx.$queryRaw`SELECT token FROM "SubmittedTransaction" WHERE token = ${token} FOR UPDATE`;
      const latest = await tx.submittedTransaction.findUniqueOrThrow({ where: { token } });
      if (latest.approved || latest.rejected) return;
      if (latest.claimedBankReference && claimedBankReference && latest.claimedBankReference !== claimedBankReference) throw new PaymentError("A different bank reference is already submitted. Contact the team to correct it.", 409);
      await tx.submittedTransaction.update({ where: { token }, data: {
        paymentStatus: "AWAITING_STATEMENT", paymentReportedAt: latest.paymentReportedAt || new Date(),
        ...(claimedBankReference ? { claimedBankReference } : {}), ...(proofPath ? { proof: proofPath } : {}),
      } });
      await tx.paymentAudit.create({ data: { token, action: "PAYMENT_REPORTED", actor: "CUSTOMER", details: { claimedBankReference, hasProof: Boolean(proofPath || latest.proof) } } });
    });
    if (order.paymentAccountId) await reconcileAccount(order.paymentAccountId, "CUSTOMER_REPORT", undefined, token);
    return NextResponse.json({ message: "Payment details received. Confirmation follows bank verification." });
  } catch (error) { return paymentError(error); }
}
