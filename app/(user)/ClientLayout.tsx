"use client";

import React from "react";
import { usePathname } from "next/navigation";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";

// Define the page order for overscroll navigation
const pageOrder = ["/", "/events", "/get-in-touch"];

export default function ClientLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const pathname = usePathname();
  const isHomepage = pathname === "/";

  // Determine the next page based on current route
  const getNextPage = () => {
    const currentIndex = pageOrder.indexOf(pathname);
    if (currentIndex === -1 || currentIndex === pageOrder.length - 1) {
      // Not in page order or last page - loop back to first
      return pageOrder[0];
    }
    return pageOrder[currentIndex + 1];
  };

  const nextPage = getNextPage();

  return (
    <div
      className="min-h-screen w-full text-white overflow-x-hidden"
      style={{
        background: isHomepage
          ? "black"
          : "linear-gradient(90deg, #3D025ABD 0%, transparent 50%, #3D025ABD 100%), black",
      }}
    >
      <Navbar />

      <main className="w-full">{children}</main>

      {!pathname.startsWith("/team") && <Footer nextPage={nextPage} />}
    </div>
  );
}
