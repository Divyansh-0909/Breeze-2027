'use client';
import { EventItem } from '@prisma/client';
import { useEffect, useState } from 'react';

interface CartItem {
  id: string;
  event_name: string;
  event_price: number;
  event_pair_price?: number | null;
  singleQuantity: number;
  pairQuantity: number;
}

export default function CartDisplayEvent({ items }: { items: (EventItem & { event_pair_price?: number | null })[] }) {
  const [cartItems, setCartItems] = useState<CartItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const updateCartFromStorage = () => {
      const cart = JSON.parse(localStorage.getItem('cart') || '{}');
      const itemsWithCart: CartItem[] = [];

      items.forEach((item) => {
        // Support both legacy "NA" key and new "SINGLE"/"PAIR" keys
        const singleQty = cart[item.id]?.['SINGLE'] || cart[item.id]?.['NA'] || 0;
        const pairQty = cart[item.id]?.['PAIR'] || 0;
        
        if (singleQty > 0 || pairQty > 0) {
          itemsWithCart.push({
            id: item.id,
            event_name: item.event_name,
            event_price: item.event_price,
            event_pair_price: item.event_pair_price,
            singleQuantity: singleQty,
            pairQuantity: pairQty,
          });
        }
      });

      setCartItems(itemsWithCart);
    };

    updateCartFromStorage();
    setIsLoading(false);

    window.addEventListener('storage', updateCartFromStorage);
    return () => window.removeEventListener('storage', updateCartFromStorage);
  }, [items]);

  if (isLoading) {
    return <div className="text-center text-xl">Your cart is loading...</div>;
  }

  if (cartItems.length === 0) {
    return (
      <div className="text-center text-xl">
        You have no event tickets in your cart!
      </div>
    );
  }

  const calculateTotal = () => {
    return cartItems.reduce((acc, item) => {
      const singleTotal = item.event_price * item.singleQuantity;
      const pairTotal = (item.event_pair_price || item.event_price * 2) * item.pairQuantity;
      return acc + singleTotal + pairTotal;
    }, 0);
  };

  return (
    <div className="max-w-4xl mx-auto p-4">
      {cartItems.map((item) => (
        <div
          key={item.id}
          className="flex flex-col border-b py-4"
        >
          <h3 className="text-lg font-semibold">{item.event_name}</h3>
          <div className="flex flex-col gap-2 mt-2">
            {item.singleQuantity > 0 && (
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-600">
                  Single Tickets ({item.singleQuantity}x) - ₹{item.event_price} each
                </span>
                <span className="font-semibold">
                  ₹{item.event_price * item.singleQuantity}
                </span>
              </div>
            )}
            {item.pairQuantity > 0 && (
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-600">
                  Pair Tickets ({item.pairQuantity}x) - ₹{item.event_pair_price || item.event_price * 2} each
                </span>
                <span className="font-semibold">
                  ₹{(item.event_pair_price || item.event_price * 2) * item.pairQuantity}
                </span>
              </div>
            )}
          </div>
        </div>
      ))}
      <div className="mt-6 text-right text-xl font-bold">
        Total: ₹{calculateTotal()}
      </div>
    </div>
  );
}
