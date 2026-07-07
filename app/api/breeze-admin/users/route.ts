import { prisma } from "@/lib/prisma";
import { NextResponse } from "next/server";
import { requireBreezeAdmin } from "@/lib/auth";

export async function GET() {
    // Verify BREEZE admin access
    const adminCheck = await requireBreezeAdmin();
    if (adminCheck.authorized === false) return adminCheck.response;

    try {
        const data = await prisma.roles.findMany();
        return NextResponse.json({ data }, { status: 200 });
    } catch {
        return NextResponse.json({ error: "Failed to fetch roles" }, { status: 500 });
    }
}
