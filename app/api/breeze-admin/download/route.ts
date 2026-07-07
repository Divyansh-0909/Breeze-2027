import { prisma } from "@/lib/prisma";
import { NextRequest, NextResponse } from "next/server";
import { requireBreezeAdmin } from "@/lib/auth";

function escapeCsvField(value: unknown): string {
    if (value === null || value === undefined) return "";
    const str = String(value);
    if (str.includes(",") || str.includes('"') || str.includes("\n")) {
        return `"${str.replace(/"/g, '""')}"`;
    }
    return str;
}

function toCsv(headers: string[], rows: unknown[][]): string {
    const headerLine = headers.map(escapeCsvField).join(",");
    const dataLines = rows.map((row) => row.map(escapeCsvField).join(","));
    return [headerLine, ...dataLines].join("\n");
}

function formatDate(date: Date | null | undefined): string {
    if (!date) return "";
    return new Date(date).toLocaleString("en-IN", { timeZone: "Asia/Kolkata" });
}

export async function GET(req: NextRequest) {
    const adminCheck = await requireBreezeAdmin();
    if (adminCheck.authorized === false) return adminCheck.response;

    const type = req.nextUrl.searchParams.get("type");

    if (!type) {
        return NextResponse.json(
            { error: "Missing 'type' query parameter" },
            { status: 400 }
        );
    }

    let csv = "";
    let filename = "";

    try {
        switch (type) {
            case "transactions": {
                const data = await prisma.submittedTransaction.findMany({
                    orderBy: { created_at: "desc" },
                });
                const headers = [
                    "Token",
                    "Created At",
                    "Name",
                    "Email",
                    "Phone",
                    "Address",
                    "Amount",
                    "Approved",
                    "Rejected",
                    "Rejection Reason",
                    "Email Sent",
                    "Accommodation",
                    "Accommodation Price",
                    "Student Details",
                    "Cart (JSON)",
                ];
                const rows = data.map((t) => [
                    t.token,
                    formatDate(t.created_at),
                    t.name,
                    t.email,
                    t.phone,
                    t.address,
                    t.amount.toString(),
                    t.approved ? "Yes" : "No",
                    t.rejected ? "Yes" : "No",
                    t.rejection_reason || "",
                    t.email_sent ? "Yes" : "No",
                    t.accommodation.join(", "),
                    t.accommodation_price.toString(),
                    t.student_details || "",
                    JSON.stringify(t.cart),
                ]);
                csv = toCsv(headers, rows);
                filename = "transactions.csv";
                break;
            }

            case "approved-transactions": {
                const data = await prisma.submittedTransaction.findMany({
                    where: { approved: true },
                    orderBy: { created_at: "desc" },
                });
                const headers = [
                    "Token",
                    "Created At",
                    "Name",
                    "Email",
                    "Phone",
                    "Address",
                    "Amount",
                    "Accommodation",
                    "Accommodation Price",
                    "Student Details",
                    "Cart (JSON)",
                ];
                const rows = data.map((t) => [
                    t.token,
                    formatDate(t.created_at),
                    t.name,
                    t.email,
                    t.phone,
                    t.address,
                    t.amount.toString(),
                    t.accommodation.join(", "),
                    t.accommodation_price.toString(),
                    t.student_details || "",
                    JSON.stringify(t.cart),
                ]);
                csv = toCsv(headers, rows);
                filename = "approved-transactions.csv";
                break;
            }

            case "events": {
                const data = await prisma.eventItem.findMany({
                    orderBy: { created_at: "desc" },
                });
                const headers = [
                    "ID",
                    "Created At",
                    "Event Name",
                    "Description",
                    "Price",
                    "Pair Price",
                    "Organizer",
                    "Venue",
                    "Date",
                    "End Date",
                    "Type",
                    "Registration Open",
                ];
                const rows = data.map((e) => [
                    e.id,
                    formatDate(e.created_at),
                    e.event_name,
                    e.event_description,
                    e.event_price,
                    e.event_pair_price ?? "",
                    e.event_org || "",
                    e.event_venue || "",
                    e.event_date || "",
                    e.event_end_date || "",
                    e.event_type || "",
                    e.registration_open ? "Yes" : "No",
                ]);
                csv = toCsv(headers, rows);
                filename = "events.csv";
                break;
            }

            case "merch": {
                const data = await prisma.merchItem.findMany({
                    orderBy: { created_at: "desc" },
                });
                const headers = [
                    "ID",
                    "Created At",
                    "Product Name",
                    "Price",
                    "Description",
                    "Image URL",
                ];
                const rows = data.map((m) => [
                    m.id,
                    formatDate(m.created_at),
                    m.product_name,
                    m.product_price,
                    m.product_description,
                    m.image_url || "",
                ]);
                csv = toCsv(headers, rows);
                filename = "merch.csv";
                break;
            }

            case "contacts": {
                const data = await prisma.contactSubmission.findMany({
                    orderBy: { created_at: "desc" },
                });
                const headers = ["ID", "Created At", "Name", "Email", "Phone", "Message"];
                const rows = data.map((c) => [
                    c.id,
                    formatDate(c.created_at),
                    c.name,
                    c.email,
                    c.phone,
                    c.message,
                ]);
                csv = toCsv(headers, rows);
                filename = "contacts.csv";
                break;
            }

            case "users": {
                const data = await prisma.roles.findMany();
                const headers = ["ID", "Club Name", "Email"];
                const rows = data.map((r) => [r.id, r.club_name, r.email]);
                csv = toCsv(headers, rows);
                filename = "users.csv";
                break;
            }

            case "attendees": {
                const confirmedEvents = await prisma.confirmedEvent.findMany({
                    include: {
                        EventItem: true,
                        SubmittedTransaction: true,
                    },
                });
                const headers = [
                    "Event Name",
                    "Event Date",
                    "Event Type",
                    "Attendee Name",
                    "Email",
                    "Phone",
                    "Ticket Quantity",
                    "Transaction Token",
                    "Student Details",
                ];
                const rows = confirmedEvents.map((ce) => [
                    ce.EventItem.event_name,
                    ce.EventItem.event_date || "",
                    ce.EventItem.event_type || "",
                    ce.SubmittedTransaction.name,
                    ce.SubmittedTransaction.email,
                    ce.SubmittedTransaction.phone,
                    ce.quantity.toString(),
                    ce.token,
                    ce.SubmittedTransaction.student_details || "",
                ]);
                csv = toCsv(headers, rows);
                filename = "event-attendees.csv";
                break;
            }

            case "merch-orders": {
                const confirmedMerch = await prisma.confirmedMerch.findMany({
                    include: {
                        MerchItem: true,
                        SubmittedTransaction: true,
                    },
                });
                const headers = [
                    "Product Name",
                    "Size",
                    "Quantity",
                    "Buyer Name",
                    "Email",
                    "Phone",
                    "Address",
                    "Transaction Token",
                ];
                const rows = confirmedMerch.map((cm) => [
                    cm.MerchItem.product_name,
                    cm.size,
                    cm.quantity.toString(),
                    cm.SubmittedTransaction.name,
                    cm.SubmittedTransaction.email,
                    cm.SubmittedTransaction.phone,
                    cm.SubmittedTransaction.address,
                    cm.token,
                ]);
                csv = toCsv(headers, rows);
                filename = "merch-orders.csv";
                break;
            }

            default:
                return NextResponse.json(
                    { error: `Unknown type: ${type}` },
                    { status: 400 }
                );
        }

        return new NextResponse(csv, {
            status: 200,
            headers: {
                "Content-Type": "text/csv; charset=utf-8",
                "Content-Disposition": `attachment; filename="${filename}"`,
            },
        });
    } catch (error) {
        console.error("Download error:", error);
        return NextResponse.json(
            { error: "Failed to generate CSV" },
            { status: 500 }
        );
    }
}
