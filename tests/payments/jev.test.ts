import { test } from "node:test";
import assert from "node:assert/strict";
import { jevReview } from "../../lib/payments/jev";

test("Jev is optional and uses its documented typed decision API", async () => {
  const priorKey = process.env.TYPESAFE_API_KEY, priorFetch = global.fetch;
  try {
    delete process.env.TYPESAFE_API_KEY;
    assert.equal((await jevReview('UPI credit')).enabled, false);
    process.env.TYPESAFE_API_KEY = 'test-only-not-a-real-key';
    global.fetch = async (url, options) => {
      assert.equal(url, 'https://api.typesafe.ai/v1/systemone');
      const body = JSON.parse(String(options.body));
      assert.equal(body.questions.entryKind.type, 'choice');
      assert.ok(body.state.untrustedStatementText);
      return new Response(JSON.stringify({ answers: { entryKind: { choice: 'incoming', confidence: 0.9 } }, usage: { input_tokens: 100 } }));
    };
    const result = await jevReview('UPI credit');
    assert.equal(result.classification, 'incoming'); assert.equal(result.inputTokens, 100);
    assert.equal('approved' in result, false);
  } finally { global.fetch = priorFetch; if (priorKey === undefined) delete process.env.TYPESAFE_API_KEY; else process.env.TYPESAFE_API_KEY = priorKey; }
});
