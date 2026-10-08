import Papa from "papaparse";
import { bankReferenceFromText, moneyToPaise, normalizeBankReference, orderReferences, sha256, statementDate } from "./core";

export type ColumnMap = { date: number; description: number; credit: number; debit: number; amount: number; direction: number; reference: number };
export type StatementGrid = { headers: string[]; rows: string[][]; warnings: string[]; sourceText: string; format: string };
export type StatementRow = {
  bookedAt: string; amountPaise: string; direction: "CREDIT" | "DEBIT";
  bankReference: string | null; description: string; orderReferences: string[];
  rowHash: string; identity: string; sourceRow: number;
};

export function csvGrid(text: string): StatementGrid {
  const result = Papa.parse<string[]>(text.replace(/^\uFEFF/, ""), { skipEmptyLines: "greedy" });
  if (result.errors.length) throw new Error(`CSV could not be read: ${result.errors[0].message}`);
  if (result.data.length < 2 || result.data.length > 15001) throw new Error("Upload a CSV containing a header and 1–15,000 statement rows.");
  const headerRow = result.data.findIndex(row => row.some(cell => /date/i.test(cell)) && row.some(cell => /credit|deposit|amount/i.test(cell)));
  const start = headerRow < 0 ? 0 : headerRow;
  const headers = result.data[start].map(cell => cell.trim());
  if (headers.length < 3 || headers.length > 40) throw new Error("The statement needs at least three columns and no more than forty.");
  return { headers, rows: result.data.slice(start + 1), warnings: start ? ["Bank heading rows were skipped. Confirm the selected account and column mapping."] : [], sourceText: text, format: "CSV" };
}

export function suggestColumns(headers: string[]): ColumnMap {
  const find = (pattern: RegExp) => headers.findIndex(header => pattern.test(header.trim()));
  return {
    date: find(/^(?:transaction |txn |booking |value )?date$/i),
    description: find(/description|narration|particular|remark|details/i),
    credit: find(/credit|deposit/i), debit: find(/debit|withdraw/i),
    amount: find(/^amount(?:\s*\(.*\))?$/i), direction: find(/^(?:type|direction|dr.?cr|cr.?dr)$/i),
    reference: find(/^(?:bank reference|reference|reference no\.?|utr|rrn|ref(?:erence)?\.?\s*(?:number|no\.?))$/i),
  };
}

export function mapStatementRows(grid: Pick<StatementGrid, "headers" | "rows">, columns: ColumnMap, dateOrder: "DMY" | "MDY") {
  if (columns.date < 0 || columns.description < 0 || (columns.credit < 0 && (columns.amount < 0 || columns.direction < 0))) {
    throw new Error("Map a date, description, and either credit/debit columns or an amount plus credit/debit direction.");
  }
  const selected = Object.values(columns).filter(index => index >= 0);
  if (selected.some(index => !Number.isInteger(index) || index >= grid.headers.length) || new Set(selected).size !== selected.length) {
    throw new Error("Each mapped field must use a different valid column.");
  }
  const rows: StatementRow[] = [], errors: { row: number; message: string }[] = [];
  let ignored = 0;
  grid.rows.forEach((cells, index) => {
    try {
      if (cells.every(cell => !cell.trim())) { ignored++; return; }
      if (selected.every(column => (cells[column] || "").trim() === grid.headers[column].trim())) { ignored++; return; }
      const get = (column: number) => column < 0 ? "" : (cells[column] || "").trim();
      const dateText = get(columns.date), description = get(columns.description);
      if (!dateText && /opening balance|closing balance|total|page \d/i.test(cells.join(" "))) { ignored++; return; }
      const bookedAt = statementDate(dateText, dateOrder).toISOString();
      if (!description || description.length > 4000) throw new Error("A transaction description is missing or too long.");
      let amount: bigint, direction: "CREDIT" | "DEBIT";
      if (columns.credit >= 0) {
        const credit = get(columns.credit), debit = get(columns.debit);
        const parse = (value: string) => !value || /^(?:-|—|0(?:\.00)?)$/.test(value) ? BigInt(0) : moneyToPaise(value);
        const incoming = parse(credit), outgoing = parse(debit);
        if (incoming > BigInt(0) && outgoing > BigInt(0)) throw new Error("Both debit and credit contain money.");
        if (incoming === BigInt(0) && outgoing === BigInt(0)) { ignored++; return; }
        direction = incoming > BigInt(0) ? "CREDIT" : "DEBIT";
        amount = incoming > BigInt(0) ? incoming : outgoing;
      } else {
        const type = get(columns.direction).toUpperCase();
        if (/^(?:CR|CREDIT|C)$/.test(type)) direction = "CREDIT";
        else if (/^(?:DR|DEBIT|D)$/.test(type)) direction = "DEBIT";
        else throw new Error("Transaction direction must explicitly identify CREDIT/CR or DEBIT/DR.");
        amount = moneyToPaise(get(columns.amount));
        if (amount === BigInt(0)) { ignored++; return; }
      }
      const reference = get(columns.reference);
      const bankReference = reference ? normalizeBankReference(reference) : bankReferenceFromText(description);
      const canonical = `${bookedAt}|${amount}|${direction}|${bankReference || ""}|${description}`;
      const rowHash = sha256(canonical);
      rows.push({ bookedAt, amountPaise: amount.toString(), direction, bankReference, description, orderReferences: orderReferences(description), rowHash,
        identity: bankReference ? `${direction}:${bankReference}` : `ROW:${rowHash}`, sourceRow: index + 2 });
    } catch (error) { errors.push({ row: index + 2, message: error instanceof Error ? error.message : "Invalid row" }); }
  });
  return { rows, errors, ignored };
}

