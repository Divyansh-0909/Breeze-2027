"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { z } from "zod";

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

import { useState } from "react";

const formSchema = z.object({
  name: z.string().min(2, {
    message: "Name must be at least 2 characters.",
  }).max(50, {
    message: "Name must be less than 50 characters.",
  }),
  email: z.string().email("Please enter a valid email address.").max(100, {
    message: "Email must be less than 100 characters.",
  }),
  phone: z.string().min(10, {
    message: "Phone number must be at least 10 digits.",
  }).max(15, {
    message: "Phone number must be less than 15 digits.",
  }),
  message: z.string().min(2, {
    message: "Message must be at least 2 characters.",
  }).max(500, {
    message: "Message must be less than 500 characters.",
  }),
});

export default function Question() {
  const [isSubmitted, setIsSubmitted] = useState(false);
  
  const form = useForm({
    resolver: zodResolver(formSchema),
    defaultValues: {
      name: "",
      email: "",
      phone: "",
      message: "",
    },
  });

  const onSubmit = async (data) => {
    try {
      // Save to database
      const response = await fetch("/api/contact", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name: data.name,
          email: data.email,
          phone: data.phone,
          message: data.message,
        }),
      });

      if (response.ok) {
        // Reset form and show success message
        form.reset();
        setIsSubmitted(true);
      }
    } catch (error) {
      console.error("Failed to save contact form:", error);
    }
  };

  return (
    <div className="min-h-screen flex flex-col lg:flex-row px-6 md:px-12 lg:px-20 pt-20 pb-4 lg:pt-24 lg:pb-0 overflow-hidden">
      {/* Left Section - CONTACT US */}
      <div className="w-full lg:w-1/2 flex flex-col items-center lg:items-start justify-center lg:justify-start py-4 lg:py-0">
        <h1
          className="text-5xl sm:text-6xl md:text-7xl lg:text-8xl xl:text-9xl font-bold tracking-tight leading-none text-center lg:text-left"
          style={{ color: "#FF6F00" }}
        >
          CONTACT
          <br />
          US
        </h1>
        
        {/* Tagline Section */}
        <p className="mt-6 md:mt-8 text-white/90 text-base md:text-lg leading-relaxed text-center lg:text-left max-w-md">
          Let's create something unforgettable.
          <br />
          From ideas to collaborations and everything in between drop us a message and be part of the energy behind
          <br />
          <span className="font-bold text-yellow-400">BREEZE'26: Neon Nirvana.</span>
        </p>
      </div>

      {/* Right Section - Form */}
      <div className="w-full lg:w-1/2 flex flex-col items-center lg:items-start justify-center lg:pl-12">
        {isSubmitted ? (
          <div className="w-full max-w-lg space-y-6 text-center lg:text-left">
            <div className="bg-green-500/20 border-2 border-green-500 rounded-lg p-6">
              <h2 className="text-2xl md:text-3xl font-bold text-green-400 mb-3">
                Message Sent Successfully!
              </h2>
              <p className="text-white/80 text-lg">
                Thank you for reaching out. We'll get back to you soon.
              </p>
            </div>
            <button
              onClick={() => setIsSubmitted(false)}
              className="text-yellow-400 hover:text-yellow-300 underline text-lg transition-colors"
            >
              Send another message
            </button>
          </div>
        ) : (
        <Form {...form}>
          <form
            onSubmit={form.handleSubmit(onSubmit)}
            className="w-full max-w-lg space-y-5"
          >
            {/* Name Field */}
            <FormField
              control={form.control}
              name="name"
              render={({ field }) => (
                <FormItem>
                  <FormLabel className="text-white text-base uppercase tracking-wider mb-1">
                    Name
                  </FormLabel>
                  <FormControl>
                    <Input
                      {...field}
                      placeholder="Your name"
                      className="h-14 text-lg px-4 bg-transparent border-2 border-yellow-400 rounded-none text-white placeholder:text-white/50 focus:border-yellow-300 focus:ring-0 focus-visible:ring-0 focus-visible:ring-offset-0"
                    />
                  </FormControl>
                  <FormMessage className="text-red-400" />
                </FormItem>
              )}
            />
            {/* Email Field */}
            <FormField
              control={form.control}
              name="email"
              render={({ field }) => (
                <FormItem>
                  <FormLabel className="text-white text-base uppercase tracking-wider mb-1">
                    Email
                  </FormLabel>
                  <FormControl>
                    <Input
                      type="email"
                      {...field}
                      placeholder="your@email.com"
                      className="h-14 text-lg px-4 bg-transparent border-2 border-yellow-400 rounded-none text-white placeholder:text-white/50 focus:border-yellow-300 focus:ring-0 focus-visible:ring-0 focus-visible:ring-offset-0"
                    />
                  </FormControl>
                  <FormMessage className="text-red-400" />
                </FormItem>
              )}
            />
            {/* Phone Number Field */}
            <FormField
              control={form.control}
              name="phone"
              render={({ field }) => (
                <FormItem>
                  <FormLabel className="text-white text-base uppercase tracking-wider mb-1">
                    Phone
                  </FormLabel>
                  <FormControl>
                    <Input
                      {...field}
                      placeholder="Your phone number"
                      className="h-14 text-lg px-4 bg-transparent border-2 border-yellow-400 rounded-none text-white placeholder:text-white/50 focus:border-yellow-300 focus:ring-0 focus-visible:ring-0 focus-visible:ring-offset-0"
                    />
                  </FormControl>
                  <FormMessage className="text-red-400" />
                </FormItem>
              )}
            />
            {/* Message Field */}
            <FormField
              control={form.control}
              name="message"
              render={({ field }) => (
                <FormItem>
                  <FormLabel className="text-white text-base uppercase tracking-wider mb-1">
                    Message
                  </FormLabel>
                  <FormControl>
                    <Input
                      {...field}
                      placeholder="Your message"
                      className="h-14 text-lg px-4 bg-transparent border-2 border-yellow-400 rounded-none text-white placeholder:text-white/50 focus:border-yellow-300 focus:ring-0 focus-visible:ring-0 focus-visible:ring-offset-0"
                    />
                  </FormControl>
                  <FormMessage className="text-red-400" />
                </FormItem>
              )}
            />
            {/* Submit Button */}
            <div className="pt-4">
              <Button
                type="submit"
                className="w-full h-14 bg-yellow-400 hover:bg-yellow-500 text-black font-bold text-lg uppercase tracking-wider rounded-none transition-colors"
              >
                Submit
              </Button>
            </div>
          </form>
        </Form>
        )}
      </div>
    </div>
  );
}
