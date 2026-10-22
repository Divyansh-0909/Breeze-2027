import { prisma } from "@/lib/prisma";
import { createClient } from "@/utils/supabase/server";
import EventTable from "./event-table";
import AddEvent from "./add-event";

export const dynamic = "force-dynamic";

export default async function Page() {
  try {
    const supabase = await createClient();
    const user = await supabase.auth.getUser();
    const curr_club = await prisma.roles.findFirst({
      where: { email: user.data.user?.email || "" },
    });

    if (!curr_club) {
      return (
        <div className="flex items-center justify-center h-full min-h-[60vh]">
          <div className="text-center">
            <div className="inline-flex items-center justify-center w-10 h-10 rounded-lg mb-3" style={{ background: '#1a1a1a', border: '1px solid #262626' }}>
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#666" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <circle cx="12" cy="12" r="10" />
                <line x1="12" y1="8" x2="12" y2="12" />
                <line x1="12" y1="16" x2="12.01" y2="16" />
              </svg>
            </div>
            <h2 className="text-[14px] font-medium mb-1" style={{ color: '#e5e5e5' }}>Access Denied</h2>
            <p className="text-[13px]" style={{ color: '#666' }}>Your account is not assigned to any club role.</p>
          </div>
        </div>
      );
    }

    const events = await prisma.eventItem.findMany({
      where: { event_org: curr_club.club_name },
      orderBy: { created_at: "desc" },
    });

    return (
      <div className="px-8 py-6 max-w-[1200px]">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-[18px] font-semibold tracking-[-0.02em]" style={{ color: '#e5e5e5' }}>
              {curr_club.club_name}
            </h1>
            <p className="text-[13px] mt-0.5" style={{ color: '#666' }}>
              Manage your club&apos;s events and registrations
            </p>
          </div>
          <AddEvent curr_club={curr_club} />
        </div>

        {/* Events Table */}
        <EventTable curr_club={curr_club} events={events} />
      </div>
    );
  } catch (error) {
    console.error("Error loading club events:", error);
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
            href="/admin/clubs"
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
