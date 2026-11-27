import { loadEnvConfig } from "@next/env";
loadEnvConfig(process.cwd());

async function main() {
  const { prisma } = await import("../../lib/prisma");
  const { reconcileAccount } = await import("../../lib/payments/service");
  const { drainPaymentEmails } = await import("../../lib/payments/email");
  const { labelReviewCredits } = await import("../../lib/payments/review-labels");
  if (!process.env.DATABASE_URL || process.env.DATABASE_URL.includes("USER:PASSWORD@HOST")) throw new Error("Configure a development DATABASE_URL before starting the payment worker.");
  let stopping = false;
  process.on("SIGINT", () => { stopping = true; });
  process.on("SIGTERM", () => { stopping = true; });
  do {
    try {
      const accounts = await prisma.paymentAccount.findMany({ where: { statements: { some: { reviewed: true } } }, select: { id: true } });
      let approved = 0, labelled = 0;
      for (const account of accounts) {
        let cursor: string | undefined;
        do {
          const batch = await reconcileAccount(account.id, "PAYMENT_WORKER", cursor);
          approved += batch.approved;
          cursor = batch.hasMore ? batch.nextCursor : undefined;
        } while (cursor && !stopping);
        // Advisory Jev labels for the review queue; a Jev failure never stops matching or email.
        const jev = await labelReviewCredits(account.id).catch(() => ({ labelled: 0, error: "Jev labelling failed." }));
        if (jev.labelled) labelled += jev.labelled;
      }
      const email = await drainPaymentEmails();
      console.log(`[payments] ${approved} orders confirmed; ${labelled} review entries labelled by Jev; ${email.sent} emails sent.`);
    } catch (error) { console.error("[payments] Worker cycle failed:", error instanceof Error ? error.name : "Unknown error"); }
    if (process.argv.includes("--once")) break;
    if (!stopping) await new Promise(resolve => setTimeout(resolve, 30000));
  } while (!stopping);
  await prisma.$disconnect();
}

main().catch(error => { console.error(error.message); process.exitCode = 1; });
