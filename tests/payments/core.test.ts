import { test } from "node:test";
import assert from "node:assert/strict";
import { newPaymentReference, orderReferences, normalizeBankReference, moneyToPaise, statementDate, upiPaymentUrl, exactPaymentMatch, MatchOrder, MatchCredit } from "../../lib/payments/core";

const reference = "BZ27ABCDEFGHJK";
const order: MatchOrder = { token: "order", paymentAccountId: "account-a", paymentReference: reference, claimedBankReference: null, amount: BigInt(800), created_at: new Date("2026-01-05T10:00:00Z"), approved: false, rejected: false };
const credit: MatchCredit = { id: "credit", accountId: "account-a", bankReference: "612345678901", amountPaise: BigInt(80000), direction: "CREDIT", description: `UPI BREEZE ${reference}`, orderReferences: [reference], conflict: false, bookedAt: new Date("2026-01-05"), reviewed: true, matchedToken: null };

test("UPI QR preserves recipient, amount, and public order code without exposing the private checkout token", () => {
  const url = new URL(upiPaymentUrl({ upiId: "recipient@bank", payeeName: "Test Person", amount: "800", reference }));
  assert.equal(url.searchParams.get("am"), "800.00");
  assert.equal(url.searchParams.get("tn"), `BREEZE ${reference}`);
  assert.equal(url.searchParams.get("tr"), reference);
  assert.equal(url.searchParams.get("pa"), "recipient@bank");
  assert.equal(url.searchParams.has("mc"), false);
});
test("references cannot be guessed from amounts or silently shortened", () => {
  assert.deepEqual(orderReferences(`UPI/${reference}/612345678901`), [reference]);
  assert.equal(normalizeBankReference("6123 4567 8901"), "612345678901");
  assert.throws(() => normalizeBankReference(reference));
  assert.throws(() => normalizeBankReference("123456789"));
  assert.equal(new Set(Array.from({ length: 5000 }, newPaymentReference)).size, 5000);
});
test("amounts use exact integer paise and dates reject ambiguous invalid calendars", () => {
  assert.equal(moneyToPaise("₹1,800.01"), BigInt(180001));
  assert.throws(() => moneyToPaise("800.001"));
  assert.throws(() => moneyToPaise("-800"));
  assert.equal(statementDate("05/01/2026").toISOString(), "2026-01-05T00:00:00.000Z");
  assert.equal(statementDate("05/01/2026", "MDY").toISOString(), "2026-05-01T00:00:00.000Z");
  assert.throws(() => statementDate("31/02/2026"));
});
test("one exact validated incoming credit is eligible even if customer never clicks I've paid", () => {
  assert.equal(exactPaymentMatch(order, [credit], true).credit?.id, credit.id);
  assert.equal(exactPaymentMatch({ ...order, created_at: new Date("2026-01-04T20:00:00Z") }, [credit], true).credit?.id, credit.id);
});
test("wrong amount, account, missing reference, conflicting claim, and allocation never approve", () => {
  for (const change of [{ amountPaise: BigInt(79900) }, { accountId: "account-b" }, { bankReference: null }, { conflict: true }, { reviewed: false }, { matchedToken: "other-order" }, { orderReferences: [reference, "BZ27JKLMNPQRST"] }]) {
    assert.equal(exactPaymentMatch(order, [{ ...credit, ...change }], true).credit, null);
  }
  assert.equal(exactPaymentMatch({ ...order, claimedBankReference: "612345678999" }, [credit], true).credit, null);
});
test("unverified personal-account notes, debits, reversals and duplicate credits go to review", () => {
  assert.equal(exactPaymentMatch(order, [credit], false).credit, null);
  assert.equal(exactPaymentMatch(order, [credit, { ...credit, id: "debit", direction: "DEBIT" }], true).credit, null);
  assert.equal(exactPaymentMatch(order, [credit, { ...credit, id: "duplicate" }], true).credit, null);
  assert.equal(exactPaymentMatch(order, [{ ...credit, description: `UPI reversal ${reference}` }], true).credit, null);
  assert.equal(exactPaymentMatch(order, [{ ...credit, bookedAt: new Date("2026-01-04") }], true).credit, null);
});
test("complete customer bank reference can match without note support; another order's code blocks it", () => {
  const claimed = { ...order, claimedBankReference: credit.bankReference };
  assert.equal(exactPaymentMatch(claimed, [{ ...credit, orderReferences: [] }], false).credit?.id, credit.id);
  assert.equal(exactPaymentMatch(claimed, [{ ...credit, orderReferences: ["BZ27JKLMNPQRST"] }], false).credit, null);
});
