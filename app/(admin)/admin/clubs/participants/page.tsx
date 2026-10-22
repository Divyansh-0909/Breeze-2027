import { prisma } from "@/lib/prisma";
import { createClient } from "@/utils/supabase/server";

export const dynamic = "force-dynamic";

export default async function Page() {
  try {
    const supabase = await createClient();
    const { data: { user } } = await supabase.auth.getUser();
    const curr_club = await prisma.roles.findFirst({
      where: { email: user?.email || "" },
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
  });

  // Fetch ALL confirmed events for this club in a single query
  const allConfirmedEvents = await prisma.confirmedEvent.findMany({
    where: {
      EventItem: {
        event_org: curr_club.club_name,
      },
    },
    include: { SubmittedTransaction: true },
  });

  // Group confirmed events by eventItemId
  const confirmedByEvent = new Map<string, typeof allConfirmedEvents>();
  for (const ce of allConfirmedEvents) {
    const key = ce.id;
    if (!confirmedByEvent.has(key)) {
      confirmedByEvent.set(key, []);
    }
    confirmedByEvent.get(key)!.push(ce);
  }

  let grandTotal = 0;

  const eventData = events.map((event) => {
    const users = confirmedByEvent.get(event.id) || [];
    const eventTotal = users.reduce(
      (acc, user) =>
        acc + Number(user.quantity) * Number(event.event_price),
      0
    );
    grandTotal += eventTotal;
    return { event, users, eventTotal };
  });

  return (
    <div className="px-8 py-6 max-w-[1200px]">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-[18px] font-semibold tracking-[-0.02em]" style={{ color: '#e5e5e5' }}>
          Participants
        </h1>
        <p className="text-[13px] mt-0.5" style={{ color: '#666' }}>
          Registered participants and revenue per event
        </p>
      </div>

      {/* Summary card */}
      <div className="flex items-center gap-6 mb-6 px-4 py-3 rounded-lg" style={{ background: '#141414', border: '1px solid #1e1e1e' }}>
        <div>
          <p className="text-[11px] font-medium uppercase tracking-wider" style={{ color: '#555' }}>Total Events</p>
          <p className="text-[20px] font-semibold" style={{ color: '#e5e5e5' }}>{eventData.length}</p>
        </div>
        <div className="w-px h-8" style={{ background: '#1e1e1e' }} />
        <div>
          <p className="text-[11px] font-medium uppercase tracking-wider" style={{ color: '#555' }}>Total Revenue</p>
          <p className="text-[20px] font-semibold" style={{ color: '#34d399' }}>₹{grandTotal.toLocaleString()}</p>
        </div>
        <div className="w-px h-8" style={{ background: '#1e1e1e' }} />
        <div>
          <p className="text-[11px] font-medium uppercase tracking-wider" style={{ color: '#555' }}>Total Registrations</p>
          <p className="text-[20px] font-semibold" style={{ color: '#e5e5e5' }}>
            {eventData.reduce((sum, d) => sum + d.users.length, 0)}
          </p>
        </div>
      </div>

      {/* Events list */}
      <div className="space-y-4">
        {eventData.map(({ event, users, eventTotal }) => (
          <div key={event.id} className="rounded-lg overflow-hidden" style={{ border: '1px solid #1e1e1e' }}>
            {/* Event header */}
            <div className="flex items-center justify-between px-4 py-3" style={{ background: '#141414', borderBottom: '1px solid #1e1e1e' }}>
              <div className="flex items-center gap-3">
                <h3 className="text-[14px] font-medium" style={{ color: '#e5e5e5' }}>
                  {event.event_name}
                </h3>
                <span className="text-[11px] px-2 py-0.5 rounded-full font-medium" style={{ background: '#1a1a1a', color: '#888', border: '1px solid #262626' }}>
                  {users.length} participant{users.length !== 1 ? 's' : ''}
                </span>
              </div>
              <span className="text-[13px] font-medium" style={{ color: '#34d399' }}>
                ₹{eventTotal.toLocaleString()}
              </span>
            </div>

            {/* Participant table */}
            {users.length > 0 ? (
              <div>
                {/* Table header */}
                <div className="grid grid-cols-[1.5fr_1.5fr_1fr_1fr_1fr_0.8fr_0.8fr] gap-3 px-4 py-2 text-[11px] font-medium uppercase tracking-wider" style={{ color: '#555', borderBottom: '1px solid #1a1a1a' }}>
                  <div>Name</div>
                  <div>Email</div>
                  <div>Phone</div>
                  <div>Roll No.</div>
                  <div>College</div>
                  <div>Passes</div>
                  <div className="text-right">Value</div>
                </div>
                {/* Table rows */}
                {users.map((user) => (
                  <div
                    key={user.token}
                    className="grid grid-cols-[1.5fr_1.5fr_1fr_1fr_1fr_0.8fr_0.8fr] gap-3 px-4 py-2.5 text-[13px] transition-colors duration-75"
                    style={{ borderBottom: '1px solid #141414' }}
                    onMouseEnter={(e) => { e.currentTarget.style.background = '#111'; }}
                    onMouseLeave={(e) => { e.currentTarget.style.background = 'transparent'; }}
                  >
                    <div className="font-medium truncate" style={{ color: '#e5e5e5' }}>{user.SubmittedTransaction.name}</div>
                    <div className="truncate" style={{ color: '#888' }}>{user.SubmittedTransaction.email}</div>
                    <div style={{ color: '#888' }}>{user.SubmittedTransaction.phone}</div>
                    <div style={{ color: '#888' }}>{user.SubmittedTransaction.address}</div>
                    <div className="truncate" style={{ color: '#666' }}>{user.SubmittedTransaction.student_details || "-"}</div>
                    <div style={{ color: '#e5e5e5' }}>{Number(user.quantity)}</div>
                    <div className="text-right font-medium" style={{ color: '#e5e5e5' }}>₹{Number(user.quantity) * Number(event.event_price)}</div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="px-4 py-8 text-center">
                <p className="text-[13px]" style={{ color: '#555' }}>No participants yet</p>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
  } catch (error) {
    console.error("Error loading club participants:", error);
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
            href="/admin/clubs/participants"
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
