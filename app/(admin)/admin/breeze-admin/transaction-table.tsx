"use client";

import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { SubmittedTransaction } from "@prisma/client";
import TransactionVerify from "@/components/breeze-admin/transaction-verify";
import { Button } from "@/components/ui/button";
import { Check } from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";

export default function TransactionTable({
  pendingTransactions,
  rejectedTransactions,
  eventMap,
  merchMap,
}: {
  pendingTransactions: SubmittedTransaction[];
  rejectedTransactions: SubmittedTransaction[];
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
  const [activeTab, setActiveTab] = useState<"pending" | "rejected">("pending");
  const [approvingId, setApprovingId] = useState<string | null>(null);
  const [confirmApproveId, setConfirmApproveId] = useState<string | null>(null);

  const transactions = activeTab === "pending" ? pendingTransactions : rejectedTransactions;
  const showActions = activeTab === "pending";
  const isRejected = activeTab === "rejected";

  const handleQuickApprove = async (transactionId: string) => {
    try {
      setApprovingId(transactionId);
      const response = await fetch("/api/breeze-admin/confirm", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ transactionId, status: "APPROVED" }),
      });

      if (!response.ok) throw new Error("Failed to approve transaction");

      const data = await response.json();
      if (data.emailSent) {
        toast.success("Transaction Approved", { description: "Approval email sent successfully" });
      } else {
        toast.error("Approved (Email Failed)", { description: `Email error: ${data.emailError || "Unknown"}` });
      }
      setTimeout(() => window.location.reload(), 1500);
    } catch (error) {
      console.error("Error approving transaction:", error);
      toast.error("Failed to approve transaction");
      setApprovingId(null);
    }
    setConfirmApproveId(null);
  };

  return (
    <div>
      {/* Tab switcher */}
      <div className="flex items-center gap-1 mb-4 p-0.5 rounded-lg w-fit" style={{ background: '#141414', border: '1px solid #1e1e1e' }}>
        <button
          onClick={() => setActiveTab("pending")}
          className="flex items-center gap-2 px-4 py-1.5 rounded-md text-[13px] font-medium transition-all duration-100 cursor-pointer"
          style={{
            background: activeTab === "pending" ? '#1e1e1e' : 'transparent',
            color: activeTab === "pending" ? '#e5e5e5' : '#666',
          }}
        >
          Pending
          <span className="text-[11px] px-1.5 py-0.5 rounded-full" style={{
            background: activeTab === "pending" ? '#333' : '#1a1a1a',
            color: activeTab === "pending" ? '#fbbf24' : '#555',
          }}>
            {pendingTransactions.length}
          </span>
        </button>
        <button
          onClick={() => setActiveTab("rejected")}
          className="flex items-center gap-2 px-4 py-1.5 rounded-md text-[13px] font-medium transition-all duration-100 cursor-pointer"
          style={{
            background: activeTab === "rejected" ? '#1e1e1e' : 'transparent',
            color: activeTab === "rejected" ? '#e5e5e5' : '#666',
          }}
        >
          Rejected
          <span className="text-[11px] px-1.5 py-0.5 rounded-full" style={{
            background: activeTab === "rejected" ? '#333' : '#1a1a1a',
            color: activeTab === "rejected" ? '#f87171' : '#555',
          }}>
            {rejectedTransactions.length}
          </span>
        </button>
      </div>

      {/* Transaction list */}
      {transactions.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-16">
          <p className="text-[13px]" style={{ color: '#555' }}>
            {isRejected ? "No rejected transactions" : "No pending transactions"}
          </p>
        </div>
      ) : (
        <div className="rounded-lg overflow-hidden" style={{ border: '1px solid #1e1e1e' }}>
          {/* Header */}
          <div className={`grid gap-3 px-4 py-2.5 text-[11px] font-medium uppercase tracking-wider ${isRejected ? 'grid-cols-[1fr_1.5fr_1.5fr_1fr_0.8fr_80px_80px]' : 'grid-cols-[1fr_1.5fr_1.5fr_1fr_0.8fr]'}`} style={{ background: '#141414', color: '#555', borderBottom: '1px solid #1e1e1e' }}>
            <div>Time</div>
            <div>Name</div>
            <div>Email</div>
            <div>Roll No.</div>
            <div className="text-right">Amount</div>
            {isRejected && <div>Email</div>}
            {isRejected && <div>Actions</div>}
          </div>

          {/* Rows */}
          {transactions.map((transaction, i) => (
            <Dialog key={i}>
              <DialogTrigger asChild>
                <div
                  className={`grid gap-3 px-4 py-3 items-center cursor-pointer transition-colors duration-75 ${isRejected ? 'grid-cols-[1fr_1.5fr_1.5fr_1fr_0.8fr_80px_80px]' : 'grid-cols-[1fr_1.5fr_1.5fr_1fr_0.8fr]'}`}
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
                  <div className="text-[13px] truncate" style={{ color: '#888' }}>
                    {transaction.address}
                  </div>
                  <div className="text-[13px] font-medium text-right" style={{ color: '#e5e5e5' }}>
                    ₹{Number(transaction.amount).toLocaleString()}
                  </div>
                  {isRejected && (
                    <div>
                      <span className="text-[11px] px-2 py-0.5 rounded-full font-medium" style={{
                        background: (transaction as any).email_sent ? 'rgba(52,211,153,0.1)' : 'rgba(248,113,113,0.1)',
                        color: (transaction as any).email_sent ? '#34d399' : '#f87171',
                        border: `1px solid ${(transaction as any).email_sent ? 'rgba(52,211,153,0.2)' : 'rgba(248,113,113,0.2)'}`,
                      }}>
                        {(transaction as any).email_sent ? "Sent" : "Failed"}
                      </span>
                    </div>
                  )}
                  {isRejected && (
                    <div onClick={(e) => e.stopPropagation()}>
                      <button
                        disabled={approvingId === transaction.token}
                        onClick={(e) => {
                          e.stopPropagation();
                          setConfirmApproveId(transaction.token);
                        }}
                        className="flex items-center gap-1 px-2 py-1 rounded text-[11px] font-medium transition-colors duration-100 cursor-pointer"
                        style={{ background: 'rgba(52,211,153,0.1)', color: '#34d399', border: '1px solid rgba(52,211,153,0.2)' }}
                      >
                        <Check size={12} />
                        {approvingId === transaction.token ? "…" : "Approve"}
                      </button>

                      {/* Confirm dialog */}
                      {confirmApproveId === transaction.token && (
                        <Dialog open onOpenChange={(open) => { if (!open) setConfirmApproveId(null); }}>
                          <DialogContent className="max-w-[440px] p-0 gap-0" style={{ background: '#141414', border: '1px solid #1e1e1e', color: '#e5e5e5' }}>
                            <DialogHeader className="px-5 py-4" style={{ borderBottom: '1px solid #1e1e1e' }}>
                              <DialogTitle className="text-[15px] font-semibold" style={{ color: '#e5e5e5' }}>Confirm Approval</DialogTitle>
                              <DialogDescription className="text-[12px] mt-1" style={{ color: '#666' }}>
                                Approve this transaction and send confirmation email?
                              </DialogDescription>
                            </DialogHeader>
                            <div className="p-5 space-y-2">
                              {[
                                ["Name", transaction.name],
                                ["Email", transaction.email],
                                ["Amount", `₹${Number(transaction.amount).toLocaleString()}`],
                                ["Roll No.", transaction.address],
                              ].map(([label, value]) => (
                                <div key={label} className="flex justify-between text-[13px]">
                                  <span style={{ color: '#666' }}>{label}</span>
                                  <span style={{ color: '#e5e5e5' }}>{value}</span>
                                </div>
                              ))}
                            </div>
                            <DialogFooter className="px-5 py-3 gap-2" style={{ borderTop: '1px solid #1e1e1e' }}>
                              <Button onClick={() => setConfirmApproveId(null)} className="h-8 text-[13px] font-medium rounded-md cursor-pointer" style={{ background: 'transparent', border: '1px solid #262626', color: '#888' }}>
                                Cancel
                              </Button>
                              <Button onClick={() => handleQuickApprove(transaction.token)} disabled={approvingId === transaction.token} className="h-8 text-[13px] font-medium rounded-md cursor-pointer" style={{ background: '#e5e5e5', color: '#0a0a0a' }}>
                                {approvingId === transaction.token ? "Approving…" : "Approve"}
                              </Button>
                            </DialogFooter>
                          </DialogContent>
                        </Dialog>
                      )}
                    </div>
                  )}
                </div>
              </DialogTrigger>

              {/* Transaction detail dialog */}
              <DialogContent className="max-w-4xl w-11/12 max-h-[90vh] overflow-y-auto p-0 gap-0" style={{ background: '#141414', border: '1px solid #1e1e1e', color: '#e5e5e5' }}>
                <DialogHeader className="px-6 py-4" style={{ borderBottom: '1px solid #1e1e1e' }}>
                  <DialogTitle className="text-[15px] font-semibold" style={{ color: '#e5e5e5' }}>
                    {isRejected ? "Rejected Transaction" : "Transaction Details"}
                  </DialogTitle>
                  <DialogDescription className="text-[12px] mt-1" style={{ color: '#666' }}>
                    Review the transaction details and proof of payment
                    {!isRejected && (
                      <>
                        <br />
                        <span style={{ color: '#555' }}>Receipt: </span>
                        <a href={`/reciept/${transaction.token}`} className="hover:underline" style={{ color: '#888' }}>
                          breezesnu.com/reciept/{transaction.token}
                        </a>
                      </>
                    )}
                  </DialogDescription>
                </DialogHeader>
                <div className="p-6">
                  <TransactionVerify
                    merchMap={merchMap}
                    eventMap={eventMap}
                    transaction={transaction}
                    showActions={showActions}
                    isRejected={isRejected}
                  />
                </div>
              </DialogContent>
            </Dialog>
          ))}
        </div>
      )}
    </div>
  );
}
