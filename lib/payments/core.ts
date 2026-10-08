import { randomBytes, createHash } from "node:crypto";

export const REFERENCE_PATTERN = /\bBZ27[A-HJ-NP-Z2-9]{10}\b/g;
const ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789";

export function newPaymentReference() {
  return "BZ27" + [...randomBytes(10)].map(value => ALPHABET[value % ALPHABET.length]).join("");
}

export function orderReferences(text: string): string[] {
  return [...new Set(text.toUpperCase().match(REFERENCE_PATTERN) || [])];
}

export function normalizeBankReference(value: string): string {
  const reference = value.trim().toUpperCase().replace(/[\s-]/g, "");
  if (!/^[A-Z0-9]{12,35}$/.test(reference) || orderReferences(reference).length) {
    throw new Error("Enter the complete bank reference / UTR, not the Breeze order code or a shortened reference.");
  }
  return reference;
}

export function bankReferenceFromText(text: string): string | null {
  const references = [...new Set(text.match(/\b\d{12}\b/g) || [])];
  return references.length === 1 ? references[0] : null;
}

export function moneyToPaise(value: string): bigint {
  const normalized = value.trim().replace(/^(?:INR|Rs\.?|₹)\s*/i, "").replace(/,/g, "");
  if (!/^\d+(?:\.\d{1,2})?$/.test(normalized)) throw new Error(`Invalid amount: ${value}`);
  const [whole, fraction = ""] = normalized.split(".");
  const result = BigInt(whole) * BigInt(100) + BigInt(fraction.padEnd(2, "0"));
  if (result > BigInt("100000000000")) throw new Error("Amount exceeds the supported statement limit.");
  return result;
}

export function statementDate(value: string, order: "DMY" | "MDY" = "DMY"): Date {
  const input = value.trim();
  let year: number, month: number, day: number;
  const iso = /^(\d{4})-(\d{2})-(\d{2})(?:[ T].*)?$/.exec(input);
  const numeric = /^(\d{1,2})[/-](\d{1,2})[/-](\d{4})(?:\s.*)?$/.exec(input);
  const named = /^(\d{1,2})[\s/-]([A-Za-z]{3,9})[\s/-](\d{4})$/.exec(input);
  if (iso) [, year, month, day] = iso.map(Number);
  else if (numeric) {
    year = Number(numeric[3]);
    day = Number(numeric[order === "DMY" ? 1 : 2]);
    month = Number(numeric[order === "DMY" ? 2 : 1]);
  } else if (named) {
    year = Number(named[3]); day = Number(named[1]);
    month = ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"].indexOf(named[2].slice(0, 3).toLowerCase()) + 1;
  } else throw new Error(`Unsupported date: ${value}. Use a four-digit year and select the correct date format.`);
  const date = new Date(Date.UTC(year, month - 1, day));
  if (year < 2020 || year > 2100 || date.getUTCFullYear() !== year || date.getUTCMonth() !== month - 1 || date.getUTCDate() !== day) {
    throw new Error(`Invalid statement date: ${value}`);
  }
  return date;
}

export function upiPaymentUrl(input: { upiId: string; payeeName: string; amount: string; reference: string }) {
  if (!/^[\w.+-]{2,256}@[a-zA-Z][\w.-]{1,63}$/.test(input.upiId)) throw new Error("Invalid receiving UPI ID.");
  if (!/^BZ27[A-HJ-NP-Z2-9]{10}$/.test(input.reference)) throw new Error("Invalid payment reference.");
  const paise = moneyToPaise(input.amount);
  const amount = `${paise / BigInt(100)}.${(paise % BigInt(100)).toString().padStart(2, "0")}`;
  // Personal-account QR: do not fabricate merchant codes, signatures, or bank transaction IDs.
  const params = new URLSearchParams({ pa: input.upiId, pn: input.payeeName, am: amount, cu: "INR", tn: `BREEZE ${input.reference}`, tr: input.reference });
  return `upi://pay?${params.toString()}`;
}

export const sha256 = (value: string | Uint8Array) => createHash("sha256").update(value).digest("hex");

export type MatchOrder = {
  token: string; paymentAccountId: string | null; paymentReference: string | null;
  claimedBankReference: string | null; amount: bigint; created_at: Date;
  approved: boolean | null; rejected: boolean;
};
export type MatchCredit = {
  id: string; accountId: string; bankReference: string | null; amountPaise: bigint;
  direction: string; description: string; orderReferences: string[]; conflict: boolean;
  bookedAt: Date; reviewed: boolean; matchedToken: string | null;
};

export function exactPaymentMatch(order: MatchOrder, rows: MatchCredit[], noteMatchingVerified: boolean) {
  if (order.approved || order.rejected || !order.paymentAccountId) return { credit: null, reason: "Order is not eligible for automatic approval." };
  const related = rows.filter(row => row.accountId === order.paymentAccountId && (
    (order.paymentReference && row.orderReferences.includes(order.paymentReference)) ||
    (order.claimedBankReference && row.bankReference === order.claimedBankReference)
  ));
  if (!related.length) return { credit: null, reason: "Waiting for a statement containing this payment reference." };
  const credits = related.filter(row => row.direction === "CREDIT");
  if (credits.length !== 1) return { credit: null, reason: "Multiple or missing incoming credits need review." };
  const credit = credits[0];
  if (!credit.reviewed || credit.conflict) return { credit: null, reason: "Statement extraction or conflicting bank entries need review." };
  if (!credit.bankReference) return { credit: null, reason: "The statement entry has no complete bank reference." };
  if (credit.matchedToken && credit.matchedToken !== order.token) return { credit: null, reason: "This bank credit is already allocated to another order." };
  if (credit.orderReferences.length > 1 || (credit.orderReferences.length === 1 && credit.orderReferences[0] !== order.paymentReference)) {
    return { credit: null, reason: "The bank entry points to a different or ambiguous order." };
  }
  if (order.claimedBankReference && order.claimedBankReference !== credit.bankReference) return { credit: null, reason: "The customer's bank reference disagrees with the statement." };
  const exactOrderNote = Boolean(order.paymentReference && credit.orderReferences.includes(order.paymentReference));
  if (!order.claimedBankReference && (!exactOrderNote || !noteMatchingVerified)) return { credit: null, reason: "Order-note preservation has not been verified for this receiving account." };
  if (credit.amountPaise !== order.amount * BigInt(100)) return { credit: null, reason: "Bank credit does not equal the server-stored order total." };
  if (rows.some(row => row.accountId === credit.accountId && row.bankReference === credit.bankReference && (row.direction !== "CREDIT" || row.conflict))) {
    return { credit: null, reason: "A debit, reversal, or conflicting entry exists for this bank reference." };
  }
  const indiaTime = new Date(order.created_at.getTime() + 330 * 60000);
  const orderDay = Date.UTC(indiaTime.getUTCFullYear(), indiaTime.getUTCMonth(), indiaTime.getUTCDate());
  const days = (credit.bookedAt.getTime() - orderDay) / 86400000;
  if (days < 0 || days > 30 || credit.bookedAt.getTime() > Date.now() + 86400000) return { credit: null, reason: "The statement date falls outside the order's payment window." };
  if (/\b(?:revers(?:al|ed)|refund(?:ed)?|chargeback|failed)\b/i.test(credit.description)) return { credit: null, reason: "The statement description indicates a reversal, refund, or failed payment." };
  return { credit, reason: exactOrderNote ? "Exact order reference, receiving account, amount, and bank credit matched." : "Exact bank reference, receiving account, and amount matched." };
}
