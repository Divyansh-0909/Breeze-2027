import React from "react";
import Link from "next/link"; 
import { Card } from "@/components/ui/card";
import PhotoCard from "./PhotoCard";
import BasicCards from "./BasicCards";
import { prisma } from "@/lib/prisma";


const CardSection = async () => {
  const all_merch = await prisma.merchItem.findMany({
    select: { product_name: true, product_description: true, product_price: true, id: true, image_url: true },
    orderBy: { product_name: 'asc' },
    take: 10,
  });
  return (
    <div className="m-10 mt-0">
      <div className="flex justify-center py-10">
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-7 w-full">
          <BasicCards merch={all_merch.slice(0, 4)}/>
          <PhotoCard></PhotoCard>
          <BasicCards merch={all_merch.slice(4, 10)}></BasicCards>
        </div>
      </div>
    </div>
  );
};

export default CardSection;


