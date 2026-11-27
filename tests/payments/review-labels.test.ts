import { test } from "node:test";
import assert from "node:assert/strict";
import { creditRelatesTo, reviewCreditText } from "../../lib/payments/review-labels";

const order = { paymentAccountId: "acct-a", paymentReference: "BZ27ABCDEFGHJK", claimedBankReference: "412345678901", bankReference: null };

test("review labels attach only to bank entries on the same account with the order's code or bank reference", () => {
  assert.equal(creditRelatesTo(order, { accountId: "acct-a", orderReferences: ["BZ27ABCDEFGHJK"], bankReference: null }), true);
  assert.equal(creditRelatesTo(order, { accountId: "acct-a", orderReferences: [], bankReference: "412345678901" }), true);
  assert.equal(creditRelatesTo(order, { accountId: "acct-b", orderReferences: ["BZ27ABCDEFGHJK"], bankReference: "412345678901" }), false);
  assert.equal(creditRelatesTo(order, { accountId: "acct-a", orderReferences: ["BZ27OTHERORDER1"], bankReference: "999999999999" }), false);
  assert.equal(creditRelatesTo({ ...order, paymentAccountId: null }, { accountId: "acct-a", orderReferences: ["BZ27ABCDEFGHJK"], bankReference: null }), false);
});

test("Jev sees the bank's own fields with exact paise, and missing references stay missing", () => {
  const text = reviewCreditText({ bookedAt: new Date("2026-11-20T00:00:00Z"), direction: "CREDIT", amountPaise: BigInt(80005), bankReference: null, description: "UPI/BREEZE BZ27ABCDEFGHJK" });
  assert.equal(text, "2026-11-20 | CREDIT | INR 800.05 | no bank reference | UPI/BREEZE BZ27ABCDEFGHJK");
});
