"use client";

import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { SubmittedTransaction } from "@prisma/client";
import TransactionVerify from "@/components/breeze-admin/transaction-verify";

export default function ApprovedTable({
  transactions,
  eventMap,
  merchMap,
}: {
  transactions: SubmittedTransaction[];
  eventMap: Map<
    string,
    {
      created_at: Date;
      event_name: string;
      event_description: string;
      event_price: number;
      event_pair_price: number | null;
      event_org: string | null;
      event_venue: string | null;
      event_date: string | null;
    }
  >;
  merchMap: Map<
    string,
    {
      created_at: Date;
      product_name: string;
      product_price: number;
      product_description: string;
    }
  >;
}) {
  if (transactions.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-16">
        <p className="text-[13px]" style={{ color: '#555' }}>No approved transactions yet</p>
      </div>
    );
  }

  return (
    <div className="rounded-lg overflow-hidden" style={{ border: '1px solid #1e1e1e' }}>
      {/* Header */}
      <div className="grid grid-cols-[1fr_1.5fr_1.5fr_1fr_0.8fr] gap-3 px-4 py-2.5 text-[11px] font-medium uppercase tracking-wider" style={{ background: '#141414', color: '#555', borderBottom: '1px solid #1e1e1e' }}>
        <div>Time</div>
        <div>Name</div>
        <div>Email</div>
        <div>Phone</div>
        <div className="text-right">Amount</div>
      </div>

      {/* Rows */}
      {transactions.map((transaction, i) => (
        <Dialog key={i}>
          <DialogTrigger asChild>
            <div
              className="grid grid-cols-[1fr_1.5fr_1.5fr_1fr_0.8fr] gap-3 px-4 py-3 items-center cursor-pointer transition-colors duration-75"
              style={{ borderBottom: '1px solid #1a1a1a' }}
              onMouseEnter={(e) => { e.currentTarget.style.background = '#141414'; }}
              onMouseLeave={(e) => { e.currentTarget.style.background = 'transparent'; }}
            >
              <div className="text-[12px]" style={{ color: '#666' }}>
                {transaction.created_at.toLocaleString()}
              </div>
              <div className="text-[13px] font-medium truncate" style={{ color: '#e5e5e5' }}>
                {transaction.name}
              </div>
              <div className="text-[13px] truncate" style={{ color: '#888' }}>
                {transaction.email}
              </div>
              <div className="text-[13px]" style={{ color: '#888' }}>
                {transaction.phone}
              </div>
              <div className="text-[13px] font-medium text-right" style={{ color: '#34d399' }}>
                ₹{Number(transaction.amount).toLocaleString()}
              </div>
            </div>
          </DialogTrigger>

          <DialogContent className="max-w-4xl w-11/12 max-h-[90vh] overflow-y-auto p-0 gap-0" style={{ background: '#141414', border: '1px solid #1e1e1e', color: '#e5e5e5' }}>
            <DialogHeader className="px-6 py-4" style={{ borderBottom: '1px solid #1e1e1e' }}>
              <DialogTitle className="text-[15px] font-semibold" style={{ color: '#e5e5e5' }}>
                Approved Transaction
              </DialogTitle>
              <DialogDescription className="text-[12px] mt-1" style={{ color: '#666' }}>
                Transaction details and proof of payment
              </DialogDescription>
            </DialogHeader>
            <div className="p-6">
              <TransactionVerify
                merchMap={merchMap}
                eventMap={eventMap}
                transaction={transaction}
                showActions={false}
                isRejected={false}
              />
            </div>
          </DialogContent>
        </Dialog>
      ))}
    </div>
  );
}
