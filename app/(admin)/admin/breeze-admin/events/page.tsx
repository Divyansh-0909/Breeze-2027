import { prisma } from "@/lib/prisma";
import EventsTable from "./events-table";
import AddEvent from "./add-event";
import { mergeClubs } from "@/lib/clubs";

export default async function Page() {
  try {
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

    const dbClubs = await prisma.roles.findMany({
      select: { club_name: true },
    });

    const existingOrgs = allEvents
      .map((e) => e.event_org)
      .filter((org): org is string => Boolean(org));

    const uniqueClubs = mergeClubs([
      ...dbClubs.map((c) => c.club_name),
      ...existingOrgs,
    ]);

  return (
    <div className="px-8 py-6 max-w-[1200px]">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-[18px] font-semibold tracking-[-0.02em]" style={{ color: '#e5e5e5' }}>
            Events
          </h1>
          <p className="text-[13px] mt-0.5" style={{ color: '#666' }}>
            Manage all events across clubs
          </p>
        </div>
        <AddEvent clubs={uniqueClubs} />
      </div>

      {/* Stats */}
      <div className="flex items-center gap-6 mb-6 px-4 py-3 rounded-lg" style={{ background: '#141414', border: '1px solid #1e1e1e' }}>
        <div>
          <p className="text-[11px] font-medium uppercase tracking-wider" style={{ color: '#555' }}>All</p>
          <p className="text-[20px] font-semibold" style={{ color: '#e5e5e5' }}>{allEvents.length}</p>
        </div>
        <div className="w-px h-8" style={{ background: '#1e1e1e' }} />
        <div>
          <p className="text-[11px] font-medium uppercase tracking-wider" style={{ color: '#555' }}>Cultural</p>
          <p className="text-[20px] font-semibold" style={{ color: '#818cf8' }}>{culturalEvents.length}</p>
        </div>
        <div className="w-px h-8" style={{ background: '#1e1e1e' }} />
        <div>
          <p className="text-[11px] font-medium uppercase tracking-wider" style={{ color: '#555' }}>Technical</p>
          <p className="text-[20px] font-semibold" style={{ color: '#38bdf8' }}>{technicalEvents.length}</p>
        </div>
      </div>

      <EventsTable
        allEvents={allEvents}
        culturalEvents={culturalEvents}
        technicalEvents={technicalEvents}
      />
    </div>
  );
  } catch (error) {
    console.error("Error loading events:", error);
    return (
      <div className="px-8 py-16 max-w-[600px] mx-auto text-center">
        <div className="p-6 rounded-xl space-y-3" style={{ background: '#141414', border: '1px solid #262626' }}>
          <div className="w-10 h-10 rounded-full mx-auto flex items-center justify-center" style={{ background: '#1f1a1a', border: '1px solid #3b2828' }}>
            <span className="w-3 h-3 rounded-full bg-red-400" />
          </div>
          <h2 className="text-[16px] font-semibold" style={{ color: '#e5e5e5' }}>Database Connecting</h2>
          <p className="text-[13px]" style={{ color: '#888' }}>
            The database pooler is warming up. Please refresh the page in a few seconds.
          </p>
          <a
            href="/admin/breeze-admin/events"
            className="inline-block px-4 py-1.5 rounded-md text-[13px] font-medium transition-colors"
            style={{ background: '#e5e5e5', color: '#0a0a0a' }}
          >
            Retry Connection
          </a>
        </div>
      </div>
    );
  }
}

export const dynamic = "force-dynamic";
