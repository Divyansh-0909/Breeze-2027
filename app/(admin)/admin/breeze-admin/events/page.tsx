import { prisma } from "@/lib/prisma";
import EventsTable from "./events-table";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import AddEvent from "./add-event";

export default async function Page() {
  const culturalEvents = await prisma.eventItem.findMany({
    where: { event_type: "Cultural" },
    orderBy: { created_at: "desc" },
  });

  const technicalEvents = await prisma.eventItem.findMany({
    where: { event_type: "Technical" },
    orderBy: { created_at: "desc" },
  });

  const allEvents = await prisma.eventItem.findMany({
    orderBy: { created_at: "desc" },
  });

  // Fetch all clubs for the add event dropdown
  const clubs = await prisma.roles.findMany({
    select: { id: true, club_name: true },
    orderBy: { club_name: "asc" },
  });

  // Get unique club names (in case of duplicates)
  const uniqueClubs = Array.from(
    new Map(clubs.map((club) => [club.club_name, club])).values()
  );

  return (
    <div className="min-h-screen bg-white">
      <div className="container mx-auto px-6 py-12">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-4xl font-bold text-[#202020] tracking-tight mb-2">
                Event Management
              </h1>
              <p className="text-gray-500 text-sm">
                Manage all events, edit details, and control registrations
              </p>
            </div>
            <AddEvent clubs={uniqueClubs} />
          </div>
        </div>

        {/* Tabs */}
        <Tabs defaultValue="all" className="w-full">
          <TabsList className="bg-gray-100 border border-[#202020]/10 p-1 mb-8 rounded-lg">
            <TabsTrigger
              value="all"
              className="data-[state=active]:bg-[#202020] data-[state=active]:text-white text-gray-600 rounded-md px-6 py-2.5 font-medium transition-all"
            >
              All Events
              <span className="ml-2 px-2 py-0.5 rounded-full bg-[#202020]/10 data-[state=active]:bg-white/20 text-xs">
                {allEvents.length}
              </span>
            </TabsTrigger>
            <TabsTrigger
              value="cultural"
              className="data-[state=active]:bg-[#202020] data-[state=active]:text-white text-gray-600 rounded-md px-6 py-2.5 font-medium transition-all"
            >
              Cultural
              <span className="ml-2 px-2 py-0.5 rounded-full bg-[#202020]/10 data-[state=active]:bg-white/20 text-xs">
                {culturalEvents.length}
              </span>
            </TabsTrigger>
            <TabsTrigger
              value="technical"
              className="data-[state=active]:bg-[#202020] data-[state=active]:text-white text-gray-600 rounded-md px-6 py-2.5 font-medium transition-all"
            >
              Technical
              <span className="ml-2 px-2 py-0.5 rounded-full bg-[#202020]/10 data-[state=active]:bg-white/20 text-xs">
                {technicalEvents.length}
              </span>
            </TabsTrigger>
          </TabsList>

          <TabsContent value="all" className="mt-0">
            <EventsTable events={allEvents} />
          </TabsContent>

          <TabsContent value="cultural" className="mt-0">
            <EventsTable events={culturalEvents} />
          </TabsContent>

          <TabsContent value="technical" className="mt-0">
            <EventsTable events={technicalEvents} />
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}

export const dynamic = "force-dynamic";

