import { z } from "zod";

export const customerSchema = z.object({
  name: z.string().trim().min(2).max(100),
  email: z.string().trim().email().max(254).transform(value => value.toLowerCase()),
  phone: z.string().trim().regex(/^\+?[\d -]{10,24}$/, "Enter a valid phone number.").refine(value => { const digits = value.replace(/\D/g, "").length; return digits >= 10 && digits <= 15; }, "Enter a phone number containing 10–15 digits."),
  rollNumber: z.string().trim().min(3).max(80),
  college_status: z.string().trim().min(6).max(200),
});

export const accountSchema = z.object({
  label: z.string().trim().min(2).max(80),
  bankName: z.string().trim().min(2).max(80),
  accountLast4: z.string().regex(/^\d{4}$/, "Enter the last four account digits."),
  upiId: z.string().trim().regex(/^[\w.+-]{2,256}@[a-zA-Z][\w.-]{1,63}$/, "Enter a valid UPI ID."),
  payeeName: z.string().trim().min(2).max(80),
});
