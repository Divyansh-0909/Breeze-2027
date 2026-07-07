"use client";
import { EventItem, Roles } from "@prisma/client";
import {
  Table,
  TableBody,
  TableCaption,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { toggleEventRegistration } from "./actions";
import { useTransition } from "react";
import { useRouter } from "next/navigation";
import { Switch } from "@/components/ui/switch";
import { Badge } from "@/components/ui/badge";

export default function EventTable({
  curr_club,
  events,
}: {
  curr_club: Roles;
  events: EventItem[];
}) {
  const [isPending, startTransition] = useTransition();
  const router = useRouter();

  return (
    <Table className="border rounded-lg">
      <TableCaption className="text-lg font-medium mb-4">
        Event List
      </TableCaption>
      <TableHeader>
        <TableRow className="bg-gray-50">
          <TableHead className="font-semibold">Event Name</TableHead>
          <TableHead className="font-semibold">Description</TableHead>
          <TableHead className="font-semibold">Price</TableHead>
          <TableHead className="font-semibold">Venue</TableHead>
          <TableHead className="font-semibold">Date</TableHead>
          <TableHead className="font-semibold">Registration</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {events.length > 0 ? (
          events.map((event) => (
            <TableRow key={event.id} className="hover:bg-gray-50">
              <TableCell className="font-medium">
                {event.event_name}
              </TableCell>
              <TableCell className="max-w-xs truncate">
                {event.event_description}
              </TableCell>
              <TableCell>
                <div className="flex flex-col">
                  <span>₹{event.event_price}</span>
                  {event.event_pair_price && (
                    <span className="text-xs text-gray-500">
                      Pair: ₹{event.event_pair_price}
                    </span>
                  )}
                </div>
              </TableCell>
              <TableCell>{event.event_venue}</TableCell>
              <TableCell>
                <div className="flex flex-col">
                  <span>{event.event_date}</span>
                  {event.event_end_date && (
                    <span className="text-xs text-gray-500">
                      to {event.event_end_date}
                    </span>
                  )}
                </div>
              </TableCell>
              <TableCell>
                <div className="flex items-center gap-2">
                  <Switch
                    checked={event.registration_open}
                    disabled={isPending}
                    className="data-[state=checked]:bg-green-600 data-[state=unchecked]:bg-red-500 [&>span]:bg-white"
                    onCheckedChange={(checked) => {
                      startTransition(async () => {
                        await toggleEventRegistration(event.id, checked);
                        router.refresh();
                      });
                    }}
                  />
                  <Badge
                    variant={
                      event.registration_open ? "default" : "destructive"
                    }
                  >
                    {event.registration_open ? "Open" : "Closed"}
                  </Badge>
                </div>
              </TableCell>
            </TableRow>
          ))
        ) : (
          <TableRow>
            <TableCell
              colSpan={6}
              className="text-center text-muted-foreground py-8"
            >
              No events found
            </TableCell>
          </TableRow>
        )}
      </TableBody>
    </Table>
  );
}
