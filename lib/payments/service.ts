import { Prisma } from "@prisma/client";
import { prisma } from "@/lib/prisma";
import { exactPaymentMatch, MatchCredit } from "./core";
import { PaymentError } from "./http";
import { deliverPaymentEmail } from "./email";

export async function approveInTransaction(tx: Prisma.TransactionClient, token: string, actor: string, creditId?: string) {
  await tx.$queryRaw`SELECT token FROM "SubmittedTransaction" WHERE token = ${token} FOR UPDATE`;
  const order = await tx.submittedTransaction.findUnique({ where: { token } });
  if (!order) throw new PaymentError("Order not found.", 404);
  if (order.approved) return { changed: false };
  if (creditId) {
    await tx.$queryRaw`SELECT id FROM "BankCredit" WHERE id = ${creditId} FOR UPDATE`;
    const account = await tx.paymentAccount.findUniqueOrThrow({ where: { id: order.paymentAccountId } });
    const candidate = await tx.bankCredit.findUniqueOrThrow({ where: { id: creditId } });
    if (candidate.bankReference) await tx.$executeRaw`SELECT pg_advisory_xact_lock(hashtextextended(${account.id + ":" + candidate.bankReference}, 0))`;
    const bankRows = await tx.bankCredit.findMany({ where: { accountId: account.id, OR: [
      ...(order.paymentReference ? [{ orderReferences: { has: order.paymentReference } }] : []),
      { bankReference: { in: [candidate.bankReference, order.claimedBankReference].filter(Boolean) } },
    ] }, include: { statement: { select: { reviewed: true } }, matchedOrder: { select: { token: true } } } });
    const match = exactPaymentMatch(order, bankRows.map(toMatchCredit), account.noteMatchingVerified);
    if (!match.credit || match.credit.id !== creditId) throw new PaymentError(match.reason, 409);
    const claimants = await tx.submittedTransaction.count({ where: { paymentAccountId: account.id, token: { not: token }, rejected: false, OR: [{ claimedBankReference: match.credit.bankReference }, { bankReference: match.credit.bankReference }] } });
    if (claimants) throw new PaymentError("Another order claims this bank reference. Team review is required.", 409);
  } else if (order.claimedBankReference && order.paymentAccountId) {
    await tx.$executeRaw`SELECT pg_advisory_xact_lock(hashtextextended(${order.paymentAccountId + ":" + order.claimedBankReference}, 0))`;
    const claimed = await tx.submittedTransaction.count({ where: { token: { not: token }, paymentAccountId: order.paymentAccountId, approved: true, OR: [{ claimedBankReference: order.claimedBankReference }, { bankReference: order.claimedBankReference }] } });
    if (claimed) throw new PaymentError("This bank reference has already confirmed another order.", 409);
  }
  const credit = creditId ? await tx.bankCredit.findUniqueOrThrow({ where: { id: creditId } }) : null;
  await tx.submittedTransaction.update({ where: { token }, data: {
    approved: true, rejected: false, rejection_reason: null, paymentStatus: "APPROVED", paymentReviewReason: null,
    ...(credit ? { matchedCreditId: credit.id, bankReference: credit.bankReference } : order.claimedBankReference ? { bankReference: order.claimedBankReference } : {}),
  } });
  const cart = order.cart as Record<string, Record<string, number>>;
  const ids = Object.keys(cart);
  const [merch, events] = await Promise.all([tx.merchItem.findMany({ where: { id: { in: ids } } }), tx.eventItem.findMany({ where: { id: { in: ids } } })]);
  const merchIds = new Set(merch.map(item => item.id)), eventIds = new Set(events.map(item => item.id));
  for (const [id, variants] of Object.entries(cart)) {
    if (merchIds.has(id)) {
      for (const [size, quantity] of Object.entries(variants)) await tx.confirmedMerch.upsert({ where: { token_id_size: { token, id, size } }, create: { token, id, size, quantity }, update: {} });
    } else if (eventIds.has(id)) {
      const quantity = Object.values(variants).reduce((total, value) => total + value, 0);
      await tx.confirmedEvent.upsert({ where: { token_id: { token, id } }, create: { token, id, quantity }, update: {} });
    } else throw new PaymentError("An order item no longer exists. Review the order before approving it.", 409);
  }
  await tx.paymentAudit.create({ data: { token, action: credit ? "AUTO_APPROVED" : "MANUALLY_APPROVED", actor, details: { creditId: credit?.id || null, bankReference: credit?.bankReference || order.claimedBankReference || null, reference: order.paymentReference } } });
  await tx.paymentEmail.upsert({ where: { token_kind: { token, kind: "APPROVED" } }, create: { token, kind: "APPROVED" }, update: {} });
  return { changed: true };
}

