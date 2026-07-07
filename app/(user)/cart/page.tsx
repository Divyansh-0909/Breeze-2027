import { prisma } from "@/lib/prisma";
import CartDisplay from "@/components/cart/CartDisplay";

export const dynamic = "force-dynamic";

export const metadata = {
  title: "Cart - Breeze '26",
  description: "Your Shopping Cart",
};

export default async function Page() {
  const merch_items = await prisma.merchItem.findMany();
  const event_items = await prisma.eventItem.findMany();

  return (
    <div className="pt-20 space-y-8 min-h-screen">
      <p className="text-4xl font-thin pt-10 text-center" style={{ fontFamily: "Fraunces, sans-serif" }}>Your Shopping Cart</p>
      <CartDisplay merch_items={merch_items} event_items={event_items} />
    </div>
  );
}
