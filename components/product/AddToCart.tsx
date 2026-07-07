"use client";

import { useState, useEffect } from "react";
import { useSizeContext } from "./SizeSelector";
import { Button } from "../ui/button";
import { useRouter } from "next/navigation";

export const AddToCartMerch = ({ merch_id }: { merch_id: string }) => {
  const { selectedSize } = useSizeContext();
  const [quantity, setQuantity] = useState(0);

  useEffect(() => {
    const cart = JSON.parse(localStorage.getItem("cart") || "{}");
    if (cart[merch_id]?.[selectedSize]) {
      setQuantity(cart[merch_id][selectedSize]);
    } else {
      setQuantity(0);
    }
  }, [merch_id, selectedSize]);

  const handleAddToCart = () => {
    if (!selectedSize) {
      alert("Please select a size before adding to the cart!");
      return;
    }

    const cart = JSON.parse(localStorage.getItem("cart") || "{}");
    if (!cart[merch_id]) {
      cart[merch_id] = {};
    }
    cart[merch_id][selectedSize] = (cart[merch_id][selectedSize] || 0) + 1;
    localStorage.setItem("cart", JSON.stringify(cart));
    setQuantity(cart[merch_id][selectedSize]);
  };

  const handleRemoveFromCart = () => {
    if (!selectedSize) return;

    const cart = JSON.parse(localStorage.getItem("cart") || "{}");
    if (cart[merch_id]?.[selectedSize] > 1) {
      cart[merch_id][selectedSize] -= 1;
    } else {
      delete cart[merch_id][selectedSize];
      if (Object.keys(cart[merch_id]).length === 0) {
        delete cart[merch_id];
      }
    }
    localStorage.setItem("cart", JSON.stringify(cart));
    setQuantity(cart[merch_id]?.[selectedSize] || 0);
  };

  return (
    <div className="mt-8 flex space-x-4 items-center">
      {quantity > 0 ? (
        <>
          <button
            className="w-[40px] h-[40px] sm:w-[40px] sm:h-[40px] bg-black text-white font-semibold rounded-lg"
            onClick={handleRemoveFromCart}
          >
            -
          </button>
          <span>{quantity}</span>
          <button
            className="w-[40px] h-[40px] sm:w-[40px] sm:h-[40px] bg-black text-white font-semibold rounded-lg"
            onClick={handleAddToCart}
          >
            +
          </button>
        </>
      ) : (
        <button
          className=" sm:w-[200px] text-[16px] sm:h-[50px] h-[10vw] bg-black text-white font-semibold rounded-lg  w-[30vw]"
          onClick={handleAddToCart}
        >
          Buy Now
        </button>
      )}
    </div>
  );
};

