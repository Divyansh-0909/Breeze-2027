import { NextRequest, NextResponse } from "next/server";
import { z } from "zod";
import { prisma } from "@/lib/prisma";
import { paymentAdmin, paymentError, PaymentError } from "@/lib/payments/http";
import { sha256 } from "@/lib/payments/core";
import { csvGrid, pdfGrid, mapStatementRows, StatementGrid, suggestColumns, ColumnMap } from "@/lib/payments/statements";
import { commitStatement } from "@/lib/payments/import";
import { jevReview } from "@/lib/payments/jev";

export const runtime = "nodejs";
export const maxDuration = 300;
const mappingSchema = z.object({ date: z.number().int(), description: z.number().int(), credit: z.number().int(), debit: z.number().int(), amount: z.number().int(), direction: z.number().int(), reference: z.number().int() });

export async function POST(req: NextRequest) {
  try {
    const auth = await paymentAdmin(req); if (auth.authorized === false) return auth.response;
    if (req.headers.get("content-type")?.includes("multipart/form-data")) {
      const form = await req.formData(), file = form.get("file"), accountId = String(form.get("accountId") || "");
      if (!(file instanceof File) || !file.size || file.size > 10 * 1024 * 1024) throw new PaymentError("Upload a PDF or CSV statement no larger than 10 MB.");
      const account = await prisma.paymentAccount.findUnique({ where: { id: accountId } });
      if (!account) throw new PaymentError("Choose the receiving account first.");
      const data = new Uint8Array(await file.arrayBuffer());
      const isPdf = Buffer.from(data.slice(0, 5)).toString() === "%PDF-";
      if (!isPdf && !file.name.toLowerCase().endsWith(".csv")) throw new PaymentError("Only bank PDF or CSV exports are supported.");
      let grid: StatementGrid;
      try { grid = isPdf ? await pdfGrid(data) : csvGrid(new TextDecoder("utf-8", { fatal: true }).decode(data)); }
      catch (error) { throw new PaymentError(error instanceof Error ? error.message : "Statement could not be extracted."); }
      if (grid.sourceText.length > 2000000) throw new PaymentError("Extracted statement text is too large. Split the statement into smaller files.");
      const fileHash = sha256(data);
      const draft = await prisma.bankStatement.upsert({ where: { accountId_fileHash: { accountId, fileHash } },
        create: { accountId, fileHash, filename: file.name.slice(0, 200), format: grid.format, extractedRows: { headers: grid.headers, rows: grid.rows, warnings: grid.warnings }, sourceText: grid.sourceText, importedBy: auth.userId }, update: {},
      });
      return NextResponse.json({ statementId: draft.id, accountId, reviewed: draft.reviewed, headers: grid.headers, rows: grid.rows.slice(0, 100), rowCount: grid.rows.length, warnings: grid.warnings, sourceText: grid.sourceText, columns: suggestColumns(grid.headers), format: grid.format });
    }
    const body = z.object({ action: z.enum(["preview", "commit", "jev"]), statementId: z.string().min(1), columns: mappingSchema.optional(), dateOrder: z.enum(["DMY", "MDY"]).default("DMY"), correctedCsv: z.string().max(2000000).optional(), accountConfirmed: z.boolean().optional(), extractionConfirmed: z.boolean().optional(), rowIndex: z.number().int().min(0).max(14999).optional(), offset: z.number().int().min(0).max(14999).default(0) }).parse(await req.json());
    const statement = await prisma.bankStatement.findUnique({ where: { id: body.statementId } });
    if (!statement) throw new PaymentError("Statement preview not found.", 404);
    const grid = body.correctedCsv ? csvGrid(body.correctedCsv) : statement.extractedRows as unknown as StatementGrid;
    if (body.action === "jev") {
      if (body.rowIndex === undefined || !grid.rows[body.rowIndex]) throw new PaymentError("Choose a statement row for Jev to review.");
      return NextResponse.json(await jevReview(grid.rows[body.rowIndex].join(" | ")));
    }
    if (!body.columns) throw new PaymentError("Map the statement columns first.");
    if (body.action === "preview") {
      const result = mapStatementRows(grid, body.columns as ColumnMap, body.dateOrder);
      return NextResponse.json({ headers: grid.headers, columns: body.columns, normalized: result.rows.slice(body.offset, body.offset + 100), offset: body.offset, transactionCount: result.rows.length, errors: result.errors.slice(0, 100), errorCount: result.errors.length, ignored: result.ignored });
    }
    return NextResponse.json(await commitStatement({ statementId: body.statementId, dateOrder: body.dateOrder, correctedCsv: body.correctedCsv, columns: body.columns as ColumnMap, accountConfirmed: Boolean(body.accountConfirmed), extractionConfirmed: Boolean(body.extractionConfirmed) }, auth.userId));
  } catch (error) { return paymentError(error); }
}
