-- Optional Jev review suggestions for bank entries in the review queue.
-- Additive and nullable: existing rows, matching and approvals are unchanged.
ALTER TABLE "BankCredit" ADD COLUMN IF NOT EXISTS "jevLabel" TEXT;
ALTER TABLE "BankCredit" ADD COLUMN IF NOT EXISTS "jevConfidence" DOUBLE PRECISION;
ALTER TABLE "BankCredit" ADD COLUMN IF NOT EXISTS "jevCheckedAt" TIMESTAMP(3);
