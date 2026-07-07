import React from "react";
import Link from "next/link";
import { Card } from "@/components/ui/card";
import { Button } from "../ui/button";
import Image from "next/image";
import { Badge } from "@/components/ui/badge";

interface EventItem {
  id: string;
  event_name: string;
  event_description: string;
  event_price: number;
  event_org: string;
  event_date: string;
  event_venue: string;
  image_url: string;
  registration_open?: boolean;
  event_end_date?: string | null;
  event_pair_price?: number | null;
}

const BasicCards = ({ event }: { event: EventItem[] }) => {
  return (
    <div className="grid grid-flow-row grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 2xl:grid-cols-5 gap-8">
      {event?.map((item, id) => (
        <Link
          key={id}
          className="bg-card group transition-transform duration-300 hover:-translate-y-2"
          href={`/events/${item.id}`}
          target="_blank"
          rel="noopener noreferrer"
        >
          <div className="flex flex-col border-2 border-border rounded-lg shadow-md hover:shadow-xl transition-shadow duration-300">
            <div>
              <div className="relative w-full aspect-[3/4] rounded-t-lg overflow-hidden">
                <Image
                  src={
                    item.image_url.startsWith("http")
                      ? item.image_url
                      : `https://media.breezesnu.com/${item.image_url}`
                  }
                  alt={`${item.event_name} poster`}
                  fill
                  className="object-cover transition-transform duration-300 group-hover:scale-105"
                  sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
                  priority={id < 4}
                />
                {item.registration_open === false && (
                  <div className="absolute top-2 right-2">
                    <Badge
                      variant="destructive"
                      className="text-xs font-semibold"
                    >
                      Registrations Closed
                    </Badge>
                  </div>
                )}
              </div>
            </div>
            <div className="p-4 space-y-3">
              <div className="flex justify-between items-center">
                <p className="text-lg h-14 max-h-14 text-muted-foreground font-medium line-clamp-2">
                  {item.event_org}
                </p>
                <div className="flex flex-col items-end">
                  <p className="px-3 py-1 bg-yellow-100 text-yellow-800 rounded-full text-sm font-semibold">
                    {item.event_price === 0 ? "FREE" : `₹${item.event_price}`}
                  </p>
                  {item.event_pair_price && (
                    <span className="text-xs text-muted-foreground mt-1">
                      Pair: ₹{item.event_pair_price}
                    </span>
                  )}
                </div>
              </div>
              <div className="text-xl h-14 max-h-14 font-bold line-clamp-2">
                {item.event_name}
              </div>
              <div className="text-sm text-muted-foreground">
                <div className="flex flex-wrap gap-2 w-full ">
                  <p className="flex items-center">
                    <span className="mr-1">📅</span> 
                    {item.event_date}
                    {item.event_end_date && ` - ${item.event_end_date}`}
                  </p>
                </div>
                <p className="mt-0.5 flex items-center">
                  <span className="mr-1">📍</span> {item.event_venue}
                </p>
              </div>
            </div>
          </div>
        </Link>
      ))}
    </div>
  );
};

export default BasicCards;
