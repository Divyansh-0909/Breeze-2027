import { prisma } from "@/lib/prisma";
import { Prisma } from "@prisma/client";
import { NextRequest, NextResponse } from "next/server";
import nodemailer from "nodemailer";
import path from "path";
import { requireBreezeAdmin } from "@/lib/auth";

interface ConfirmRequestBody {
  transactionId: string;
  status: "APPROVED" | "REJECTED";
  rejectionReason?: string;
}

type CartItem = {
  [key: string]: {
    [size: string]: number;
  };
};

export async function POST(req: NextRequest) {
  // Verify BREEZE admin access
  const adminCheck = await requireBreezeAdmin();
  if (adminCheck.authorized === false) return adminCheck.response;

  try {
    const body: ConfirmRequestBody = await req.json();

    const transaction = await prisma.submittedTransaction.findUnique({
      where: { token: body.transactionId },
    });

    if (!transaction) {
      return NextResponse.json(
        { message: "Transaction not found", emailSent: false },
        { status: 404 }
      );
    }

    let emailSent = false;
    let emailError = null;

    // Handle re-approval of rejected transactions
    if (body.status === "APPROVED" && (transaction as any).rejected) {
      // Clear rejection status
      await prisma.submittedTransaction.update({
        where: { token: body.transactionId },
        data: {
          rejected: false,
          rejection_reason: null,
          approved: false, // Will be set to true below
          email_sent: false, // Reset email flag
        },
      });
    }

    if (body.status === "REJECTED") {
      // Update transaction as rejected instead of deleting
      await prisma.submittedTransaction.update({
        where: { token: body.transactionId },
        data: {
          rejected: true,
          rejection_reason: body.rejectionReason || "No reason provided",
          approved: false,
        },
      });

      // Send rejection email
      if (process.env.EMAIL_HOST && process.env.EMAIL_USERNAME) {
        try {
          const transporter = nodemailer.createTransport({
            host: process.env.EMAIL_HOST,
            port: parseInt(process.env.EMAIL_PORT || "587"),
            secure: process.env.EMAIL_SECURE === "true",
            auth: {
              user: process.env.EMAIL_USERNAME,
              pass: process.env.EMAIL_PASSWORD,
            },
          });

          await transporter.sendMail({
            from: `"${process.env.EMAIL_FROM_NAME || "Breeze 2026"}" <${process.env.EMAIL_FROM}>`,
            to: transaction.email,
            subject: "Payment Rejected - Breeze 2026",
            html: `
              <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <h2 style="color: #dc2626;">Payment Request Rejected</h2>
                <p>Dear ${transaction.name},</p>
                <p>Your payment request for Breeze 2026 has been rejected.</p>
                
                <div style="background-color: #fee2e2; border-left: 4px solid #dc2626; padding: 15px; margin: 20px 0;">
                  <strong>Rejection Reason:</strong>
                  <p style="margin: 5px 0 0 0;">${body.rejectionReason || "No specific reason provided"}</p>
                </div>
                
                <p><strong>Transaction Details:</strong></p>
                <ul>
                  <li>Transaction ID: ${transaction.token}</li>
                  <li>Amount: ₹${transaction.amount}</li>
                  <li>Date: ${new Date(transaction.created_at).toLocaleDateString()}</li>
                </ul>
                
                <p>If you have any questions or believe this rejection was made in error, please reply to this email or contact us at:</p>
                <p><strong>${process.env.EMAIL_FROM}</strong></p>
                
                <p>We will review your query and get back to you within 24-48 hours.</p>
                
                <hr style="margin: 30px 0; border: none; border-top: 1px solid #e5e7eb;">
                <p style="color: #6b7280; font-size: 12px;">
                  Breeze 2026 - Annual Cultural & Technical Festival<br>
                  This is an automated email. Please do not reply directly to this message.
                </p>
              </div>
            `,
          });
          emailSent = true;

          // Update email_sent flag
          await prisma.submittedTransaction.update({
            where: { token: body.transactionId },
            data: { email_sent: true },
          });
        } catch (error) {
          console.error("Email sending failed:", error);
          emailError = error.message;
        }
      }

      return NextResponse.json(
        {
          message: "Transaction rejected successfully",
          emailSent,
          emailError: emailError || undefined,
        },
        { status: 200 }
      );
    }

    // APPROVAL PROCESS
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

    // Create confirmed events/merch and update transaction
    await prisma.$transaction(async (tx: Prisma.TransactionClient) => {
      await tx.submittedTransaction.update({
        where: { token: transaction.token },
        data: { approved: true, rejected: false },
      });
      await Promise.all(
        Object.entries(transaction.cart as unknown as CartItem).flatMap(
          ([id, sizes]) =>
            Object.entries(sizes).map(([size, quantity]) => {
              if (merchItems.has(id)) {
                return tx.confirmedMerch.create({
                  data: {
                    id: id,
                    size: size,
                    quantity: quantity,
                    token: transaction.token,
                  },
                });
              } else if (eventItems.has(id)) {
                return tx.confirmedEvent.create({
                  data: {
                    id: id,
                    quantity: quantity,
                    token: transaction.token,
                  },
                });
              }
              return Promise.resolve();
            })
        )
      );
    });

    // Send approval email with receipt
    if (process.env.EMAIL_HOST && process.env.EMAIL_USERNAME) {
      try {
        const transporter = nodemailer.createTransport({
          host: process.env.EMAIL_HOST,
          port: parseInt(process.env.EMAIL_PORT || "587"),
          secure: process.env.EMAIL_SECURE === "true",
          auth: {
            user: process.env.EMAIL_USERNAME,
            pass: process.env.EMAIL_PASSWORD,
          },
        });

        const receiptUrl = `${process.env.NEXT_PUBLIC_APP_URL || "http://localhost:3000"}/reciept/${transaction.token}`;
        const pdfPath = path.join(process.cwd(), "public", "BREEZE-2026-Code-of-Conduct.pdf");

        await transporter.sendMail({
          attachments: [
            {
              filename: "Breeze-2026-Code-of-Conduct.pdf",
              path: pdfPath,
            },
          ],
          from: `"${process.env.EMAIL_FROM_NAME || "Breeze 2026"}" <${process.env.EMAIL_FROM}>`,
          to: transaction.email,
          subject: "Payment Approved - Breeze 2026 Registration Confirmed! 🎉",
          html: `
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
              <h2 style="color: #16a34a;">Payment Approved!</h2>
              <p>Dear ${transaction.name},</p>
              <p>Congratulations! Your payment for Breeze 2026 has been approved and your registration is confirmed.</p>
              
              <div style="background-color: #dcfce7; border-left: 4px solid #16a34a; padding: 15px; margin: 20px 0;">
                <strong>✓ Registration Confirmed</strong>
                <p style="margin: 5px 0 0 0;">You're all set for Breeze 2026!</p>
              </div>
              
              <p><strong>Transaction Details:</strong></p>
              <ul>
                <li>Transaction ID: ${transaction.token}</li>
                <li>Amount Paid: ₹${transaction.amount}</li>
                <li>Date: ${new Date(transaction.created_at).toLocaleDateString()}</li>
              </ul>
              
              <div style="text-align: center; margin: 30px 0;">
                <a href="${receiptUrl}" 
                   style="background-color: #f97316; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block; font-weight: bold;">
                  View Your Receipt
                </a>
              </div>
              
              <p>Please keep this email for your records. You can access your receipt at any time using the link above.</p>
              
              <p>We look forward to seeing you at Breeze 2026!</p>
              
              <hr style="margin: 30px 0; border: none; border-top: 1px solid #e5e7eb;">
              <p style="color: #6b7280; font-size: 12px;">
                Breeze 2026 - Annual Cultural & Technical Festival<br>
                For any queries, contact us at ${process.env.EMAIL_FROM}
              </p>
            </div>
          `,
        });
        emailSent = true;

        // Update email_sent flag
        await prisma.submittedTransaction.update({
          where: { token: body.transactionId },
          data: { email_sent: true },
        });
      } catch (error) {
        console.error("Email sending failed:", error);
        emailError = error.message;
      }
    }

    return NextResponse.json(
      {
        message: "Transaction approved successfully",
        emailSent,
        emailError: emailError || undefined,
      },
      { status: 200 }
    );
  } catch (e) {
    console.error(e);
    return NextResponse.json({ error: e.message, emailSent: false }, { status: 500 });
  }
}
