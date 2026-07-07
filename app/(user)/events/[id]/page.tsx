import React from "react";
import { prisma } from "@/lib/prisma";
import { AddToCartEvent } from "@/components/product/AddToCart";
import Image from "next/image";
import { Badge } from "@/components/ui/badge";

export default async function Page({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const event = await prisma.eventItem.findUnique({
    where: { id: (await params).id },
  });

  if (!event) {
    return (
      <div className="flex items-center justify-center h-screen text-white text-xl">
        Event not found
      </div>
    );
  }

  return (
    <div className="min-h-screen py-20 md:py-32 px-4 sm:px-8 lg:px-16">
      <title>{event.event_name + " - Breeze '26"}</title>

      <div className="max-w-7xl mx-auto">
        {/* Event Name */}
        <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold mb-8 md:mb-12 text-center">
          {event.event_name}
        </h1>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 lg:gap-12">
          {/* Image Section */}
          <div className="relative w-full aspect-[3/4] max-w-[500px] mx-auto lg:mx-0 rounded-2xl overflow-hidden shadow-2xl">
            {event.image_url ? (
              <Image
                src={
                  event.image_url.startsWith("http")
                    ? event.image_url
                    : `https://media.breezesnu.com/${event.image_url}`
                }
                alt={`${event.event_name} poster`}
                fill
                className="object-cover"
                priority
                unoptimized
              />
            ) : (
              <div className="w-full h-full bg-gradient-to-br from-purple-600 to-purple-900 flex items-center justify-center">
                <span className="text-white text-2xl">No Image Available</span>
              </div>
            )}
            {!event.registration_open && (
              <div className="absolute top-4 right-4">
                <Badge
                  variant="destructive"
                  className="text-sm font-semibold px-4 py-2 shadow-lg"
                >
                  Registrations Closed
                </Badge>
              </div>
            )}
          </div>

          {/* Event Details Section */}
          <div className="flex flex-col gap-6 text-white">
            <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6 border border-white/20">
              <h2 className="text-xl md:text-2xl font-semibold mb-2">
                Organized by
              </h2>
              <p className="text-2xl md:text-3xl font-bold text-[#ffbc00]">
                {event.event_org}
              </p>
            </div>

            <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6 border border-white/20">
              <h3 className="text-xl md:text-2xl font-bold mb-3 text-[#ffbc00]">
                Description
              </h3>
              <p className="text-base md:text-lg leading-relaxed">
                {event.event_description}
              </p>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 border border-white/20">
                <h3 className="text-sm font-semibold text-[#ffbc00] mb-1">
                  Date
                </h3>
                <p className="text-lg">
                  {event.event_date}
                  {event.event_end_date && ` - ${event.event_end_date}`}
                </p>
              </div>

              <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 border border-white/20">
                <h3 className="text-sm font-semibold text-[#ffbc00] mb-1">
                  Location
                </h3>
                <p className="text-lg">{event.event_venue}</p>
              </div>

              <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 border border-white/20 sm:col-span-2">
                <h3 className="text-sm font-semibold text-[#ffbc00] mb-1">
                  Pricing
                </h3>
                <div className="flex gap-4 items-center">
                  <div>
                    <p className="text-lg font-bold">
                      {event.event_price === 0 ? "Free" : `₹${event.event_price}`}
                    </p>
                    <span className="text-xs text-white/70">Single Ticket</span>
                  </div>
                  {event.event_pair_price && (
                    <>
                      <span className="text-white/50">|</span>
                      <div>
                        <p className="text-lg font-bold">₹{event.event_pair_price}</p>
                        <span className="text-xs text-white/70">Pair Ticket</span>
                      </div>
                    </>
                  )}
                </div>
              </div>
            </div>

            {/* Call to Action */}
            <div className="mt-4">
              {event.registration_open ? (
              <AddToCartEvent 
                event_id={event.id} 
                event_price={event.event_price}
                event_pair_price={event.event_pair_price}
              />
              ) : (
                <div className="bg-red-900/30 backdrop-blur-sm rounded-xl p-6 border border-red-500/50 text-center">
                  <Badge
                    variant="destructive"
                    className="text-lg px-6 py-3 mb-3"
                  >
                    Registrations Closed
                  </Badge>
                  <p className="text-sm text-white/80">
                    This event is no longer accepting registrations
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