export async function pdfGrid(data: Uint8Array): Promise<StatementGrid> {
  const { PDFParse } = await import("pdf-parse");
  const parser = new PDFParse({ data });
  try {
    const info = await parser.getInfo();
    if (info.total > 100) throw new Error("PDF statements are limited to 100 pages per upload. Split larger statements.");
    const text = await parser.getText({ cellSeparator: "\t", lineEnforce: true });
    let sourceText = text.pages.map(page => page.text).join("\n");
    const warnings: string[] = ["Review PDF extraction against the original statement before importing. Wrapped descriptions and OCR can change columns or digits."];
    const dateLines = sourceText.match(/^\s*(?:\d{1,2}[/-]\d{1,2}[/-]\d{4}|\d{4}-\d{2}-\d{2})/gm);
    if (!dateLines?.length) {
      if (info.total > 10) throw new Error("This PDF needs OCR. Upload up to 10 scanned pages at a time, or export CSV from your bank.");
      const { createWorker } = await import("tesseract.js");
      const { mkdir } = await import("node:fs/promises");
      const path = await import("node:path");
      const cachePath = process.env.PAYMENT_OCR_CACHE || path.join(process.cwd(), ".payment-ocr-cache");
      await mkdir(cachePath, { recursive: true });
      const worker = await createWorker("eng", 1, { cachePath });
      try {
        sourceText = "";
        for (let pageNumber = 1; pageNumber <= info.total; pageNumber++) {
          const screenshot = await parser.getScreenshot({ partial: [pageNumber], desiredWidth: 1800, imageDataUrl: false });
          const result = await worker.recognize(Buffer.from(screenshot.pages[0].data));
          sourceText += result.data.text + "\n";
        }
        warnings.push("OCR was used. References and amounts MUST be checked against the original PDF.");
      } finally { await worker.terminate(); }
    }
    const lines = sourceText.split(/\r?\n/).map(line => line.trim()).filter(Boolean);
    const tableLines = lines.filter(line => line.includes("\t"));
    if (tableLines.length > 1) {
      const grid = csvGrid(tableLines.map(line => line.split("\t").map(cell => `"${cell.replace(/"/g, '""')}"`).join(",")).join("\n"));
      return { ...grid, sourceText, format: "PDF", warnings: [...warnings, ...grid.warnings] };
    }
    // Keep verbatim text when no reliable table exists. The admin supplies corrected CSV;
    // never guess which of several monetary values is a credit.
    return { headers: [], rows: [], sourceText, format: "PDF", warnings: [...warnings, "No reliable table was found. Use the extracted text to prepare CSV with date, description, credit, debit, and bank reference columns."] };
  } finally { await parser.destroy(); }
}
