"use client";

import {
  Table,
  TableBody,
  TableCaption,
  TableCell,
  TableFooter,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
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
import { SubmittedTransaction } from "@prisma/client";
import TransactionVerify from "@/components/breeze-admin/transaction-verify";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Check } from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";

export default function TransactionTable({
  transactions,
  eventMap,
  merchMap,
  showActions = true,
  isRejected = false,
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
  showActions?: boolean;
  isRejected?: boolean;
}) {
  const [approvingId, setApprovingId] = useState<string | null>(null);
  const [confirmApproveId, setConfirmApproveId] = useState<string | null>(null);

  const handleQuickApprove = async (transactionId: string) => {
    try {
      setApprovingId(transactionId);
      const response = await fetch("/api/breeze-admin/confirm", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          transactionId: transactionId,
          status: "APPROVED",
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to approve transaction");
      }

      const data = await response.json();

      if (data.emailSent) {
        toast.success("✓ Transaction Approved", {
          description: "Approval email sent successfully",
        });
      } else {
        toast.error("⚠ Approved (Email Failed)", {
          description: `Email could not be sent: ${
            data.emailError || "Unknown error"
          }`,
        });
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
    <Table className="w-11/12 lg:w-3/4 mx-auto mt-10 rounded-lg overflow-hidden border border-gray-200 shadow-lg">
      <TableCaption className="pb-4 text-gray-700 font-medium">
        {isRejected ? (
          <div className="space-y-1">
            <p className="text-lg">Rejected Transactions</p>
            <p className="text-sm text-gray-500">
              View details and rejection reasons
            </p>
          </div>
        ) : (
          <div className="space-y-1">
            <p className="text-lg">Pending Transactions</p>
            <p className="text-sm text-gray-500">
              Click any transaction to approve/reject
            </p>
          </div>
        )}
      </TableCaption>
      <TableHeader>
        <TableRow className="bg-gradient-to-r from-blue-50 to-indigo-50">
          <TableHead className="font-semibold text-gray-700">
            Submitted At
          </TableHead>
          <TableHead className="font-semibold text-gray-700">Name</TableHead>
          <TableHead className="font-semibold text-gray-700">Email</TableHead>
          <TableHead className="font-semibold text-gray-700">
            Phone Number
          </TableHead>
          <TableHead className="font-semibold text-gray-700">Roll Number</TableHead>
          <TableHead className="font-semibold text-gray-700">Amount</TableHead>
          {isRejected && (
            <>
              <TableHead className="font-semibold text-gray-700">
                Email Sent
              </TableHead>
              <TableHead className="font-semibold text-gray-700">
                Actions
              </TableHead>
            </>
          )}
        </TableRow>
      </TableHeader>
      <TableBody>
        {transactions.length === 0 ? (
          <TableRow>
            <TableCell
              colSpan={isRejected ? 8 : 6}
              className="text-center py-8 text-gray-500 italic"
            >
              {isRejected
                ? "No rejected transactions"
                : "No pending transactions"}
            </TableCell>
          </TableRow>
        ) : (
          transactions.map((transaction, i) => (
            <Dialog key={i}>
              <DialogTrigger asChild>
                <TableRow
                  className={`cursor-pointer transition-colors duration-200 ${
                    isRejected ? "hover:bg-red-50" : "hover:bg-blue-50"
                  }`}
                >
                  <TableCell className="font-medium">
                    {transaction.created_at.toLocaleString()}
                  </TableCell>
                  <TableCell>{transaction.name}</TableCell>
                  <TableCell className="text-blue-600">
                    {transaction.email}
                  </TableCell>
                  <TableCell>{transaction.phone}</TableCell>
                  <TableCell className="max-w-xs truncate">
                    {transaction.address}
                  </TableCell>
                  <TableCell className="font-semibold">
                    Rs. {Number(transaction.amount).toLocaleString()}
                  </TableCell>
                  {isRejected && (
                    <>
                      <TableCell>
                        {(transaction as any).email_sent ? (
                          <Badge variant="default" className="bg-green-500">
                            ✓ Sent
                          </Badge>
                        ) : (
                          <Badge variant="destructive">✗ Failed</Badge>
                        )}
                      </TableCell>
                      <TableCell>
                        <Button
                          size="sm"
                          disabled={approvingId === transaction.token}
                          onClick={(e) => {
                            e.stopPropagation();
                            setConfirmApproveId(transaction.token);
                          }}
                          className="bg-green-500 hover:bg-green-600 text-white gap-1"
                        >
                          <Check size={14} />
                          {approvingId === transaction.token
                            ? "Approving..."
                            : "Approve"}
                        </Button>
                        {/* Confirmation Dialog */}
                        {confirmApproveId === transaction.token && (
                          <Dialog
                            open
                            onOpenChange={(open) => {
                              if (!open) setConfirmApproveId(null);
                            }}
                          >
                            <DialogContent className="max-w-lg w-full bg-white border-[#202020]/10">
                              <DialogHeader className="pb-4 border-b border-[#202020]/10">
                                <DialogTitle className="text-3xl font-bold text-[#202020] tracking-tight">
                                  Confirm Approval
                                </DialogTitle>
                                <DialogDescription className="text-sm text-gray-500 mt-2">
                                  Are you sure you want to approve this
                                  transaction?
                                </DialogDescription>
                              </DialogHeader>
                              <div className="my-4 space-y-3 text-sm bg-gray-50 p-4 rounded-lg border border-[#202020]/10">
                                <div className="flex justify-between">
                                  <span className="font-semibold text-[#202020]">
                                    Name:
                                  </span>
                                  <span className="text-gray-700">
                                    {transaction.name}
                                  </span>
                                </div>
                                <div className="flex justify-between">
                                  <span className="font-semibold text-[#202020]">
                                    Email:
                                  </span>
                                  <span className="text-gray-700">
                                    {transaction.email}
                                  </span>
                                </div>
                                <div className="flex justify-between">
                                  <span className="font-semibold text-[#202020]">
                                    Phone:
                                  </span>
                                  <span className="text-gray-700">
                                    {transaction.phone}
                                  </span>
                                </div>
                                <div className="flex justify-between">
                                  <span className="font-semibold text-[#202020]">
                                    Amount:
                                  </span>
                                  <span className="text-gray-700 font-semibold">
                                    Rs.{" "}
                                    {Number(
                                      transaction.amount
                                    ).toLocaleString()}
                                  </span>
                                </div>
                                <div className="flex justify-between">
                                  <span className="font-semibold text-[#202020]">
                                    Submitted At:
                                  </span>
                                  <span className="text-gray-700">
                                    {transaction.created_at.toLocaleString()}
                                  </span>
                                </div>
                                <div className="flex flex-col gap-1">
                                  <span className="font-semibold text-[#202020]">
                                    Roll Number:
                                  </span>
                                  <span className="text-gray-700">
                                    {transaction.address}
                                  </span>
                                </div>
                                {(transaction as any).rejection_reason && (
                                  <div className="flex flex-col gap-1 pt-2 border-t border-[#202020]/10">
                                    <span className="font-semibold text-[#202020]">
                                      Rejection Reason:
                                    </span>
                                    <span className="text-gray-700">
                                      {(transaction as any).rejection_reason}
                                    </span>
                                  </div>
                                )}
                              </div>
                              <DialogFooter className="gap-3 pt-4 border-t border-[#202020]/10">
                                <Button
                                  variant="outline"
                                  onClick={() => setConfirmApproveId(null)}
                                  className="border-[#202020]/20 text-gray-600 hover:bg-gray-50"
                                >
                                  Cancel
                                </Button>
                                <Button
                                  className="bg-[#202020] hover:bg-[#303030] text-white font-semibold"
                                  onClick={() =>
                                    handleQuickApprove(transaction.token)
                                  }
                                  disabled={approvingId === transaction.token}
                                >
                                  {approvingId === transaction.token
                                    ? "Approving..."
                                    : "Yes, Approve"}
                                </Button>
                              </DialogFooter>
                            </DialogContent>
                          </Dialog>
                        )}
                      </TableCell>
                    </>
                  )}
                </TableRow>
              </DialogTrigger>
              <DialogContent className="max-w-4xl w-11/12 max-h-[90vh] overflow-y-auto bg-white border-[#202020]/10">
                <DialogHeader className="pb-4 border-b border-[#202020]/10">
                  <DialogTitle className="text-3xl font-bold text-[#202020] tracking-tight">
                    {isRejected
                      ? "Rejected Transaction Details"
                      : "Transaction Details"}
                  </DialogTitle>
                  <DialogDescription className="text-sm text-gray-500 mt-2">
                    Review the transaction details and proof of payment
                    {!isRejected && (
                      <>
                        <br />
                        <span className="text-gray-600">Receipt link: </span>
                        <a
                          href={`/reciept/${transaction.token}`}
                          className="text-[#202020] hover:underline font-medium"
                        >
                          https://breezesnu.com/reciept/{transaction.token}
                        </a>
                      </>
                    )}
                  </DialogDescription>
                </DialogHeader>
                <TransactionVerify
                  merchMap={merchMap}
                  eventMap={eventMap}
                  transaction={transaction}
                  showActions={showActions}
                  isRejected={isRejected}
                />
              </DialogContent>
            </Dialog>
          ))
        )}
      </TableBody>
    </Table>
  );
}
