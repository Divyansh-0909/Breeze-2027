"use client";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { useRouter } from "next/navigation";
import * as z from "zod";
import { Button } from "@/components/ui/button";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { useSearchParams } from "next/navigation";
import { useState } from "react";
import Image from "next/image";

const MAX_FILE_SIZE = 1 * 1024 * 1024; // 1MB in bytes
const ACCEPTED_IMAGE_TYPES = [
  "image/jpeg",
  "image/jpg",
  "image/png",
  "image/webp",
];

const formSchema = z.object({
  name: z.string().min(2, "Name must be at least 2 characters"),
  email: z.string().email("Invalid email address"),
  phone: z.string().min(10, "Phone number must be at least 10 digits"),
  rollNumber: z.string().min(3, "Roll number must be at least 3 characters"),
  college_status: z.string().min(6, "Invalid student details"),
  proofImage: z
    .instanceof(File, {
      message: "Please upload proof of transaction",
    })
    .refine((file) => file.size <= MAX_FILE_SIZE, `Max file size is 1MB.`)
    .nullable()
    .optional(),
});

interface CheckoutFormProps {
  amount: number;
}

export function CheckoutForm({ amount }: CheckoutFormProps) {
  const searchParams = useSearchParams();
  const token = searchParams.get("token");
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      name: "",
      email: "",
      phone: "",
      rollNumber: "",
      college_status: "",
      proofImage: null,
    },
  });

  const handleSubmit = async (values: z.infer<typeof formSchema>) => {
    try {
      setIsLoading(true);
      const formData = new FormData();
      formData.append("name", values.name);
      formData.append("email", values.email);
      formData.append("phone", values.phone);
      formData.append("rollNumber", values.rollNumber);
      formData.append("college_status", values.college_status);
      formData.append("amount", amount.toString());
      if (values.proofImage) {
        formData.append("proofImage", values.proofImage);
      }
      if (token) {
        formData.append("token", token);
      }

      const response = await fetch("/api/pay", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error("Payment submission failed");
      } else {
        localStorage.removeItem("cart");
        router.push("/thank-you");
      }
    } catch (error) {
      console.error("Payment error:", error);
      // You might want to show an error message to the user here
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="max-w-md mx-auto p-6">
      <div className="mb-6 text-center  ">
        <h2 className="text-2xl font-bold">Checkout</h2>
        <p className="text-xl font-semibold text-green-600">
          Amount to pay: Rs.{amount.toFixed(2)}
        </p>
        <div className="text-center">
          <Image
            src={"/qr-aparna.jpeg"}
            width={300}
            height={300}
            alt="UPI Payment QR"
            className="mx-auto mb-2"
          />
          <p className="text-sm text-muted-foreground mb-4">
            Scan QR code to pay
          </p>
        </div>
        <Form {...form}>
          <form
            onSubmit={form.handleSubmit(handleSubmit)}
            className="space-y-6"
          >
            <FormField
              control={form.control}
              name="name"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Full Name</FormLabel>
                  <FormControl>
                    <Input placeholder="John Doe" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="email"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Email</FormLabel>
                  <FormControl>
                    <Input placeholder="john@example.com" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="phone"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Phone</FormLabel>
                  <FormControl>
                    <Input placeholder="1234567890" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="rollNumber"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>College Roll Number</FormLabel>
                  <FormControl>
                    <Input placeholder="e.g., 2024UCS1234" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="college_status"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>
                    Current College and Year of Graduation:{" "}
                  </FormLabel>
                  <FormControl>
                    <Input
                      placeholder="Example: Shiv Nadar University, 2027"
                      {...field}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="proofImage"
              render={({ field: { onChange, value, ...field } }) => (
                <FormItem>
                  <FormLabel>
                    Proof of Transaction, if Applicable (Max 1MB)
                  </FormLabel>
                  <FormControl>
                    <Input
                      type="file"
                      accept="image/*"
                      onChange={(e) => {
                        const file = e.target.files?.[0];
                        if (file) {
                          if (file.size > MAX_FILE_SIZE) {
                            form.setError("proofImage", {
                              message: "File size must be less than 1MB",
                            });
                            e.target.value = "";
                            return;
                          }
                          onChange(file);
                        }
                      }}
                      {...field}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <Button type="submit" className="w-full" disabled={isLoading}>
              {isLoading ? (
                <>
                  <svg
                    className="animate-spin -ml-1 mr-3 h-5 w-5 "
                    xmlns="http://www.w3.org/2000/svg"
                    fill="none"
                    viewBox="0 0 24 24"
                  >
                    <circle
                      className="opacity-25"
                      cx="12"
                      cy="12"
                      r="10"
                      stroke="currentColor"
                      strokeWidth="4"
                    ></circle>
                    <path
                      className="opacity-75"
                      fill="currentColor"
                      d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                    ></path>
                  </svg>
                  Processing...
                </>
              ) : (
                "Proceed to Payment"
              )}
            </Button>
          </form>
        </Form>
      </div>
    </div>
  );
}
