import { prisma } from "@/lib/prisma";
import { createClient } from "@/utils/supabase/server";
import ClubEventsReadOnly from "./club-events-readonly";

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

    // Fetch club events (read-only)
    const events = await prisma.eventItem.findMany({
      where: { event_org: curr_club.club_name },
      orderBy: { created_at: "desc" },
    });

    // Fetch approved transactions that contain this club's events
    const eventIds = events.map((e) => e.id);

    // Get confirmed event entries for this club's events
    const confirmedEntries = await prisma.confirmedEvent.findMany({
      where: { id: { in: eventIds } },
      include: {
        SubmittedTransaction: true,
        EventItem: true,
      },
    });

    // Filter only approved transactions
    const approvedTransactions = confirmedEntries.filter(
      (ce) => ce.SubmittedTransaction.approved === true
    );

    // Calculate stats
    const totalTicketsSold = approvedTransactions.reduce(
      (sum, ce) => sum + Number(ce.quantity),
      0
    );

    const totalRevenue = approvedTransactions.reduce((sum, ce) => {
      const price = ce.EventItem.event_price;
      return sum + Number(ce.quantity) * price;
    }, 0);

    // Build unique approved transaction list for display
    const uniqueTransactionMap = new Map<string, {
      token: string;
      name: string;
      email: string;
      amount: number;
      created_at: Date;
      events: { name: string; quantity: number; price: number }[];
    }>();

    for (const ce of approvedTransactions) {
      const tx = ce.SubmittedTransaction;
      if (!uniqueTransactionMap.has(tx.token)) {
        uniqueTransactionMap.set(tx.token, {
          token: tx.token,
          name: tx.name,
          email: tx.email,
          amount: 0,
          created_at: tx.created_at,
          events: [],
        });
      }
      const entry = uniqueTransactionMap.get(tx.token)!;
      const eventPrice = ce.EventItem.event_price;
      entry.events.push({
        name: ce.EventItem.event_name,
        quantity: Number(ce.quantity),
        price: eventPrice,
      });
      entry.amount += Number(ce.quantity) * eventPrice;
    }

    const transactionsForDisplay = Array.from(uniqueTransactionMap.values())
      .sort((a, b) => b.created_at.getTime() - a.created_at.getTime());

    return (
      <ClubEventsReadOnly
        clubName={curr_club.club_name}
        events={events}
        totalTicketsSold={totalTicketsSold}
        totalRevenue={totalRevenue}
        approvedTransactions={transactionsForDisplay}
      />
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