function toMatchCredit(row: { id: string; accountId: string; bankReference: string | null; amountPaise: bigint; direction: string; description: string; orderReferences: string[]; conflict: boolean; bookedAt: Date; statement: { reviewed: boolean }; matchedOrder: { token: string } | null }): MatchCredit {
  return { ...row, reviewed: row.statement.reviewed, matchedToken: row.matchedOrder?.token || null };
}

export async function approvePayment(token: string, actor: string, creditId?: string, sendEmail = true) {
  const result = await prisma.$transaction(tx => approveInTransaction(tx, token, actor, creditId), { timeout: 30000 });
  const email = sendEmail ? await deliverPaymentEmail(token, "APPROVED") : { emailSent: false, emailError: undefined };
  return { ...result, ...email };
}

export async function reconcileAccount(accountId: string, actor: string, afterToken?: string, onlyToken?: string) {
  const account = await prisma.paymentAccount.findUniqueOrThrow({ where: { id: accountId } });
  const rows = await prisma.bankCredit.findMany({ where: { accountId }, include: { statement: { select: { reviewed: true } }, matchedOrder: { select: { token: true } } } });
  const candidates = await prisma.submittedTransaction.findMany({ where: { paymentAccountId: accountId, approved: false, rejected: false, ...(onlyToken ? { token: onlyToken } : afterToken ? { token: { gt: afterToken } } : {}) }, orderBy: { token: "asc" }, take: 101 });
  const orders = candidates.slice(0, 100);
  let approved = 0, review = 0, waiting = 0;
  for (const order of orders) {
    const match = exactPaymentMatch(order, rows.map(toMatchCredit), account.noteMatchingVerified);
    if (match.credit) {
      try {
        const result = await approvePayment(order.token, actor, match.credit.id, false);
        if (result.changed) approved++;
        continue;
      } catch (error) {
        if (!(error instanceof PaymentError)) throw error;
        match.reason = error.message;
      }
    }
    const noEntry = match.reason.startsWith("Waiting for");
    const status = noEntry ? (order.paymentReportedAt ? "AWAITING_STATEMENT" : "AWAITING_PAYMENT") : "NEEDS_REVIEW";
    // Never overwrite an approval from a concurrent reviewer/import.
    await prisma.submittedTransaction.updateMany({ where: { token: order.token, approved: false, rejected: false }, data: { paymentStatus: status, paymentReviewReason: noEntry ? null : match.reason } });
    if (noEntry) waiting++; else review++;
  }
  // A later statement may report a reversal of a previously confirmed payment.
  for (const row of rows.filter(row => row.direction === "DEBIT" || row.conflict)) {
    if (!row.bankReference) continue;
    const affected = await prisma.submittedTransaction.findMany({ where: { paymentAccountId: accountId, approved: true, bankReference: row.bankReference, paymentStatus: { not: "APPROVED_REVIEW_REQUIRED" } } });
    for (const order of affected) await prisma.$transaction([
      prisma.submittedTransaction.update({ where: { token: order.token }, data: { paymentStatus: "APPROVED_REVIEW_REQUIRED", paymentReviewReason: "A later bank entry indicates a possible reversal or conflict. Review fulfillment and refund status." } }),
      prisma.paymentAudit.create({ data: { token: order.token, action: "REVERSAL_REVIEW", actor, details: { creditId: row.id } } }),
    ]);
  }
  return { approved, review, waiting, processed: orders.length, hasMore: candidates.length > 100, nextCursor: orders.at(-1)?.token || null };
}
