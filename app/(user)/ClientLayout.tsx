"use client";

import React, { useSyncExternalStore } from "react";
import { usePathname } from "next/navigation";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import dynamic from "next/dynamic";
import { wantsClassicHub } from "@/lib/classic-hub";

const ImmersiveShell = dynamic(() => import("@/components/immersive/ImmersiveShell"), { ssr: false });

// Next re-renders on every router and history change, so reading the query
// on render stays current without a Suspense boundary around the whole layout.
const noSubscribe = () => () => {};
const readClassicHub = () => wantsClassicHub(new URLSearchParams(window.location.search));

// Define the page order for overscroll navigation
const pageOrder = ["/", "/events", "/get-in-touch"];

export default function ClientLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const pathname = usePathname();
  const classicHub = useSyncExternalStore(noSubscribe, readClassicHub, () => false);
  const isHomepage = pathname === "/";
  const isPaymentRoute = pathname === "/checkout" || pathname === "/thank-you" || pathname.startsWith("/payments/");

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

  // The home page renders the walkable gully and cypher itself. The classic
  // hub fallback and the Aftermovie route keep the original persistent shell.
  if ((pathname === "/" && classicHub) || pathname === "/aftermovie") {
    return <><ImmersiveShell />{children}</>;
  }
  if (pathname === "/") return <>{children}</>;

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

      {!pathname.startsWith("/team") && !isPaymentRoute && <Footer nextPage={nextPage} />}
    </div>
  );
}
