-- AlterTable
ALTER TABLE "PendingTransaction" ADD COLUMN     "paymentAccountId" TEXT,
ADD COLUMN     "paymentPayeeName" TEXT,
ADD COLUMN     "paymentReference" TEXT,
ADD COLUMN     "paymentUpiId" TEXT;

-- AlterTable
ALTER TABLE "SubmittedTransaction" ADD COLUMN     "bankReference" TEXT,
ADD COLUMN     "claimedBankReference" TEXT,
ADD COLUMN     "matchedCreditId" TEXT,
ADD COLUMN     "paymentAccountId" TEXT,
ADD COLUMN     "paymentPayeeName" TEXT,
ADD COLUMN     "paymentReference" TEXT,
ADD COLUMN     "paymentReportedAt" TIMESTAMP(3),
ADD COLUMN     "paymentReviewReason" TEXT,
ADD COLUMN     "paymentStatus" TEXT NOT NULL DEFAULT 'AWAITING_STATEMENT',
ADD COLUMN     "paymentUpiId" TEXT;

-- CreateTable
CREATE TABLE "PaymentAccount" (
    "id" TEXT NOT NULL,
    "label" TEXT NOT NULL,
    "bankName" TEXT NOT NULL,
    "accountLast4" TEXT NOT NULL,
    "upiId" TEXT NOT NULL,
    "payeeName" TEXT NOT NULL,
    "active" BOOLEAN NOT NULL DEFAULT false,
    "noteMatchingVerified" BOOLEAN NOT NULL DEFAULT false,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "createdBy" TEXT NOT NULL,

    CONSTRAINT "PaymentAccount_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "BankStatement" (
    "id" TEXT NOT NULL,
    "accountId" TEXT NOT NULL,
    "fileHash" TEXT NOT NULL,
    "filename" TEXT NOT NULL,
    "format" TEXT NOT NULL,
    "extractedRows" JSONB NOT NULL,
    "sourceText" TEXT NOT NULL,
    "reviewed" BOOLEAN NOT NULL DEFAULT false,
    "importedAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "importedBy" TEXT NOT NULL,

    CONSTRAINT "BankStatement_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "BankCredit" (
    "id" TEXT NOT NULL,
    "accountId" TEXT NOT NULL,
    "statementId" TEXT NOT NULL,
    "identity" TEXT NOT NULL,
    "rowHash" TEXT NOT NULL,
    "bookedAt" TIMESTAMP(3) NOT NULL,
    "amountPaise" BIGINT NOT NULL,
    "direction" TEXT NOT NULL,
    "bankReference" TEXT,
    "description" TEXT NOT NULL,
    "orderReferences" TEXT[],
    "conflict" BOOLEAN NOT NULL DEFAULT false,

    CONSTRAINT "BankCredit_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "PaymentAudit" (
    "id" TEXT NOT NULL,
    "token" TEXT NOT NULL,
    "action" TEXT NOT NULL,
    "actor" TEXT NOT NULL,
    "details" JSONB NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "PaymentAudit_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "PaymentEmail" (
    "id" TEXT NOT NULL,
    "token" TEXT NOT NULL,
    "kind" TEXT NOT NULL,
    "status" TEXT NOT NULL DEFAULT 'PENDING',
    "attempts" INTEGER NOT NULL DEFAULT 0,
    "lastError" TEXT,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "PaymentEmail_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE UNIQUE INDEX "BankStatement_accountId_fileHash_key" ON "BankStatement"("accountId", "fileHash");

-- CreateIndex
CREATE INDEX "BankCredit_accountId_bankReference_idx" ON "BankCredit"("accountId", "bankReference");

-- CreateIndex
CREATE UNIQUE INDEX "BankCredit_accountId_identity_key" ON "BankCredit"("accountId", "identity");

-- CreateIndex
CREATE UNIQUE INDEX "PaymentEmail_token_kind_key" ON "PaymentEmail"("token", "kind");

-- CreateIndex
CREATE UNIQUE INDEX "PendingTransaction_paymentReference_key" ON "PendingTransaction"("paymentReference");

-- CreateIndex
CREATE UNIQUE INDEX "SubmittedTransaction_paymentReference_key" ON "SubmittedTransaction"("paymentReference");

-- CreateIndex
CREATE UNIQUE INDEX "SubmittedTransaction_matchedCreditId_key" ON "SubmittedTransaction"("matchedCreditId");

-- CreateIndex
CREATE INDEX "SubmittedTransaction_paymentAccountId_approved_rejected_idx" ON "SubmittedTransaction"("paymentAccountId", "approved", "rejected");

-- AddForeignKey
ALTER TABLE "SubmittedTransaction" ADD CONSTRAINT "SubmittedTransaction_paymentAccountId_fkey" FOREIGN KEY ("paymentAccountId") REFERENCES "PaymentAccount"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "SubmittedTransaction" ADD CONSTRAINT "SubmittedTransaction_matchedCreditId_fkey" FOREIGN KEY ("matchedCreditId") REFERENCES "BankCredit"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "BankStatement" ADD CONSTRAINT "BankStatement_accountId_fkey" FOREIGN KEY ("accountId") REFERENCES "PaymentAccount"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "BankCredit" ADD CONSTRAINT "BankCredit_accountId_fkey" FOREIGN KEY ("accountId") REFERENCES "PaymentAccount"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "BankCredit" ADD CONSTRAINT "BankCredit_statementId_fkey" FOREIGN KEY ("statementId") REFERENCES "BankStatement"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "PaymentAudit" ADD CONSTRAINT "PaymentAudit_token_fkey" FOREIGN KEY ("token") REFERENCES "SubmittedTransaction"("token") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "PaymentEmail" ADD CONSTRAINT "PaymentEmail_token_fkey" FOREIGN KEY ("token") REFERENCES "SubmittedTransaction"("token") ON DELETE RESTRICT ON UPDATE CASCADE;

-- Only one account can receive new checkouts. Rotation does not mutate old orders.
ALTER TABLE "PendingTransaction" ADD COLUMN "pricingSnapshot" JSONB;
ALTER TABLE "SubmittedTransaction" ADD COLUMN "pricingSnapshot" JSONB;
ALTER TABLE "PaymentAccount" ADD COLUMN "noteVerifiedBy" TEXT, ADD COLUMN "noteVerifiedAt" TIMESTAMP(3);
CREATE UNIQUE INDEX "PaymentAccount_one_active" ON "PaymentAccount" (("active")) WHERE "active" = true;

-- Statements, credits, audit trails and account settings are server-managed.
-- No browser/Supabase anon or authenticated policies grant direct access.
ALTER TABLE "PaymentAccount" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "BankStatement" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "BankCredit" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "PaymentAudit" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "PaymentEmail" ENABLE ROW LEVEL SECURITY;