export const AddToCartEvent = ({ 
  event_id, 
  event_price,
  event_pair_price 
}: { 
  event_id: string;
  event_price?: number;
  event_pair_price?: number | null;
}) => {
  const [singleQuantity, setSingleQuantity] = useState(0);
  const [pairQuantity, setPairQuantity] = useState(0);
  const router = useRouter();

  useEffect(() => {
    const cart = JSON.parse(localStorage.getItem("cart") || "{}");
    // Support legacy "NA" key and new "SINGLE"/"PAIR" keys
    setSingleQuantity(cart[event_id]?.["SINGLE"] || cart[event_id]?.["NA"] || 0);
    setPairQuantity(cart[event_id]?.["PAIR"] || 0);
  }, [event_id]);

  const handleAddSingle = () => {
    const cart = JSON.parse(localStorage.getItem("cart") || "{}");
    if (!cart[event_id]) {
      cart[event_id] = {};
    }
    // Clear legacy NA key if present
    if (cart[event_id]["NA"]) {
      cart[event_id]["SINGLE"] = cart[event_id]["NA"];
      delete cart[event_id]["NA"];
    }
    cart[event_id]["SINGLE"] = (cart[event_id]["SINGLE"] || 0) + 1;
    localStorage.setItem("cart", JSON.stringify(cart));
    setSingleQuantity(cart[event_id]["SINGLE"]);
  };

  const handleRemoveSingle = () => {
    const cart = JSON.parse(localStorage.getItem("cart") || "{}");
    if (cart[event_id]?.["SINGLE"] > 1) {
      cart[event_id]["SINGLE"] -= 1;
    } else {
      delete cart[event_id]["SINGLE"];
      if (Object.keys(cart[event_id] || {}).length === 0) {
        delete cart[event_id];
      }
    }
    localStorage.setItem("cart", JSON.stringify(cart));
    setSingleQuantity(cart[event_id]?.["SINGLE"] || 0);
  };

  const handleAddPair = () => {
    const cart = JSON.parse(localStorage.getItem("cart") || "{}");
    if (!cart[event_id]) {
      cart[event_id] = {};
    }
    cart[event_id]["PAIR"] = (cart[event_id]["PAIR"] || 0) + 1;
    localStorage.setItem("cart", JSON.stringify(cart));
    setPairQuantity(cart[event_id]["PAIR"]);
  };

  const handleRemovePair = () => {
    const cart = JSON.parse(localStorage.getItem("cart") || "{}");
    if (cart[event_id]?.["PAIR"] > 1) {
      cart[event_id]["PAIR"] -= 1;
    } else {
      delete cart[event_id]["PAIR"];
      if (Object.keys(cart[event_id] || {}).length === 0) {
        delete cart[event_id];
      }
    }
    localStorage.setItem("cart", JSON.stringify(cart));
    setPairQuantity(cart[event_id]?.["PAIR"] || 0);
  };

  const totalQuantity = singleQuantity + pairQuantity;

  return (
    <div className="w-full space-y-4">
      {/* Single Tickets */}
      <div className="flex items-center justify-between bg-white/10 rounded-lg p-3">
        <div>
          <span className="text-white font-medium">Single Ticket</span>
          {event_price !== undefined && (
            <span className="text-white/70 text-sm ml-2">₹{event_price}</span>
          )}
        </div>
        <div className="flex items-center gap-3">
          {singleQuantity > 0 && (
            <button
              className="w-8 h-8 rounded-full bg-white/20 hover:bg-white/30 text-white text-lg flex items-center justify-center transition-all border border-white/30"
              onClick={handleRemoveSingle}
            >
              −
            </button>
          )}
          <span className="text-xl font-bold text-white min-w-[30px] text-center">
            {singleQuantity}
          </span>
          <button
            className="w-8 h-8 rounded-full bg-[#ffbc00] hover:bg-[#ffbc00]/90 text-[#8200C1] text-lg flex items-center justify-center transition-all"
            onClick={handleAddSingle}
          >
            +
          </button>
        </div>
      </div>

      {/* Pair Tickets - only show if pair pricing is available */}
      {event_pair_price && (
        <div className="flex items-center justify-between bg-white/10 rounded-lg p-3">
          <div>
            <span className="text-white font-medium">Pair Ticket</span>
            <span className="text-white/70 text-sm ml-2">₹{event_pair_price}</span>
          </div>
          <div className="flex items-center gap-3">
            {pairQuantity > 0 && (
              <button
                className="w-8 h-8 rounded-full bg-white/20 hover:bg-white/30 text-white text-lg flex items-center justify-center transition-all border border-white/30"
                onClick={handleRemovePair}
              >
                −
              </button>
            )}
            <span className="text-xl font-bold text-white min-w-[30px] text-center">
              {pairQuantity}
            </span>
            <button
              className="w-8 h-8 rounded-full bg-[#ffbc00] hover:bg-[#ffbc00]/90 text-[#8200C1] text-lg flex items-center justify-center transition-all"
              onClick={handleAddPair}
            >
              +
            </button>
          </div>
        </div>
      )}

      {/* Proceed to Cart Button */}
      {totalQuantity > 0 && (
        <button
          className="w-full h-12 rounded-lg bg-[#ffbc00] hover:bg-[#ffbc00]/90 text-[#8200C1] font-semibold transition-all"
          onClick={() => router.push("/cart")}
        >
          Proceed to Cart ({totalQuantity} ticket{totalQuantity > 1 ? 's' : ''})
        </button>
      )}
    </div>
  );
};
