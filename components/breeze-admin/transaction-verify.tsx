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
      const supabase = createClient();
      const { data, error } = await supabase.storage
        .from("transaction-proofs")
        .download(transaction.proof);

      if (data) {
        const url = URL.createObjectURL(data);
        setImageUrl(url);
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
    if (imageUrl) {
      window.open(imageUrl, "_blank");
    }
  };

  const handleAccept = async () => {
    try {
      setIsAccepting(true);
      const response = await fetch("/api/breeze-admin/confirm", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          transactionId: transaction.token,
          status: "APPROVED",
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to approve transaction");
      }

      const data = await response.json();

      // Show email status notification
      if (data.emailSent) {
        toast.success("✓ Transaction Approved", {
          description: "Approval email sent to customer successfully",
        });
      } else {
        toast.error("⚠ Transaction Approved (Email Failed)", {
          description: `Approved but email could not be sent: ${
            data.emailError || "Unknown error"
          }`,
        });
      }

      // Refresh the page after a short delay
      setTimeout(() => window.location.reload(), 2000);
    } catch (error) {
      console.error("Error accepting transaction:", error);
      toast.error("Error", {
        description: "Failed to approve transaction",
      });
    } finally {
      setIsAccepting(false);
    }
  };

  const handleDeny = async () => {
    if (!rejectionReason.trim()) {
      toast.error("Rejection Reason Required", {
        description: "Please provide a reason for rejection",
      });
      return;
    }

    try {
      setIsDenying(true);
      const response = await fetch("/api/breeze-admin/confirm", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          transactionId: transaction.token,
          status: "REJECTED",
          rejectionReason: rejectionReason,
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to reject transaction");
      }

      const data = await response.json();

      // Show email status notification
      if (data.emailSent) {
        toast.success("✓ Transaction Rejected", {
          description: "Rejection email sent to customer successfully",
        });
      } else {
        toast.error("⚠ Transaction Rejected (Email Failed)", {
          description: `Rejected but email could not be sent: ${
            data.emailError || "Unknown error"
          }`,
        });
      }

      // Close dialog and refresh after short delay
      setShowRejectionDialog(false);
      setTimeout(() => window.location.reload(), 2000);
    } catch (error) {
      console.error("Error rejecting transaction:", error);
      toast.error("Error", {
        description: "Failed to reject transaction",
      });
    } finally {
      setIsDenying(false);
    }
  };

  if (transaction.proof && !imageUrl) {
    return (
      <div className="flex items-center justify-center p-8">Loading...</div>
    );
  }

  const cart = transaction.cart as unknown as CartItem;

  return (
    <div className="mt-4">
      <div className="flex flex-col md:flex-row gap-6">
        {/* Image Section */}
        {transaction.proof ? (
          <div className="flex-shrink-0">
            <div
              className="relative w-[250px] h-[250px] rounded-lg overflow-hidden border-2 border-gray-200 hover:border-blue-500 transition-all cursor-pointer"
              onClick={handleImageClick}
            >
              <Image
                src={imageUrl}
                alt="Transaction Proof"
                fill
                className="object-contain hover:scale-105 transition-transform duration-200"
              />
            </div>
            <p className="text-sm text-gray-500 text-center mt-2">
              Click to open in new tab
            </p>
          </div>
        ) : (
          <div className="flex items-center justify-center p-8">
            No Transaction Proof Available
          </div>
        )}

        {/* Details Section - adjust width to prevent overflow */}
        <div className="flex-grow max-w-[calc(100%-250px-1.5rem)] space-y-4">
          <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
            <h3 className="text-lg font-semibold text-gray-800 mb-3">
              Order Details
            </h3>
            <div className="mb-4 pb-3 border-b border-gray-200">
              <h4 className="text-sm font-medium text-gray-600 mb-2">
                Student Status
              </h4>
              <div className="text-gray-800">
                <p>{transaction.student_details || "No details provided"}</p>
              </div>
            </div>
            <div className="mb-4 pb-3 border-b border-gray-200">
              <h4 className="text-sm font-medium text-gray-600 mb-2">
                College Roll Number
              </h4>
              <div className="text-gray-800">
                <p>{transaction.address}</p>
              </div>
            </div>
            {transaction.accommodation &&
              transaction.accommodation.length > 0 && (
                <div className="mb-4 pb-3 border-b border-gray-200">
                  <h4 className="text-sm font-medium text-gray-600 mb-2">
                    Accommodation Details
                  </h4>
                  <div className="space-y-3">
                    <div className="flex flex-col space-y-2">
                      <span className="text-sm text-gray-700 font-medium">
                        Package Type:
                      </span>
                      <div className="flex flex-wrap gap-2">
                        {transaction.accommodation.map(
                          (day: accommodation_option, i) => (
                            <span
                              className="bg-gray-100 px-3 py-1 rounded-md text-gray-800"
                              key={i}
                            >
                              {day.toString().slice(0, 3) +
                                " " +
                                day.toString()[3]}
                            </span>
                          )
                        )}
                      </div>
                    </div>
                    <div className="flex justify-between items-center pt-2">
                      <span className="text-gray-700">Price</span>
                      <span className="font-medium text-green-600">
                        ₹{Number(transaction.accommodation_price)}
                      </span>
                    </div>
                  </div>
                </div>
              )}
            <ul className="space-y-3 divide-y divide-gray-200">
              {Object.entries(cart).map(([itemId, sizes]) => {
                const event = eventMap.get(itemId);
                const merch = merchMap.get(itemId);

                return (
                  <li key={itemId} className="pt-2">
                    {event && (
                      <div className="space-y-2">
                        <div className="font-medium text-gray-700">
                          {event.event_name}
                        </div>
                        <div className="ml-4 grid grid-cols-2 gap-2">
                          {Object.entries(sizes).map(([ticketType, quantity]) => {
                            const isPair = ticketType === "PAIR";
                            const price = isPair ? (event.event_pair_price || event.event_price) : event.event_price;
                            return (
                              <div
                                key={ticketType}
                                className="flex items-center justify-between bg-gray-100 px-3 py-1 rounded"
                              >
                                <span className="text-sm text-gray-600">
                                  {isPair ? "Pair" : "Single"}
                                </span>
                                <span className="font-medium text-gray-800">
                                  x{quantity}
                                </span>
                                <span className="font-medium text-green-600">
                                  ₹{price * quantity}
                                </span>
                              </div>
                            );
                          })}
                        </div>
                        <div className="flex justify-between text-sm text-gray-500">
                          <span>{event.event_org}</span>
                        </div>
                      </div>
                    )}
                    {merch && (
                      <div className="space-y-1">
                        <span className="font-medium text-gray-700">
                          {merch.product_name}
                        </span>
                        <div className="ml-4 grid grid-cols-2 gap-2">
                          {Object.entries(sizes).map(([size, quantity]) => (
                            <div
                              key={size}
                              className="flex items-center justify-between bg-gray-100 px-3 py-1 rounded"
                            >
                              <span className="text-sm text-gray-600">
                                Size {size}
                              </span>
                              <span className="font-medium text-gray-800">
                                {quantity}
                              </span>
                              <span className="font-medium text-green-600">
                                ₹{merch.product_price * quantity}
                              </span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </li>
                );
              })}
            </ul>
            <div className="mt-4 pt-3 border-t border-gray-200">
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Total Amount</span>
                <span className="text-xl font-bold text-green-600">
                  ₹{Number(transaction.amount)}
                </span>
              </div>
            </div>
          </div>

          {/* Show rejection details if viewing a rejected transaction */}
          {isRejected && (transaction as any).rejection_reason && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4">
              <div className="flex items-start gap-2">
                <AlertCircle
                  className="text-red-500 mt-1 flex-shrink-0"
                  size={20}
                />
                <div className="flex-grow">
                  <h4 className="font-semibold text-red-800 mb-1">
                    Rejection Reason
                  </h4>
                  <p className="text-red-700 text-sm">
                    {(transaction as any).rejection_reason}
                  </p>
                </div>
                {(transaction as any).email_sent && (
                  <div className="flex items-center gap-1 bg-green-100 text-green-700 px-2 py-1 rounded text-xs">
                    <Mail size={14} />
                    <span>Email Sent</span>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Action buttons for rejected transactions - allow re-approval */}
          {showActions && isRejected && (
            <div className="flex gap-4 justify-end pt-4">
              <Button
                disabled={isAccepting}
                onClick={handleAccept}
                className="bg-green-500 hover:bg-green-600 text-white gap-2"
              >
                <Check size={18} />
                {isAccepting ? "Processing..." : "Approve Now"}
              </Button>
            </div>
          )}

          {/* Action buttons for pending transactions */}
          {showActions && !isRejected && (
            <div className="flex gap-4 justify-end pt-4">
              <Button
                disabled={isAccepting || isDenying}
                onClick={handleAccept}
                className="bg-green-500 hover:bg-green-600 text-white gap-2"
              >
                <Check size={18} />
                {isAccepting ? "Processing..." : "Accept"}
              </Button>

              <Dialog
                open={showRejectionDialog}
                onOpenChange={setShowRejectionDialog}
              >
                <DialogTrigger asChild>
                  <Button
                    disabled={isAccepting || isDenying}
                    className="bg-red-500 hover:bg-red-600 text-white gap-2"
                  >
                    <X size={18} />
                    Reject
                  </Button>
                </DialogTrigger>
                <DialogContent className="sm:max-w-[500px] bg-white border border-gray-200 shadow-xl">
                  <DialogHeader className="pb-4 border-b border-gray-200">
                    <DialogTitle className="text-xl font-bold text-gray-900">
                      Reject Transaction
                    </DialogTitle>
                    <DialogDescription className="text-sm text-gray-600 mt-2">
                      Please provide a reason for rejecting this transaction.
                      The customer will be notified via email.
                    </DialogDescription>
                  </DialogHeader>
                  <div className="grid gap-4 py-4">
                    <div className="grid gap-2">
                      <Label
                        htmlFor="rejection-reason"
                        className="text-gray-700 font-medium"
                      >
                        Rejection Reason <span className="text-red-500">*</span>
                      </Label>
                      <Textarea
                        id="rejection-reason"
                        placeholder="e.g., Payment proof is unclear, incorrect amount, duplicate transaction..."
                        value={rejectionReason}
                        onChange={(e) => setRejectionReason(e.target.value)}
                        className="min-h-[100px] bg-white border-gray-300 text-gray-900 placeholder:text-gray-400 focus:border-red-500 focus:ring-red-500"
                      />
                    </div>
                    <div className="bg-amber-50 border border-amber-200 rounded-lg p-3 text-sm">
                      <p className="font-semibold text-amber-800 mb-1 flex items-center gap-2">
                        <Mail size={16} />
                        Email Notification
                      </p>
                      <p className="text-amber-700">
                        The customer will receive an email with your rejection
                        reason and instructions to contact support.
                      </p>
                    </div>
                  </div>
                  <DialogFooter className="pt-4 border-t border-gray-200 gap-2">
                    <DialogClose asChild>
                      <Button
                        variant="outline"
                        disabled={isDenying}
                        className="border-gray-300 text-gray-700 hover:bg-gray-100"
                      >
                        Cancel
                      </Button>
                    </DialogClose>
                    <Button
                      onClick={handleDeny}
                      disabled={isDenying || !rejectionReason.trim()}
                      className="bg-red-500 hover:bg-red-600 text-white font-semibold"
                    >
                      {isDenying ? "Rejecting..." : "Confirm Rejection"}
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
