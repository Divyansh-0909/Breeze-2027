import nodemailer from "nodemailer";
import path from "node:path";
import { prisma } from "@/lib/prisma";

const escape = (value: string) => value.replace(/[&<>"']/g, char => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[char]);

export async function deliverPaymentEmail(token: string, kind: string) {
  if (!process.env.EMAIL_HOST || process.env.EMAIL_HOST === "smtp.example.com" || !process.env.EMAIL_USERNAME) return { emailSent: false, emailError: "Email is not configured; confirmation is queued." };
  // Claim first: concurrent imports/retries cannot send the same queued email together.
  const claim = await prisma.paymentEmail.updateMany({ where: { token, kind, status: { in: ["PENDING", "FAILED"] } }, data: { status: "SENDING", attempts: { increment: 1 }, lastError: null } });
  if (!claim.count) {
    const email = await prisma.paymentEmail.findUnique({ where: { token_kind: { token, kind } } });
    return { emailSent: email?.status === "SENT", emailError: email?.status === "SENDING" ? "Email delivery is already in progress." : undefined };
  }
  try {
    if (!process.env.EMAIL_HOST || !process.env.EMAIL_USERNAME || !process.env.EMAIL_FROM) throw new Error("Email credentials have not been configured.");
    const transaction = await prisma.submittedTransaction.findUniqueOrThrow({ where: { token } });
    const baseUrl = process.env.NEXT_PUBLIC_APP_URL || "http://localhost:3000";
    const approved = kind === "APPROVED", rejected = kind === "REJECTED";
    const heading = approved ? "Registration confirmed" : rejected ? "Payment needs attention" : "Order saved — awaiting payment verification";
    const link = approved ? `${baseUrl}/reciept/${token}` : `${baseUrl}/checkout?token=${token}`;
    const transporter = nodemailer.createTransport({ host: process.env.EMAIL_HOST, port: Number(process.env.EMAIL_PORT || "587"), secure: process.env.EMAIL_SECURE === "true", connectionTimeout: 5000, greetingTimeout: 5000, socketTimeout: 10000, auth: { user: process.env.EMAIL_USERNAME, pass: process.env.EMAIL_PASSWORD } });
    await transporter.sendMail({
      from: { name: process.env.EMAIL_FROM_NAME || "Breeze 2027", address: process.env.EMAIL_FROM }, to: transaction.email,
      subject: `${heading} | Breeze 2027`,
      attachments: approved ? [{ filename: "Breeze-Code-of-Conduct.pdf", path: path.join(process.cwd(), "public", "BREEZE-2026-Code-of-Conduct.pdf") }] : [],
      html: `<h2>${heading}</h2><p>Hello ${escape(transaction.name)},</p><p>${approved ? "Your payment has been verified and your registration is confirmed." : rejected ? escape(transaction.rejection_reason || "Please contact the team about this payment.") : "Your details are saved. Confirmation will follow after your payment is matched to the receiving bank statement."}</p><p>Order reference: <strong>${escape(transaction.paymentReference || "Legacy order")}</strong><br>Amount: ₹${transaction.amount.toString()}</p><p><a href="${escape(link)}">${approved ? "View receipt" : "View your order"}</a></p>`,
    });
    await prisma.paymentEmail.update({ where: { token_kind: { token, kind } }, data: { status: "SENT" } });
    if (approved || rejected) await prisma.submittedTransaction.update({ where: { token }, data: { email_sent: true } });
    return { emailSent: true, emailError: undefined };
  } catch (error) {
    const message = error instanceof Error ? error.message.slice(0, 400) : "Email delivery failed.";
    await prisma.paymentEmail.update({ where: { token_kind: { token, kind } }, data: { status: "FAILED", lastError: message } });
    return { emailSent: false, emailError: "The order was saved, but email delivery failed. The team can retry it." };
  }
}

export async function drainPaymentEmails(limit = 20) {
  if (!process.env.EMAIL_HOST || process.env.EMAIL_HOST === "smtp.example.com" || !process.env.EMAIL_USERNAME) return { sent: 0, failed: 0, remaining: true, configured: false };
  const ready = { OR: [{ status: "PENDING" }, { status: "FAILED", attempts: { lt: 5 }, updatedAt: { lt: new Date(Date.now() - 300000) } }] };
  const emails = await prisma.paymentEmail.findMany({ where: ready, take: limit, orderBy: { updatedAt: "asc" } });
  let sent = 0, failed = 0;
  for (let index = 0; index < emails.length; index += 4) {
    const results = await Promise.all(emails.slice(index, index + 4).map(email => deliverPaymentEmail(email.token, email.kind)));
    results.forEach(result => { if (result.emailSent) sent++; else failed++; });
  }
  return { sent, failed, remaining: await prisma.paymentEmail.count({ where: { status: "PENDING" } }) > 0, configured: true };
}
