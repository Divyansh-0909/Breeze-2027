import { prisma } from "@/lib/prisma";
import { createClient } from "@/utils/supabase/server";
import EventTable from "./event-table";

export const dynamic = "force-dynamic";

export default async function Page() {
  const supabase = await createClient();
  const user = await supabase.auth.getUser();
  const curr_club = await prisma.roles.findFirst({
    where: { email: user.data.user.email },
  });
  const events = await prisma.eventItem.findMany({
    where: { event_org: curr_club.club_name },
  });
  return (
    <div className="min-h-screen bg-white">
      <div className="container mx-auto px-6 py-12 space-y-8">
        <div className="mb-12">
          <h1 className="text-4xl font-bold text-[#202020] tracking-tight mb-2">
            All events for {curr_club.club_name}
          </h1>
          <p className="text-gray-500 text-sm">
            View your club's events and manage registrations
          </p>
        </div>
        <EventTable curr_club={curr_club} events={events} />
      </div>
    </div>
  );
}
