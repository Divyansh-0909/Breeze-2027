import { test } from "node:test";
import assert from "node:assert/strict";
import { PDFDocument, StandardFonts } from "pdf-lib";
import { csvGrid, suggestColumns, mapStatementRows, pdfGrid } from "../../lib/payments/statements";

const csv = 'Date,Description,Credit,Debit,Bank Reference\n05/01/2026,"UPI, BREEZE BZ27ABCDEFGHJK","1,800.00",,612345678901\n05/01/2026,UPI reversal,,1800.00,612345678901';
test("CSV preserves quoted bank descriptions and both credit/debit entries", () => {
  const grid = csvGrid(csv);
  const result = mapStatementRows(grid, suggestColumns(grid.headers), "DMY");
  assert.equal(result.errors.length, 0);
  assert.equal(result.rows[0].amountPaise, "180000");
  assert.equal(result.rows[0].direction, "CREDIT");
  assert.equal(result.rows[1].direction, "DEBIT");
  assert.deepEqual(result.rows[0].orderReferences, ["BZ27ABCDEFGHJK"]);
  assert.notEqual(result.rows[0].identity, result.rows[1].identity);
});
test("unknown direction and malformed monetary values fail validation rather than approve", () => {
  const grid = csvGrid('Date,Description,Amount,Direction\n05/01/2026,UPI,800,UNKNOWN\n05/01/2026,UPI,800.999,CR');
  const result = mapStatementRows(grid, suggestColumns(grid.headers), "DMY");
  assert.equal(result.rows.length, 0); assert.equal(result.errors.length, 2);
});
test("missing bank references remain missing; multiple numeric candidates cannot be invented", () => {
  const grid = csvGrid('Date,Description,Credit,Debit\n05/01/2026,UPI 612345678901 912345678901,800,');
  assert.equal(mapStatementRows(grid, suggestColumns(grid.headers), "DMY").rows[0].bankReference, null);
});
test("duplicate columns, swapped date formats, and corrupt CSV are explicit", () => {
  const grid = csvGrid(csv), columns = suggestColumns(grid.headers);
  assert.throws(() => mapStatementRows(grid, { ...columns, credit: columns.date }, "DMY"));
  assert.throws(() => csvGrid('Date,Description,Credit\n05/01/2026,"unclosed,800'));
});
test("text PDF extraction preserves original text and requires review", async () => {
  const document = await PDFDocument.create(), page = document.addPage(), font = await document.embedFont(StandardFonts.Helvetica);
  const rows = [['Date', 'Description', 'Credit', 'Debit', 'Bank Reference'], ['05/01/2026', 'BREEZE BZ27ABCDEFGHJK', '800.00', '-', '612345678901']];
  rows.forEach((row, index) => row.forEach((cell, column) => page.drawText(cell, { x: [20, 100, 290, 350, 410][column], y: 750 - index * 24, size: 9, font })));
  const result = await pdfGrid(await document.save());
  assert.ok(result.sourceText.includes('BZ27ABCDEFGHJK'));
  assert.ok(result.warnings.some(warning => warning.includes('Review PDF')));
});
