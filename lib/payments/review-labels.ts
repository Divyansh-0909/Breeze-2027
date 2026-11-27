// Labels the bank entries behind orders in the review queue with a Jev suggestion,
// so the team can sort the queue faster. Labels are advisory only: exact matching
// in core.ts never reads them, and nothing here approves, rejects or changes an order.
import { prisma } from "@/lib/prisma";
import { jevConfigured, jevReview } from "./jev";

export const REVIEW_STATUSES = ["NEEDS_REVIEW", "APPROVED_REVIEW_REQUIRED"];

type ReviewOrder = { paymentReference: string | null; claimedBankReference: string | null; bankReference: string | null };
type LabelledCredit = { accountId: string; orderReferences: string[]; bankReference: string | null };

/** Which bank entries relate to a review order: same order code in the note, or the same bank reference. */
export function creditRelatesTo(order: ReviewOrder & { paymentAccountId: string | null }, credit: LabelledCredit) {
  if (!order.paymentAccountId || credit.accountId !== order.paymentAccountId) return false;
  if (order.paymentReference && credit.orderReferences.includes(order.paymentReference)) return true;
  return Boolean(credit.bankReference && (credit.bankReference === order.claimedBankReference || credit.bankReference === order.bankReference));
}

/** The text Jev sees: the bank's own fields for one entry. The description is customer-influenced and stays untrusted. */
export function reviewCreditText(credit: { bookedAt: Date; direction: string; amountPaise: bigint; bankReference: string | null; description: string }) {
  const rupees = `${credit.amountPaise / BigInt(100)}.${String(credit.amountPaise % BigInt(100)).padStart(2, "0")}`;
  return [credit.bookedAt.toISOString().slice(0, 10), credit.direction, `INR ${rupees}`, credit.bankReference || "no bank reference", credit.description].join(" | ");
}

/**
 * Labels up to `limit` unlabelled bank entries linked to review orders on one account.
 * Best-effort: stops at the first Jev error and leaves the remaining entries for the next run.
 */
export async function labelReviewCredits(accountId: string, limit = 20) {
  if (!jevConfigured()) return { labelled: 0, skipped: "Jev is not configured." };
  const orders = await prisma.submittedTransaction.findMany({
    where: { paymentAccountId: accountId, paymentStatus: { in: REVIEW_STATUSES } },
    select: { paymentAccountId: true, paymentReference: true, claimedBankReference: true, bankReference: true },
    take: 500,
  });
  const orderCodes = orders.flatMap(order => order.paymentReference ? [order.paymentReference] : []);
  const bankRefs = orders.flatMap(order => [order.claimedBankReference, order.bankReference].filter((ref): ref is string => Boolean(ref)));
  if (!orderCodes.length && !bankRefs.length) return { labelled: 0 };
  const credits = await prisma.bankCredit.findMany({
    where: { accountId, jevCheckedAt: null, OR: [{ orderReferences: { hasSome: orderCodes } }, { bankReference: { in: bankRefs } }] },
    orderBy: { bookedAt: "asc" },
    take: limit,
  });
  let labelled = 0;
  for (const credit of credits) {
    try {
      const result = await jevReview(reviewCreditText(credit));
      if (!result.enabled) break;
      await prisma.bankCredit.update({ where: { id: credit.id }, data: { jevLabel: result.classification, jevConfidence: result.confidence, jevCheckedAt: new Date() } });
      labelled++;
    } catch (error) {
      return { labelled, error: error instanceof Error ? error.message : "Jev labelling failed." };
    }
  }
  return { labelled };
}

/** Jev labels for the bank entries behind each review order, keyed by order token. */
export async function reviewLabelsFor(orders: (ReviewOrder & { token: string; paymentAccountId: string | null; paymentStatus: string })[]) {
  const review = orders.filter(order => REVIEW_STATUSES.includes(order.paymentStatus) && order.paymentAccountId);
  const labels = new Map<string, { label: string; confidence: number; bankReference: string | null }[]>();
  if (!review.length) return labels;
  const orderCodes = review.flatMap(order => order.paymentReference ? [order.paymentReference] : []);
  const bankRefs = review.flatMap(order => [order.claimedBankReference, order.bankReference].filter((ref): ref is string => Boolean(ref)));
  const credits = await prisma.bankCredit.findMany({
    where: { accountId: { in: [...new Set(review.map(order => order.paymentAccountId as string))] }, jevLabel: { not: null }, OR: [{ orderReferences: { hasSome: orderCodes } }, { bankReference: { in: bankRefs } }] },
    select: { accountId: true, orderReferences: true, bankReference: true, jevLabel: true, jevConfidence: true },
  });
  for (const order of review) {
    const related = credits.filter(credit => creditRelatesTo(order, credit));
    if (related.length) labels.set(order.token, related.map(credit => ({ label: credit.jevLabel as string, confidence: credit.jevConfidence ?? 0, bankReference: credit.bankReference })));
  }
  return labels;
}
