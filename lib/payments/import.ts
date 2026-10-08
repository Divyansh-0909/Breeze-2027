import { prisma } from "@/lib/prisma";
import { mapStatementRows, ColumnMap, csvGrid, StatementGrid } from "./statements";
import { PaymentError } from "./http";

export async function commitStatement(input: { statementId: string; columns: ColumnMap; dateOrder: "DMY" | "MDY"; correctedCsv?: string; accountConfirmed: boolean; extractionConfirmed: boolean }, actor: string) {
  if (!input.accountConfirmed || !input.extractionConfirmed) throw new PaymentError("Confirm the receiving account and check the extracted statement rows before importing.");
  const statement = await prisma.bankStatement.findUniqueOrThrow({ where: { id: input.statementId } });
  const original = statement.extractedRows as unknown as StatementGrid;
  const grid = input.correctedCsv ? csvGrid(input.correctedCsv) : original;
  const parsed = mapStatementRows(grid, input.columns, input.dateOrder);
  if (parsed.errors.length) throw new PaymentError(`Fix ${parsed.errors.length} invalid statement row(s) before importing. Row ${parsed.errors[0].row}: ${parsed.errors[0].message}`);
  if (!parsed.rows.length) throw new PaymentError("No valid transactions were found in the mapped columns.");
  return prisma.$transaction(async tx => {
    await tx.$queryRaw`SELECT id FROM "PaymentAccount" WHERE id = ${statement.accountId} FOR UPDATE`;
    const current = await tx.bankStatement.findUniqueOrThrow({ where: { id: statement.id } });
    if (current.reviewed) return { accountId: statement.accountId, imported: 0, duplicates: parsed.rows.length, conflicts: 0, alreadyImported: true };
    const data = parsed.rows.map(row => ({
      accountId: statement.accountId, statementId: statement.id, identity: row.identity, rowHash: row.rowHash,
      bookedAt: new Date(row.bookedAt), amountPaise: BigInt(row.amountPaise), direction: row.direction,
      bankReference: row.bankReference, description: row.description, orderReferences: row.orderReferences,
    }));
    const created = await tx.bankCredit.createMany({ data, skipDuplicates: true });
    const stored = await tx.bankCredit.findMany({ where: { accountId: statement.accountId, identity: { in: data.map(row => row.identity) } } });
    const byIdentity = new Map(stored.map(row => [row.identity, row]));
    const conflicts = new Set<string>();
    for (const row of data) {
      const prior = byIdentity.get(row.identity);
      const reversal = (text: string) => /\b(?:revers(?:al|ed)|refund(?:ed)?|chargeback|failed)\b/i.test(text);
      if (prior && (prior.amountPaise !== row.amountPaise || prior.bookedAt.getTime() !== row.bookedAt.getTime() || prior.orderReferences.join(",") !== row.orderReferences.join(",") || reversal(prior.description) !== reversal(row.description))) conflicts.add(prior.id);
    }
    if (conflicts.size) await tx.bankCredit.updateMany({ where: { id: { in: [...conflicts] } }, data: { conflict: true } });
    await tx.bankStatement.update({ where: { id: statement.id }, data: { reviewed: true, importedBy: actor, extractedRows: { headers: grid.headers, rows: grid.rows, warnings: grid.warnings, columns: input.columns, dateOrder: input.dateOrder, manuallyCorrected: Boolean(input.correctedCsv), transactionCount: parsed.rows.length } } });
    return { accountId: statement.accountId, imported: created.count, duplicates: data.length - created.count, conflicts: conflicts.size, alreadyImported: false };
  }, { timeout: 60000 });
}
