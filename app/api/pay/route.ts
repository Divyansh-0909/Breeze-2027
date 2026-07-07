import { NextRequest, NextResponse } from "next/server";
import { createAdminClient } from "@/utils/supabase/admin";

import * as z from "zod";
import { prisma } from "@/lib/prisma";
import nodemailer from "nodemailer";

const paymentSchema = z.object({
  name: z.string().min(2),
  email: z.string().email(),
  phone: z.string().min(10),
  rollNumber: z.string().min(3),
  college_status: z.string().min(6, "Invalid student details"),
  amount: z.string().transform((val) => Number(val)),
  proofImage: z.instanceof(File).optional().nullable(),
  token: z.string().min(1, "Transaction token is required"),
});

// File validation constants
const MAX_FILE_SIZE = 5 * 1024 * 1024; // 5MB
const ALLOWED_FILE_TYPES = ["image/jpeg", "image/png", "image/webp", "image/jpg"];

export async function POST(req: NextRequest) {
  try {
    const supabase = createAdminClient();

    const formData = await req.formData();
    const data = {
      name: formData.get("name"),
      email: formData.get("email"),
      phone: formData.get("phone"),
      rollNumber: formData.get("rollNumber"),
      college_status: formData.get("college_status"),
      amount: formData.get("amount"),
      proofImage: formData.get("proofImage"),
      token: formData.get("token"),
    };
    const validatedData = paymentSchema.parse(data);

    let uploadData = null;

    if (validatedData.proofImage) {
      const file = validatedData.proofImage;

      // Validate file size
      if (file.size > MAX_FILE_SIZE) {
        return NextResponse.json(
          { success: false, error: "File too large. Maximum size is 5MB." },
          { status: 400 }
        );
      }

      // Validate file type
      if (!ALLOWED_FILE_TYPES.includes(file.type)) {
        return NextResponse.json(
          { success: false, error: "Invalid file type. Only JPEG, PNG, and WebP images are allowed." },
          { status: 400 }
        );
      }

      const { data: imageData, error: uploadError } = await supabase.storage
        .from("transaction-proofs")
        .upload(
          `${validatedData.email}-${Date.now()}`,
          file
        );

      if (uploadError) {
        throw new Error("Failed to upload image");
      }
      uploadData = imageData;
    }

    const cart = await prisma.pendingTransaction.findUnique({
      where: { id: validatedData.token },
    });

    if (!cart) {
      return NextResponse.json(
        { success: false, error: "Transaction token not found or already processed" },
        { status: 404 }
      );
    }

    await prisma.$transaction([
      prisma.submittedTransaction.create({
        data: {
          name: validatedData.name,
          email: validatedData.email,
          phone: validatedData.phone,
          address: validatedData.rollNumber, // Storing roll number in address field
          student_details: validatedData.college_status,
          amount: validatedData.amount,
          proof: uploadData?.path || null,
          token: validatedData.token,
          accommodation: cart.accommodation,
          cart: cart.cart,
          accommodation_price: cart.accommodation_price,
        },
      }),
      prisma.pendingTransaction.deleteMany({
        where: { id: validatedData.token },
      }),
    ]);

    // Send confirmation email to user
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
          to: validatedData.email,
          subject: "Registration Submitted - Pending Approval | Breeze 2026",
          html: `
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
              <h2 style="color: #2563eb;">Registration Submitted Successfully!</h2>
              <p>Dear ${validatedData.name},</p>
              <p>Thank you for submitting your registration for Breeze 2026. We have received your payment details and they are currently under review.</p>
              
              <div style="background-color: #dbeafe; border-left: 4px solid #2563eb; padding: 15px; margin: 20px 0;">
                <strong>⏳ Pending Approval</strong>
                <p style="margin: 5px 0 0 0;">Your registration is currently being reviewed by our team. You will receive another email once your payment has been verified and approved.</p>
              </div>
              
              <p><strong>Submission Details:</strong></p>
              <ul>
                <li>Transaction ID: ${validatedData.token}</li>
                <li>Amount: ₹${validatedData.amount}</li>
                <li>Submitted: ${new Date().toLocaleDateString('en-IN', {
            day: 'numeric',
            month: 'long',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
          })}</li>
              </ul>
              
              <div style="background-color: #fef3c7; border-left: 4px solid #f59e0b; padding: 15px; margin: 20px 0;">
                <strong>⏰ What's Next?</strong>
                <p style="margin: 5px 0 0 0;">Our team will review your payment proof within 24-48 hours. Once approved, you'll receive a confirmation email with your receipt and event details.</p>
              </div>
              
              <p>If you have any questions or concerns, please don't hesitate to contact us at:</p>
              <p><strong>${process.env.EMAIL_FROM}</strong></p>
              
              <p>Thank you for your patience!</p>
              
              <hr style="margin: 30px 0; border: none; border-top: 1px solid #e5e7eb;">
              <p style="color: #6b7280; font-size: 12px;">
                Breeze 2026 - Annual Cultural & Technical Festival<br>
                This is an automated confirmation email.
              </p>
            </div>
          `,
        });
      } catch (emailError) {
        console.error("Failed to send confirmation email:", emailError);
        // Don't fail the request if email fails
      }
    }

    return NextResponse.json(
      { message: "Payment submitted successfully" },
      { status: 200 }
    );
  } catch (error) {
    console.error("Payment API Error:", error);

    if (error instanceof z.ZodError) {
      return NextResponse.json(
        { success: false, errors: error.errors },
        { status: 400 }
      );
    }

    if (error instanceof Error) {
      return NextResponse.json(
        { success: false, error: error.message },
        { status: 500 }
      );
    }

    return NextResponse.json(
      { success: false, error: "Internal server error" },
      { status: 500 }
    );
  }
}
