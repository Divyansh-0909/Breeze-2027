import { NextResponse } from "next/server";

import { prisma } from "@/lib/prisma";

export async function GET() {
    const x = await prisma.merchItem.findMany({select: {product_name: true, product_description: true, product_price: true}});
  return NextResponse.json(x);
}