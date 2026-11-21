import { prisma } from "@/lib/prisma";
import { readEventCatalog } from "./catalog";
import { currentCypherEvents } from "./cypher-schedule";

export async function readCypherEvents() {
  const catalog = await readEventCatalog(() => prisma.eventItem.findMany({
    select: {
      id: true, event_name: true, event_description: true, event_org: true, event_date: true,
      event_end_date: true, event_venue: true, event_type: true, image_url: true, registration_open: true,
    },
  }));
  return catalog.available
    ? { available: true as const, data: currentCypherEvents(catalog.data) }
    : catalog;
}

export type CypherCatalog = Awaited<ReturnType<typeof readCypherEvents>>;
export type CypherEvent = NonNullable<CypherCatalog["data"]>[number];
