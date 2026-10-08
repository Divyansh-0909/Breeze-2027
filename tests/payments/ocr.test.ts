import { test } from "node:test";
import assert from "node:assert/strict";
import { createCanvas } from "@napi-rs/canvas";
import { PDFDocument } from "pdf-lib";
import { receiptText } from "../../lib/payments/ocr";
import { bankReferenceFromText } from "../../lib/payments/core";
import { pdfGrid } from "../../lib/payments/statements";

test("local OCR extracts a receipt reference and reads a scanned PDF without trusting it for approval", async () => {
  const canvas = createCanvas(1500, 550), context = canvas.getContext("2d");
  context.fillStyle = "white"; context.fillRect(0, 0, 1500, 550);
  context.fillStyle = "black"; context.font = "36px Arial";
  ["Date Description Credit Debit Bank Reference", "05/01/2026 BREEZE BZ27ABCDEFGHJK 800.00", "UTR 612345678901"].forEach((line, index) => context.fillText(line, 40, 90 + index * 100));
  const png = canvas.toBuffer("image/png");
  const text = await receiptText(png);
  assert.equal(bankReferenceFromText(text), "612345678901");
  const document = await PDFDocument.create();
  const page = document.addPage([1500, 550]), image = await document.embedPng(png);
  page.drawImage(image, { x: 0, y: 0, width: 1500, height: 550 });
  const extracted = await pdfGrid(await document.save());
  assert.ok(extracted.warnings.some(warning => warning.includes("OCR was used")));
  assert.ok(extracted.sourceText.includes("612345678901"));
  assert.equal(extracted.rows.length, 0); // No reliable columns: must be corrected/reviewed.
});
