import { prisma } from "@/lib/prisma";
import { accommodation_option } from "@prisma/client";
import { Metadata } from "next";

export const metadata: Metadata = {
  title: "Receipt - Breeze '26",
};
type CartItem = {
  [key: string]: {
    [sizeOrTicketType: string]: number;
  };
};

export default async function Page({
  params,
}: {
  params: Promise<{ token: string }>;
}) {
  const events = await prisma.eventItem.findMany({
    select: { id: true, event_name: true, event_price: true, event_pair_price: true },
  });
  const merch = await prisma.merchItem.findMany();

  const eventsMap = events.reduce((acc, event) => {
    acc[event.id] = event;
    return acc;
  }, {} as Record<string, (typeof events)[0]>);

  const merchMap = merch.reduce((acc, item) => {
    acc[item.id] = item;
    return acc;
  }, {} as Record<string, (typeof merch)[0]>);
  const transaction = await prisma.submittedTransaction.findUnique({
    where: { token: (await params).token, approved: true },
  });

  if (!transaction) {
    return (
      <div className="flex items-center justify-center h-screen text-foreground text-xl">
        Transaction not found
      </div>
    );
  }

  return (
    <div className="flex flex-col items-center justify-center min-h-screen pt-10 p-4">
      <h1 className="text-center mt-12">
        Dear {transaction.name},<br /> Thank you for your transaction. Please
        find attached the reciept below. Please do not share this link with
        anyone.
      </h1>
      <div className="rounded-lg p-8 max-w-md w-full space-y-6">
        <h1 className="text-2xl font-bold text-center mb-6 text-primary">
          Receipt
        </h1>
        <div className="flex justify-between items-center">
          <div className="space-y-1">
            <h2 className="text-lg font-semibold text-foreground">
              {transaction.name}
            </h2>
            <p className="text-sm text-muted-foreground">{transaction.email}</p>
          </div>
          <div className="px-1 space-y-1">
            <p className="text-sm text-muted-foreground">
                {new Date(transaction.created_at).toLocaleString('en-IN', {
                hour: '2-digit',
                minute: '2-digit',
                hour12: false,
                day: 'numeric',
                month: 'short',
                year: 'numeric'
                })}
            </p>
          </div>
        </div>
        <div className="space-y-4 divide-y divide-foreground">
          {Object.entries(transaction.cart as unknown as CartItem).flatMap(
            ([id, sizes]) => {
              if (merchMap[id]) {
                return Object.entries(sizes).map(([size, quantity]) => (
                  <div
                    key={id + size}
                    className="flex justify-between items-center pt-4"
                  >
                    <div className="space-y-1">
                      <h2 className="text-lg font-semibold text-foreground">
                        {merchMap[id].product_name}
                      </h2>
                      <p className="text-sm text-muted-foreground">
                        Size: {size}
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="text-sm text-muted-foreground">
                        x{quantity}
                      </p>
                      <p className="text-lg font-medium">
                        ₹{(merchMap[id].product_price * quantity).toFixed(2)}
                      </p>
                    </div>
                  </div>
                ));
              } else if (eventsMap[id]) {
                return Object.entries(sizes).map(([ticketType, quantity]) => {
                  const isPair = ticketType === "PAIR";
                  const price = isPair ? (eventsMap[id].event_pair_price || eventsMap[id].event_price) : eventsMap[id].event_price;
                  return (
                    <div
                      key={id + ticketType}
                      className="flex justify-between items-center pt-4"
                    >
                      <div className="space-y-1">
                        <h2 className="text-lg font-semibold text-foreground">
                          {eventsMap[id].event_name}
                        </h2>
                        <p className="text-sm text-muted-foreground">
                          {isPair ? "Pair Ticket" : "Single Ticket"}
                        </p>
                      </div>
                      <div className="text-right">
                        <p className="text-sm text-muted-foreground">
                          x{quantity}
                        </p>
                        <p className="text-lg font-medium">
                          ₹{(price * quantity).toFixed(2)}
                        </p>
                      </div>
                    </div>
                  );
                });
              }
            }
          )}
          {transaction.accommodation && transaction.accommodation.length>0 && (
            <div className="border-b">
              <h4 className="mt-4 text-lg mb-2">
                Accommodation Details
              </h4>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <div className="flex flex-col space-y-2">
                    <span className="text-sm font-medium">Package Type:</span>
                    <div className="flex flex-wrap gap-2">
                      {transaction.accommodation.map(
                        (day: accommodation_option, i) => (
                          <span
                            className="bg-primary text-white px-3 py-1 rounded-md"
                            key={i}
                          >
                            {day.toString().slice(0, 3) +
                              " " +
                              day.toString()[3]}
                          </span>
                        )
                      )}
                    </div>
                  </div>
                  <span className="text-lg font-medium">
                    ₹{Number(transaction.accommodation_price)}
                  </span>
                </div>
              </div>
            </div>
          )}
        </div>

        <div className="pt-6 mt-6 border-t border-foreground">
          <div className="flex justify-between items-center">
            <span className="text-lg font-semibold">Total</span>
            <span className="text-xl font-bold text-primary">
              ₹{Number(transaction.amount).toFixed(2)}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
