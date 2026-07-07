import { NextRequest, NextResponse } from "next/server";
import { prisma } from "@/lib/prisma";
import * as z from "zod";

const contactSchema = z.object({
    name: z.string().min(2),
    email: z.string().email(),
    phone: z.string().min(10),
    message: z.string().min(10),
});

export async function POST(req: NextRequest) {
    try {
        const body = await req.json();
        const validatedData = contactSchema.parse(body);

        await prisma.contactSubmission.create({
            data: {
                name: validatedData.name,
                email: validatedData.email,
                phone: validatedData.phone,
                message: validatedData.message,
            },
        });

        return NextResponse.json(
            { success: true, message: "Contact form submitted successfully" },
            { status: 200 }
        );
    } catch (error) {
        console.error("Contact API Error:", error);

        if (error instanceof z.ZodError) {
            return NextResponse.json(
                { success: false, errors: error.errors },
                { status: 400 }
            );
        }

        return NextResponse.json(
            { success: false, error: "Failed to submit contact form" },
            { status: 500 }
        );
    }
}

export async function GET() {
    try {
        const submissions = await prisma.contactSubmission.findMany({
            orderBy: { created_at: "desc" },
        });

        return NextResponse.json(submissions);
    } catch (error) {
        console.error("Contact GET Error:", error);
        return NextResponse.json(
            { success: false, error: "Failed to fetch submissions" },
            { status: 500 }
        );
    }
}
