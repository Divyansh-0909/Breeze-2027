"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import Footer from "@/components/Footer";
import MerchScroll from "@/components/merchscroll";
import BuyMerch from "@/components/buymerch";

export default function MerchPage() {
  const router = useRouter();

  // Temporarily redirect users away from merch page
  useEffect(() => {
    router.replace("/");
  }, [router]);

  // Return null while redirecting
  return null;

  /* Original merch page content - temporarily disabled
  return (
    <div className="relative w-full">
      <MerchScroll />
      <BuyMerch />
      <div className="relative z-50 bg-black text-white">
        <Footer />
      </div>
    </div>
  );
  */
}
