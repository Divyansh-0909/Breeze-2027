import React from "react";
import Link from "next/link"; 
import { Card } from "@/components/ui/card";
import BasicCards from "./BasicCards";
import { prisma } from "@/lib/prisma";


const CardSection = async () => {
  const all_events = await prisma.eventItem.findMany({
    orderBy: { event_name: 'asc' },
    take: 10,
  });

  return (
    <div className="m-10 mt-0">
      <div className="flex justify-center py-10">
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-7 w-full">
        <BasicCards event={all_events}/>
          
          
          
        </div>
      </div>
    </div>
  );
};

export default CardSection;


