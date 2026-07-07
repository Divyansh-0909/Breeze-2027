import { prisma } from "@/lib/prisma";
import { redirect } from "next/navigation";
import { CheckoutForm } from "@/components/checkout/CheckoutForm";

export const dynamic = "force-dynamic";

interface PageProps {
  searchParams: Promise<{ [key: string]: string | undefined }>;
}

export const metadata = {
  title: "Checkout - Breeze '26",
  description: "Checkout Page for Transactions",
};

export default async function CheckoutPage({ searchParams }: PageProps) {
  const params = await searchParams;
  const token = params.token;
  if (!token) {
    redirect("/cart");
  }
  const transaction = await prisma.pendingTransaction.findUnique({
    where: { id: token },
  });

  if (!transaction) {
    redirect("/cart");
  }

  return (
    <div className="pt-20 container mx-auto py-8">
      <CheckoutForm amount={Number(transaction.amount)} />
    </div>
  );
}
