import { prisma } from "@/lib/prisma";
import TransactionTable from "./transaction-table";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

export default async function Page() {
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

  const pendingTransactions = await prisma.submittedTransaction.findMany({
    where: {
      approved: false,
      rejected: false,
    },
  });

  const rejectedTransactions = await prisma.submittedTransaction.findMany({
    where: { rejected: true },
    orderBy: { created_at: "desc" },
  });

  return (
    <div className="min-h-screen bg-white">
      <div className="container mx-auto px-6 py-12">
        {/* Header */}
        <div className="mb-12">
          <h1 className="text-4xl font-bold text-[#202020] tracking-tight mb-2">
            Transaction Management
          </h1>
          <p className="text-gray-500 text-sm">
            Review and manage pending and rejected transactions
          </p>
        </div>

        {/* Tabs */}
        <Tabs defaultValue="pending" className="w-full">
          <TabsList className="bg-gray-100 border border-[#202020]/10 p-1 mb-8 rounded-lg">
            <TabsTrigger
              value="pending"
              className="data-[state=active]:bg-[#202020] data-[state=active]:text-white text-gray-600 rounded-md px-6 py-2.5 font-medium transition-all"
            >
              Pending
              <span className="ml-2 px-2 py-0.5 rounded-full bg-[#202020]/10 data-[state=active]:bg-white/20 text-xs">
                {pendingTransactions.length}
              </span>
            </TabsTrigger>
            <TabsTrigger
              value="rejected"
              className="data-[state=active]:bg-[#202020] data-[state=active]:text-white text-gray-600 rounded-md px-6 py-2.5 font-medium transition-all"
            >
              Rejected
              <span className="ml-2 px-2 py-0.5 rounded-full bg-[#202020]/10 data-[state=active]:bg-white/20 text-xs">
                {rejectedTransactions.length}
              </span>
            </TabsTrigger>
          </TabsList>

          <TabsContent value="pending" className="mt-0">
            <TransactionTable
              transactions={pendingTransactions}
              eventMap={eventItems}
              merchMap={merchItems}
              showActions={true}
            />
          </TabsContent>

          <TabsContent value="rejected" className="mt-0">
            <TransactionTable
              transactions={rejectedTransactions}
              eventMap={eventItems}
              merchMap={merchItems}
              showActions={false}
              isRejected={true}
            />
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}

export const dynamic = "force-dynamic";
