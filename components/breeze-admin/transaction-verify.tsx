"use client";

import { SubmittedTransaction } from "@prisma/client";
import { createClient } from "@/utils/supabase/client";
import Image from "next/image";
import { useEffect, useState } from "react";
import { Button } from "../ui/button";
import { Check, X, Mail, AlertCircle } from "lucide-react";
import { accommodation_option } from "@prisma/client";
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { toast } from "sonner";

type CartItem = {
  [key: string]: {
    [sizeOrTicketType: string]: number;
  };
};

export default function TransactionVerify({
  transaction,
  eventMap,
  merchMap,
  showActions = true,
  isRejected = false,
}: {
  transaction: SubmittedTransaction;
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
  showActions?: boolean;
  isRejected?: boolean;
}) {
  const [imageUrl, setImageUrl] = useState<string | null>(null);
  const [isAccepting, setIsAccepting] = useState(false);
  const [isDenying, setIsDenying] = useState(false);
  const [rejectionReason, setRejectionReason] = useState("");
  const [showRejectionDialog, setShowRejectionDialog] = useState(false);

  useEffect(() => {
    async function loadImage() {
      if (!transaction.proof) return;
      try {
        const supabase = createClient();
        const { data, error } = await supabase.storage
          .from("transaction-proofs")
          .download(transaction.proof);

        if (data) {
          const url = URL.createObjectURL(data);
          setImageUrl(url);
        }
      } catch (err) {
        console.error("Error loading proof image:", err);
      }
    }

    loadImage();

    return () => {
      if (imageUrl) {
        URL.revokeObjectURL(imageUrl);
      }
    };
  }, [transaction.proof]);

  const handleImageClick = () => {
    if (imageUrl) window.open(imageUrl, "_blank");
  };

  const handleAccept = async () => {
    try {
      setIsAccepting(true);
      const response = await fetch("/api/breeze-admin/confirm", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ transactionId: transaction.token, status: "APPROVED" }),
      });

      if (!response.ok) throw new Error("Failed to approve transaction");

      const data = await response.json();
      if (data.emailSent) {
        toast.success("Transaction Approved", { description: "Approval email sent to customer successfully" });
      } else {
        toast.error("Approved (Email Failed)", { description: `Email error: ${data.emailError || "Unknown"}` });
      }
      setTimeout(() => window.location.reload(), 2000);
    } catch (error) {
      console.error("Error accepting transaction:", error);
      toast.error("Error", { description: "Failed to approve transaction" });
    } finally {
      setIsAccepting(false);
    }
  };

  const handleDeny = async () => {
    if (!rejectionReason.trim()) {
      toast.error("Rejection Reason Required", { description: "Please provide a reason for rejection" });
      return;
    }

    try {
      setIsDenying(true);
      const response = await fetch("/api/breeze-admin/confirm", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ transactionId: transaction.token, status: "REJECTED", rejectionReason }),
      });

      if (!response.ok) throw new Error("Failed to reject transaction");

      const data = await response.json();
      if (data.emailSent) {
        toast.success("Transaction Rejected", { description: "Rejection email sent to customer successfully" });
      } else {
        toast.error("Rejected (Email Failed)", { description: `Email error: ${data.emailError || "Unknown"}` });
      }
      setShowRejectionDialog(false);
      setTimeout(() => window.location.reload(), 2000);
    } catch (error) {
      console.error("Error rejecting transaction:", error);
      toast.error("Error", { description: "Failed to reject transaction" });
    } finally {
      setIsDenying(false);
    }
  };

  if (transaction.proof && !imageUrl) {
    return (
      <div className="flex items-center justify-center p-8">
        <p className="text-[13px]" style={{ color: '#555' }}>Loading proof…</p>
      </div>
    );
  }

  const cart = transaction.cart as unknown as CartItem;

  return (
    <div>
      <div className="flex flex-col md:flex-row gap-6">
        {/* Image Section */}
        {transaction.proof ? (
          <div className="flex-shrink-0">
            <div
              className="relative w-[220px] h-[220px] rounded-lg overflow-hidden cursor-pointer transition-all duration-150"
              style={{ border: '1px solid #262626' }}
              onClick={handleImageClick}
              onMouseEnter={(e) => { e.currentTarget.style.borderColor = '#444'; }}
              onMouseLeave={(e) => { e.currentTarget.style.borderColor = '#262626'; }}
            >
              <Image src={imageUrl} alt="Transaction Proof" fill className="object-contain" />
            </div>
            <p className="text-[11px] text-center mt-2" style={{ color: '#555' }}>Click to open full size</p>
          </div>
        ) : (
          <div className="flex items-center justify-center w-[220px] h-[220px] rounded-lg" style={{ background: '#111', border: '1px solid #1e1e1e' }}>
            <p className="text-[12px]" style={{ color: '#555' }}>No proof available</p>
          </div>
        )}

        {/* Details Section */}
        <div className="flex-grow min-w-0 space-y-4">
          {/* Info card */}
          <div className="rounded-lg p-4 space-y-3" style={{ background: '#111', border: '1px solid #1e1e1e' }}>
            <h3 className="text-[13px] font-semibold" style={{ color: '#e5e5e5' }}>Order Details</h3>

            {/* Student details */}
            <div className="pb-3" style={{ borderBottom: '1px solid #1a1a1a' }}>
              <p className="text-[11px] font-medium uppercase tracking-wider mb-1" style={{ color: '#555' }}>Student Status</p>
              <p className="text-[13px]" style={{ color: '#ccc' }}>{transaction.student_details || "No details provided"}</p>
            </div>

            <div className="pb-3" style={{ borderBottom: '1px solid #1a1a1a' }}>
              <p className="text-[11px] font-medium uppercase tracking-wider mb-1" style={{ color: '#555' }}>Roll Number</p>
              <p className="text-[13px]" style={{ color: '#ccc' }}>{transaction.address}</p>
            </div>

            {/* Accommodation */}
            {transaction.accommodation && transaction.accommodation.length > 0 && (
              <div className="pb-3" style={{ borderBottom: '1px solid #1a1a1a' }}>
                <p className="text-[11px] font-medium uppercase tracking-wider mb-2" style={{ color: '#555' }}>Accommodation</p>
                <div className="flex flex-wrap gap-1.5 mb-2">
                  {transaction.accommodation.map((day: accommodation_option, i) => (
                    <span key={i} className="text-[11px] px-2 py-0.5 rounded" style={{ background: '#1a1a1a', color: '#888', border: '1px solid #262626' }}>
                      {day.toString().slice(0, 3) + " " + day.toString()[3]}
                    </span>
                  ))}
                </div>
                <div className="flex justify-between">
                  <span className="text-[12px]" style={{ color: '#666' }}>Price</span>
                  <span className="text-[12px] font-medium" style={{ color: '#34d399' }}>₹{Number(transaction.accommodation_price)}</span>
                </div>
              </div>
            )}

            {/* Cart items */}
            <div className="space-y-3">
              {Object.entries(cart).map(([itemId, sizes]) => {
                const event = eventMap.get(itemId);
                const merch = merchMap.get(itemId);

                return (
                  <div key={itemId} className="pb-3" style={{ borderBottom: '1px solid #1a1a1a' }}>
                    {event && (
                      <div className="space-y-2">
                        <div className="flex items-center justify-between">
                          <span className="text-[13px] font-medium" style={{ color: '#e5e5e5' }}>{event.event_name}</span>
                          <span className="text-[11px]" style={{ color: '#555' }}>{event.event_org}</span>
                        </div>
                        <div className="space-y-1">
                          {Object.entries(sizes).map(([ticketType, quantity]) => {
                            const isPair = ticketType === "PAIR";
                            const price = isPair ? (event.event_pair_price || event.event_price) : event.event_price;
                            return (
                              <div key={ticketType} className="flex items-center justify-between px-2.5 py-1.5 rounded" style={{ background: '#0f0f0f' }}>
                                <span className="text-[12px]" style={{ color: '#888' }}>{isPair ? "Pair" : "Single"}</span>
                                <span className="text-[12px]" style={{ color: '#aaa' }}>×{quantity}</span>
                                <span className="text-[12px] font-medium" style={{ color: '#34d399' }}>₹{price * quantity}</span>
                              </div>
                            );
                          })}
                        </div>
                      </div>
                    )}
                    {merch && (
                      <div className="space-y-2">
                        <span className="text-[13px] font-medium" style={{ color: '#e5e5e5' }}>{merch.product_name}</span>
                        <div className="space-y-1">
                          {Object.entries(sizes).map(([size, quantity]) => (
                            <div key={size} className="flex items-center justify-between px-2.5 py-1.5 rounded" style={{ background: '#0f0f0f' }}>
                              <span className="text-[12px]" style={{ color: '#888' }}>Size {size}</span>
                              <span className="text-[12px]" style={{ color: '#aaa' }}>×{quantity}</span>
                              <span className="text-[12px] font-medium" style={{ color: '#34d399' }}>₹{merch.product_price * quantity}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>

            {/* Total */}
            <div className="flex justify-between items-center pt-2">
              <span className="text-[13px] font-medium" style={{ color: '#888' }}>Total Amount</span>
              <span className="text-[18px] font-semibold" style={{ color: '#34d399' }}>₹{Number(transaction.amount)}</span>
            </div>
          </div>

          {/* Rejection details */}
          {isRejected && (transaction as any).rejection_reason && (
            <div className="rounded-lg p-4" style={{ background: 'rgba(248,113,113,0.05)', border: '1px solid rgba(248,113,113,0.15)' }}>
              <div className="flex items-start gap-2.5">
                <AlertCircle className="mt-0.5 flex-shrink-0" size={15} style={{ color: '#f87171' }} />
                <div className="flex-grow min-w-0">
                  <h4 className="text-[12px] font-semibold mb-1" style={{ color: '#f87171' }}>Rejection Reason</h4>
                  <p className="text-[12px]" style={{ color: '#fca5a5' }}>{(transaction as any).rejection_reason}</p>
                </div>
                {(transaction as any).email_sent && (
                  <span className="flex items-center gap-1 px-2 py-0.5 rounded text-[10px] shrink-0" style={{ background: 'rgba(52,211,153,0.1)', color: '#34d399' }}>
                    <Mail size={10} /> Sent
                  </span>
                )}
              </div>
            </div>
          )}

          {/* Action buttons for rejected transactions */}
          {showActions && isRejected && (
            <div className="flex gap-3 justify-end pt-2">
              <button
                disabled={isAccepting}
                onClick={handleAccept}
                className="flex items-center gap-1.5 px-4 py-[7px] rounded-md text-[13px] font-medium transition-colors duration-100 cursor-pointer"
                style={{ background: 'rgba(52,211,153,0.1)', color: '#34d399', border: '1px solid rgba(52,211,153,0.2)' }}
              >
                <Check size={14} />
                {isAccepting ? "Processing…" : "Approve Now"}
              </button>
            </div>
          )}

          {/* Action buttons for pending transactions */}
          {showActions && !isRejected && (
            <div className="flex gap-3 justify-end pt-2">
              <button
                disabled={isAccepting || isDenying}
                onClick={handleAccept}
                className="flex items-center gap-1.5 px-4 py-[7px] rounded-md text-[13px] font-medium transition-colors duration-100 cursor-pointer"
                style={{ background: 'rgba(52,211,153,0.1)', color: '#34d399', border: '1px solid rgba(52,211,153,0.2)' }}
              >
                <Check size={14} />
                {isAccepting ? "Processing…" : "Accept"}
              </button>

              <Dialog open={showRejectionDialog} onOpenChange={setShowRejectionDialog}>
                <DialogTrigger asChild>
                  <button
                    disabled={isAccepting || isDenying}
                    className="flex items-center gap-1.5 px-4 py-[7px] rounded-md text-[13px] font-medium transition-colors duration-100 cursor-pointer"
                    style={{ background: 'rgba(248,113,113,0.1)', color: '#f87171', border: '1px solid rgba(248,113,113,0.2)' }}
                  >
                    <X size={14} />
                    Reject
                  </button>
                </DialogTrigger>
                <DialogContent className="max-w-[440px] p-0 gap-0" style={{ background: '#141414', border: '1px solid #1e1e1e', color: '#e5e5e5' }}>
                  <DialogHeader className="px-5 py-4" style={{ borderBottom: '1px solid #1e1e1e' }}>
                    <DialogTitle className="text-[15px] font-semibold" style={{ color: '#e5e5e5' }}>Reject Transaction</DialogTitle>
                    <DialogDescription className="text-[12px] mt-1" style={{ color: '#666' }}>
                      Provide a reason for rejection. The customer will be notified via email.
                    </DialogDescription>
                  </DialogHeader>
                  <div className="p-5 space-y-4">
                    <div className="space-y-1.5">
                      <Label className="text-[12px] font-medium" style={{ color: '#888' }} htmlFor="rejection-reason">
                        Reason <span style={{ color: '#f87171' }}>*</span>
                      </Label>
                      <Textarea
                        id="rejection-reason"
                        placeholder="e.g., Payment proof is unclear, incorrect amount..."
                        value={rejectionReason}
                        onChange={(e) => setRejectionReason(e.target.value)}
                        className="min-h-[80px] text-[13px] rounded-md resize-none"
                        style={{ background: '#0a0a0a', border: '1px solid #262626', color: '#e5e5e5' }}
                      />
                    </div>
                    <div className="rounded-md p-3 flex items-start gap-2" style={{ background: 'rgba(251,191,36,0.05)', border: '1px solid rgba(251,191,36,0.15)' }}>
                      <Mail size={13} className="mt-0.5 shrink-0" style={{ color: '#fbbf24' }} />
                      <p className="text-[11px] leading-relaxed" style={{ color: '#fbbf24' }}>
                        The customer will receive an email with your rejection reason and instructions to contact support.
                      </p>
                    </div>
                  </div>
                  <DialogFooter className="px-5 py-3 gap-2" style={{ borderTop: '1px solid #1e1e1e' }}>
                    <DialogClose asChild>
                      <Button disabled={isDenying} className="h-8 text-[13px] font-medium rounded-md cursor-pointer" style={{ background: 'transparent', border: '1px solid #262626', color: '#888' }}>Cancel</Button>
                    </DialogClose>
                    <Button
                      onClick={handleDeny}
                      disabled={isDenying || !rejectionReason.trim()}
                      className="h-8 text-[13px] font-medium rounded-md cursor-pointer"
                      style={{ background: 'rgba(239,68,68,0.9)', color: '#fff', opacity: (isDenying || !rejectionReason.trim()) ? 0.5 : 1 }}
                    >
                      {isDenying ? "Rejecting…" : "Confirm Rejection"}
                    </Button>
                  </DialogFooter>
                </DialogContent>
              </Dialog>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
