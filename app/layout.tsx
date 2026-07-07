import type { Metadata } from "next";
import { Inter } from "next/font/google";
import { Analytics } from "@vercel/analytics/react";
import { SpeedInsights } from "@vercel/speed-insights/next";
import "./globals.css";
import React from "react";
const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Breeze'26",
  description: "The Annual Techno-Cultural Fest of SNU",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="w-full">
      <body className={`${inter.className} w-full min-w-full`}>
        {children}
        <Analytics />
        <SpeedInsights />
      </body>
    </html>
  );
}
