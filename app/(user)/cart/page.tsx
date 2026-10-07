import { prisma } from "@/lib/prisma";
import CartDisplay from "@/components/cart/CartDisplay";
import type { MerchItem, EventItem } from "@prisma/client";

export const dynamic = "force-dynamic";

export const metadata = {
  title: "Cart - Breeze '26",
  description: "Your Shopping Cart",
};

export default async function Page() {
  let merch_items: MerchItem[] = [];
  let event_items: EventItem[] = [];
  let catalogAvailable = false;

  if (process.env.DATABASE_URL?.trim()) {
    try {
      [merch_items, event_items] = await Promise.all([
        prisma.merchItem.findMany(),
        prisma.eventItem.findMany(),
      ]);
      catalogAvailable = true;
    } catch {
      console.error("Cart catalog could not be loaded from the database.");
    }
  }

  return (
    <div className="pt-20 space-y-8 min-h-screen">
      <p className="text-4xl font-thin pt-10 text-center" style={{ fontFamily: "Fraunces, sans-serif" }}>Your Shopping Cart</p>
      <CartDisplay merch_items={merch_items} event_items={event_items} catalogAvailable={catalogAvailable} />
    </div>
  );
}
