import { prisma } from "@/lib/prisma";
import { redirect } from "next/navigation";
import { CheckoutForm } from "@/components/checkout/CheckoutForm";
import { upiPaymentUrl } from "@/lib/payments/core";
import { tokenPattern } from "@/lib/payments/http";

export const dynamic = "force-dynamic";

interface PageProps {
  searchParams: Promise<{ [key: string]: string | undefined }>;
}

export const metadata = {
  title: "Checkout - Breeze '27",
  description: "Checkout Page for Transactions",
};

export default async function CheckoutPage({ searchParams }: PageProps) {
  const params = await searchParams;
  const token = params.token;
  if (!token || !tokenPattern.test(token)) {
    redirect("/cart");
  }
  const [pending, saved] = await Promise.all([prisma.pendingTransaction.findUnique({
    where: { id: token },
  }), prisma.submittedTransaction.findUnique({ where: { token }, include: { paymentAccount: { select: { noteMatchingVerified: true } } } })]);
  const transaction = saved || pending;

  if (!transaction) {
    redirect("/cart");
  }
  const paymentAccount = transaction.paymentAccountId ? await prisma.paymentAccount.findUnique({ where: { id: transaction.paymentAccountId }, select: { noteMatchingVerified: true } }) : null;

  return (
    <div className="pt-20 container mx-auto py-8">
      <CheckoutForm token={token} amount={transaction.amount.toString()} reference={transaction.paymentReference}
        prepared={Boolean(saved)} initialStatus={saved?.paymentStatus} noteVerified={paymentAccount?.noteMatchingVerified}
        payeeName={transaction.paymentPayeeName} upiId={transaction.paymentUpiId}
        paymentUrl={saved && saved.amount > BigInt(0) && saved.paymentReference && saved.paymentUpiId ? upiPaymentUrl({ upiId: saved.paymentUpiId, payeeName: saved.paymentPayeeName, amount: saved.amount.toString(), reference: saved.paymentReference }) : null} />
    </div>
  );
}
