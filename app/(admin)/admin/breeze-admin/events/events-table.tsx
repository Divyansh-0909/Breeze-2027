"use client";
import { EventItem } from "@prisma/client";
import {
  Table,
  TableBody,
  TableCaption,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import { deleteEvent, toggleEventRegistration } from "./actions";
import { Button } from "@/components/ui/button";
import { useTransition } from "react";
import { useRouter } from "next/navigation";
import { EditEventDialog } from "./edit-event-dialog";
import { useState } from "react";
import { Switch } from "@/components/ui/switch";
import { Badge } from "@/components/ui/badge";

export default function EventsTable({ events }: { events: EventItem[] }) {
  const [isPending, startTransition] = useTransition();
  const router = useRouter();
  const [selectedEvent, setSelectedEvent] = useState<EventItem | null>(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [eventToDelete, setEventToDelete] = useState<EventItem | null>(null);

  return (
    <>
      <Table className="border rounded-lg">
        <TableCaption className="text-lg font-medium mb-4">
          Event List - {events.length} events
        </TableCaption>
        <TableHeader>
          <TableRow className="bg-gray-50">
            <TableHead className="font-semibold">Event Name</TableHead>
            <TableHead className="font-semibold">Club</TableHead>
            <TableHead className="font-semibold">Type</TableHead>
            <TableHead className="font-semibold">Price</TableHead>
            <TableHead className="font-semibold">Date</TableHead>
            <TableHead className="font-semibold">Registration</TableHead>
            <TableHead className="font-semibold">Actions</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {events.length > 0 ? (
            events.map((event) => (
              <TableRow key={event.id} className="hover:bg-gray-50">
                <TableCell className="font-medium max-w-[200px] truncate">
                  {event.event_name}
                </TableCell>
                <TableCell>{event.event_org}</TableCell>
                <TableCell>
                  <Badge
                    variant={
                      event.event_type === "Cultural" ? "default" : "secondary"
                    }
                  >
                    {event.event_type}
                  </Badge>
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
                <TableCell>
                  <div className="flex gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => {
                        setSelectedEvent(event);
                        setDialogOpen(true);
                      }}
                    >
                      Edit
                    </Button>
                    <Button
                      variant="destructive"
                      size="sm"
                      disabled={isPending}
                      onClick={() => {
                        setEventToDelete(event);
                        setDeleteDialogOpen(true);
                      }}
                    >
                      Delete
                    </Button>
                  </div>
                </TableCell>
              </TableRow>
            ))
          ) : (
            <TableRow>
              <TableCell
                colSpan={7}
                className="text-center text-muted-foreground py-8"
              >
                No events found
              </TableCell>
            </TableRow>
          )}
        </TableBody>
      </Table>
      <EditEventDialog
        event={selectedEvent}
        open={dialogOpen}
        onOpenChange={setDialogOpen}
      />

      <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <AlertDialogContent className="bg-white">
          <AlertDialogHeader>
            <AlertDialogTitle>Delete Event</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete{" "}
              <strong>{eventToDelete?.event_name}</strong>? This action cannot
              be undone and will remove all associated registrations.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction
              className="bg-red-600 hover:bg-red-700"
              onClick={() => {
                if (eventToDelete) {
                  startTransition(async () => {
                    await deleteEvent(eventToDelete.id);
                    router.refresh();
                    setDeleteDialogOpen(false);
                    setEventToDelete(null);
                  });
                }
              }}
            >
              Delete Event
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </>
  );
}
