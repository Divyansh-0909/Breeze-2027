import { NextRequest, NextResponse } from "next/server";
import { prisma } from "@/lib/prisma";
import crypto from "crypto";
import { accommodation_option } from "@prisma/client";

export async function POST(req: NextRequest) {
  try {
    const data = await req.json();
    const cart: { [key: string]: { [ticketType: string]: number } } = data["cart"];
    const accommodation: [boolean, boolean, boolean] = data["accommodation"];

    const merch_items = await prisma.merchItem.findMany();
    const event_items = await prisma.eventItem.findMany();
    const merchPrices = new Map(
      merch_items.map((item) => [item.id, item.product_price])
    );
    // Store both single and pair prices for events
    const eventPrices = new Map(
      event_items.map((item) => [item.id, { single: item.event_price, pair: item.event_pair_price }])
    );

    let total = 0;
    Object.entries(cart).forEach(([itemId, sizes]) => {
      Object.entries(sizes).forEach(([sizeOrTicketType, quantity]) => {
        if (merchPrices.has(itemId)) {
          // Merch item
          total += merchPrices.get(itemId)! * quantity;
        } else if (eventPrices.has(itemId)) {
          // Event item - check for SINGLE, PAIR, or legacy NA
          const prices = eventPrices.get(itemId)!;
          if (sizeOrTicketType === "PAIR" && prices.pair) {
            total += prices.pair * quantity;
          } else {
            // SINGLE, NA, or any other key uses single price
            total += prices.single * quantity;
          }
        }
      });
    });

    let accommodation_array: any[] = [];
    let accommodation_price = 0;

    const id = crypto.randomBytes(32).toString("hex");
    try {
      await prisma.pendingTransaction.create({
        data: {
          amount: total + accommodation_price,
          id,
          cart,
          accommodation_price,
          accommodation:
            accommodation_array ? accommodation_array : null,
        },
      });
    } catch (e) {
      console.log(e)
      return NextResponse.json("Error processing checkout", { status: 500 });
    }
    return NextResponse.json({ message: "Success", id }, { status: 200 });
  } catch (e) {
    return NextResponse.json("Error processing checkout", { status: 500 });
  }
}
