"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
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
import { login } from "./action";

const formSchema = z.object({
  email: z.string().email(),
  password: z.string().min(4),
});

export default function LoginPage() {
  const router = useRouter();
  const [errorMsg, setErrorMsg] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      email: "",
      password: "",
    },
  });

  async function onSubmit(values: z.infer<typeof formSchema>) {
    setErrorMsg("");
    setIsLoading(true);
    try {
      const formData = new FormData();
      formData.append("email", values.email);
      formData.append("password", values.password);
      const result = await login(formData);

      if (result?.error) {
        setErrorMsg(result.error);
      } else if (result?.success && result.redirect) {
        router.push(result.redirect);
      }
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center" style={{ background: '#0a0a0a' }}>
      {/* Subtle grid pattern */}
      <div className="absolute inset-0 opacity-[0.03]" style={{
        backgroundImage: 'linear-gradient(rgba(255,255,255,.1) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,.1) 1px, transparent 1px)',
        backgroundSize: '64px 64px'
      }} />

      <div className="relative w-full max-w-[400px] mx-4">
        {/* Logo / Brand */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-10 h-10 rounded-lg mb-4" style={{ background: '#1a1a1a', border: '1px solid #262626' }}>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#888" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M12 2L2 7l10 5 10-5-10-5z" />
              <path d="M2 17l10 5 10-5" />
              <path d="M2 12l10 5 10-5" />
            </svg>
          </div>
          <h1 className="text-[15px] font-semibold tracking-[-0.01em]" style={{ color: '#e5e5e5' }}>
            Breeze Admin
          </h1>
          <p className="text-[13px] mt-1" style={{ color: '#666' }}>
            Sign in to your account
          </p>
        </div>

        {/* Card */}
        <div className="rounded-xl p-6" style={{ background: '#141414', border: '1px solid #1e1e1e' }}>
          {errorMsg && (
            <div className="mb-4 px-3 py-2.5 rounded-lg text-[13px]" style={{ background: 'rgba(239,68,68,0.08)', border: '1px solid rgba(239,68,68,0.15)', color: '#f87171' }}>
              {errorMsg}
            </div>
          )}

          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
              <FormField
                control={form.control}
                name="email"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel className="text-[13px] font-medium" style={{ color: '#a0a0a0' }}>
                      Email
                    </FormLabel>
                    <FormControl>
                      <Input
                        placeholder="admin@breeze.com"
                        {...field}
                        className="h-9 text-[13px] rounded-lg transition-colors duration-150"
                        style={{
                          background: '#0a0a0a',
                          border: '1px solid #262626',
                          color: '#e5e5e5',
                        }}
                      />
                    </FormControl>
                    <FormMessage className="text-[12px]" />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="password"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel className="text-[13px] font-medium" style={{ color: '#a0a0a0' }}>
                      Password
                    </FormLabel>
                    <FormControl>
                      <Input
                        type="password"
                        {...field}
                        className="h-9 text-[13px] rounded-lg transition-colors duration-150"
                        style={{
                          background: '#0a0a0a',
                          border: '1px solid #262626',
                          color: '#e5e5e5',
                        }}
                      />
                    </FormControl>
                    <FormMessage className="text-[12px]" />
                  </FormItem>
                )}
              />
              <Button
                type="submit"
                disabled={isLoading}
                className="w-full h-9 text-[13px] font-medium rounded-lg transition-all duration-150"
                style={{
                  background: '#e5e5e5',
                  color: '#0a0a0a',
                  opacity: isLoading ? 0.6 : 1,
                }}
              >
                {isLoading ? (
                  <span className="flex items-center gap-2">
                    <svg className="animate-spin h-3.5 w-3.5" viewBox="0 0 24 24" fill="none">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                    </svg>
                    Signing in…
                  </span>
                ) : (
                  "Sign in"
                )}
              </Button>
            </form>
          </Form>
        </div>

        <p className="text-center mt-6 text-[12px]" style={{ color: '#444' }}>
          Breeze 2027 - Admin Portal
        </p>
      </div>
    </div>
  );
}
