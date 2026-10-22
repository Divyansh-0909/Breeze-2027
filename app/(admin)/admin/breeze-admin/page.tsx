import { prisma } from "@/lib/prisma";
import TransactionTable from "./transaction-table";

export default async function Page() {
  try {
    const [merchItemsArray, eventItemsArray, pendingTransactions, rejectedTransactions] =
      await Promise.all([
        prisma.merchItem.findMany(),
        prisma.eventItem.findMany(),
        prisma.submittedTransaction.findMany({
          where: {
            approved: false,
            rejected: false,
          },
        }),
        prisma.submittedTransaction.findMany({
          where: { rejected: true },
          orderBy: { created_at: "desc" },
        }),
      ]);

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

    return (
      <div className="px-8 py-6 max-w-[1200px]">
        {/* Header */}
        <div className="mb-6">
          <h1 className="text-[18px] font-semibold tracking-[-0.02em]" style={{ color: '#e5e5e5' }}>
            Transactions
          </h1>
          <p className="text-[13px] mt-0.5" style={{ color: '#666' }}>
            Review and manage pending and rejected transactions
          </p>
        </div>

        {/* Stats */}
        <div className="flex items-center gap-6 mb-6 px-4 py-3 rounded-lg" style={{ background: '#141414', border: '1px solid #1e1e1e' }}>
          <div>
            <p className="text-[11px] font-medium uppercase tracking-wider" style={{ color: '#555' }}>Pending</p>
            <p className="text-[20px] font-semibold" style={{ color: '#fbbf24' }}>{pendingTransactions.length}</p>
          </div>
          <div className="w-px h-8" style={{ background: '#1e1e1e' }} />
          <div>
            <p className="text-[11px] font-medium uppercase tracking-wider" style={{ color: '#555' }}>Rejected</p>
            <p className="text-[20px] font-semibold" style={{ color: '#f87171' }}>{rejectedTransactions.length}</p>
          </div>
        </div>

        {/* Tabs */}
        <TransactionTable
          pendingTransactions={pendingTransactions}
          rejectedTransactions={rejectedTransactions}
          eventMap={eventItems}
          merchMap={merchItems}
        />
      </div>
    );
  } catch (error) {
    console.error("Error loading transactions:", error);
    return (
      <div className="px-8 py-16 max-w-[600px] mx-auto text-center">
        <div className="p-6 rounded-xl space-y-3" style={{ background: '#141414', border: '1px solid #262626' }}>
          <div className="w-10 h-10 rounded-full mx-auto flex items-center justify-center" style={{ background: '#1f1a1a', border: '1px solid #3b2828' }}>
            <span className="w-3 h-3 rounded-full bg-red-400" />
          </div>
          <h2 className="text-[16px] font-semibold" style={{ color: '#e5e5e5' }}>Database Connecting</h2>
          <p className="text-[13px]" style={{ color: '#888' }}>
            The database pooler is warming up. Please refresh the page in a few seconds.
          </p>
          <a
            href="/admin/breeze-admin"
            className="inline-block px-4 py-1.5 rounded-md text-[13px] font-medium transition-colors"
            style={{ background: '#e5e5e5', color: '#0a0a0a' }}
          >
            Retry Connection
          </a>
        </div>
      </div>
    );
  }
}

export const dynamic = "force-dynamic";
