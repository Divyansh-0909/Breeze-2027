import { prisma } from "@/lib/prisma";
import TransactionTable from "../transaction-table";

export default async function ApprovedTransactionsPage() {
  const merchItemsArray = await prisma.merchItem.findMany();
  const eventItemsArray = await prisma.eventItem.findMany();

  const merchItems = new Map(
    merchItemsArray.map((item) => {
      const { id, ...rest } = item;
      return [id, rest];
    })
  );

  const eventItems = new Map(
    eventItemsArray.map((item) => {
      const { id, ...rest } = item;
      return [id, rest];
    })
  );

  const transactions = await prisma.submittedTransaction.findMany({
    where: { approved: true },
  });

  return (
    <TransactionTable
      transactions={transactions}
      eventMap={eventItems}
      merchMap={merchItems}
    />
  );
}

export const dynamic = "force-dynamic";
