"use client";
import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Button } from "../ui/button";

interface CheckoutButtonProps {
  accommodation: [boolean, boolean, boolean];
}

export default function CheckoutButton({ accommodation }: CheckoutButtonProps) {
  const [isLoading, setIsLoading] = useState(false);
  const [cart, setCart] = useState({});
  const router = useRouter();

  useEffect(() => {
    const updateCartFromStorage = () => {
      const cartData = JSON.parse(localStorage.getItem("cart") || "{}");
      setCart(cartData);
    };

    updateCartFromStorage();
    window.addEventListener("storage", updateCartFromStorage);
    return () => window.removeEventListener("storage", updateCartFromStorage);
  }, []);

  const handleCheckout = async () => {
    setIsLoading(true);
    try {
      const cartData = JSON.parse(localStorage.getItem("cart") || "{}");
      setCart(cartData);
      const response = await fetch("/api/checkout", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          cart: cartData,
          accommodation,
        }),
      });
      const data: { message: string; id: string } = await response.json();
      if (response.ok) {
        router.push(`/checkout?token=${data.id}`);
      }
    } catch (error) {
      alert("Error processing checkout");
    } finally {
      setIsLoading(false);
    }
  };

  const hasItems = Object.keys(cart).length > 0 || accommodation.includes(true);

  if (!hasItems) {
    return null;
  }
  return (
    <div>
      <Button
        onClick={handleCheckout}
        disabled={isLoading}
        className="font-semibold py-3 px-8 text-lg border-2 border-[#ffbc00] bg-[#ffbc00] hover:bg-[#ffbc00]/90 text-[#8200C1] rounded-lg shadow-lg transition-all"
      >
        {isLoading ? "Processing..." : "Proceed to Checkout"}
      </Button>
      <div className="py-10"></div>
    </div>
  );
}
