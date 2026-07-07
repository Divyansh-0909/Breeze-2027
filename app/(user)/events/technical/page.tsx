import React from "react";
import Heading2 from "@/components/events/heading2";
import BasicCards from "@/components/events/BasicCards";
import BottomButtons from "@/components/events/bottombuttons";
import { prisma } from "@/lib/prisma";

export const dynamic = "force-dynamic";

const page = async ({
  searchParams,
}: {
  searchParams: Promise<{ page?: string }>;
}) => {
  const params = await searchParams;
  const all_events = await prisma.eventItem.findMany({
    select: {
      event_name: true,
      event_description: true,
      event_price: true,
      event_venue: true,
      event_org: true,
      event_date: true,
      image_url: true,
      id: true,
      registration_open: true,
    },
    where: {
      event_type: {
        equals: "Technical",
      },
    },
  });

  const currentPage = Number(params.page) || 1;
  const totalItems = all_events.length;
  const itemsPerPage = 10;
  const startIndex = (currentPage - 1) * itemsPerPage;
  const eventsForPage = all_events.slice(startIndex, startIndex + itemsPerPage);

  return (
    <div className="pt-20">
      <title>Technical Events - Breeze '26</title>
      <Heading2 content="Here's all the technical events Breeze 26' has in store for you" />

      <div className="m-10 mt-0">
        <div className="flex justify-center py-10">
          <div className="">
            <BasicCards event={eventsForPage} />
          </div>
        </div>
      </div>

      <BottomButtons currentPage={currentPage} totalItems={totalItems} />
    </div>
  );
};

export default page;
