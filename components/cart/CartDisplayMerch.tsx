"use client";
import Image from 'next/image';
import { MerchItem } from "@prisma/client";
import { useEffect, useState } from "react";

export default function CartDisplayMerch({ items }: { items: MerchItem[] }) {
  const [cartItems, setCartItems] = useState<{
    [key: string]: (MerchItem & { quantity: number; size: string })[];
  }>({});
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const updateCartFromStorage = () => {
      const cart = JSON.parse(localStorage.getItem("cart") || "{}");
      const cartWithDetails: {
        [key: string]: (MerchItem & { quantity: number; size: string })[];
      } = {};

      items.forEach((item) => {
        if (cart[item.id]) {
          cartWithDetails[item.id] = Object.entries(cart[item.id]).map(
            ([size, quantity]) => ({
              ...item,
              quantity: quantity as number,
              size,
            })
          );
        }
      });
      setCartItems(cartWithDetails);
    };

    // Initial load
    updateCartFromStorage();
    setIsLoading(false);

    // Listen for storage changes
    window.addEventListener("storage", updateCartFromStorage);

    return () => {
      window.removeEventListener("storage", updateCartFromStorage);
    };
  }, [items]);

  if (isLoading) {
    return <div className="text-center text-xl">Your cart is loading...</div>;
  }

  if (Object.keys(cartItems).length === 0) {
    return (
    <div className='mt-10'>
      <div className='py-2'></div>
      <Image 
        src="/images/empty-cart.png"
        alt="Not Found"
        width={275} 
        height={275} 
        className="mt-10 mx-auto" 
      /> 
      <p className="mt-8 text-center font-semibold text-xl">Your Cart is empty</p>
      <p className="text-center mt-2 text-gray-600">Looks like you have not added anything to your cart. Go </p>
      <p className="text-center text-gray-600">ahead and & explore top categories</p>
      <div className='py-10'></div>
    </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto p-6">
      {Object.entries(cartItems).map(([itemId, sizeVariants]) =>
        sizeVariants.map((item) => (
          <div
            key={`${itemId}-${item.size}`}
            className="flex items-center justify-between p-2 mb-2 bg-white shadow-lg rounded-lg border hover:shadow-xl transition-all sm:p-4 sm:mb-4"
          >
            <div className="flex-shrink-0 w-12 h-12 sm:w-16 sm:h-16 mr-3">
              <Image
                src={"/images/product-placeholder.png"} // item.img_url here later
                alt={item.product_name}
                width={64}
                height={64}
                className="w-full h-full object-cover rounded-md"
              />
            </div>

            <div className="flex flex-col flex-grow">
              <h3 className="text-sm sm:text-xl font-semibold text-gray-800 truncate">{item.product_name}</h3>
              <p className="text-xs sm:text-base text-gray-600">₹{item.product_price}</p>
              <p className="text-xs sm:text-base text-gray-600">Size: {item.size}</p>
            </div>

            <div className="flex items-center space-x-2 mt-2 sm:mt-0">
              <div className="flex items-center space-x-2">
                <button
                  className="px-2 py-1 border rounded-md text-xs sm:text-sm text-gray-700 hover:bg-gray-200"
                  aria-label={`Decrease quantity of ${item.product_name}`}
                >
                  -
                </button>
                <span className="text-xs sm:text-sm">{item.quantity}</span>
                <button
                  className="px-2 py-1 border rounded-md text-xs sm:text-sm text-gray-700 hover:bg-gray-200"
                  aria-label={`Increase quantity of ${item.product_name}`}
                >
                  +
                </button>
              </div>

              <div className="font-semibold text-xs sm:text-lg text-gray-900">
                Total: ₹{item.product_price * item.quantity}
              </div>
            </div>
          </div>
        ))
      )}

      <div className="mt-4 sm:mt-6 text-right text-lg sm:text-xl font-bold">
        Grand Total: ₹
        {Object.values(cartItems)
          .flat()
          .reduce((acc, item) => acc + item.product_price * item.quantity, 0)}
      </div>
    </div>
  );
}