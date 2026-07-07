"use server"

import { prisma } from "@/lib/prisma";
import { revalidatePath } from "next/cache";
import { createClient } from "@/utils/supabase/server";
import { requireBreezeAdmin } from "@/lib/auth";

export async function createEvent(formData: FormData) {
  // Verify BREEZE admin access
  const adminCheck = await requireBreezeAdmin();
  if (adminCheck.authorized === false) {
    return { success: false, error: "Unauthorized" };
  }

  try {
    const supabase = await createClient();
    const eventPoster = formData.get("event_poster") as File;

    if (!eventPoster || eventPoster.size === 0) {
      return { success: false, error: "Event poster is required" };
    }

    const { data, error } = await supabase.storage
      .from("assets")
      .upload(`${Date.now()}_${eventPoster.name}`, eventPoster);

    if (error) {
      return { success: false, error: "Failed to upload image" };
    }

    // Get the public URL for the uploaded image
    const { data: publicUrlData } = supabase.storage.from("assets").getPublicUrl(data.path);

    const eventData = {
      event_name: formData.get("event_name"),
      event_description: formData.get("event_description"),
      event_price: Number(formData.get("event_price")),
      event_venue: formData.get("event_venue"),
      event_date: formData.get("event_date"),
      event_org: formData.get("event_org"),
      event_type: formData.get("event_type"),
      event_end_date: formData.get("event_end_date") || null,
      event_pair_price: formData.get("event_pair_price") ? Number(formData.get("event_pair_price")) : null,
    };

    await prisma.eventItem.create({
      data: {
        event_name: eventData.event_name?.toString() || "",
        event_description: eventData.event_description?.toString() || "",
        event_price: eventData.event_price,
        event_org: eventData.event_org?.toString() || "",
        event_date: eventData.event_date?.toString() || "",
        event_venue: eventData.event_venue?.toString() || "",
        event_type: eventData.event_type as "Cultural" | "Technical",
        image_url: publicUrlData.publicUrl,
        registration_open: true,
        event_end_date: eventData.event_end_date?.toString() || null,
        event_pair_price: eventData.event_pair_price,
      },
    });

    revalidatePath("/admin/breeze-admin/events");
    revalidatePath("/admin/clubs");
    revalidatePath("/events");
    return { success: true };
  } catch (error) {
    console.error("Failed to create event:", error);
    return { success: false, error: "Failed to create event" };
  }
}


export async function toggleEventRegistration(eventId: string, registrationOpen: boolean) {
  // Verify BREEZE admin access
  const adminCheck = await requireBreezeAdmin();
  if (adminCheck.authorized === false) {
    return { success: false, error: "Unauthorized" };
  }

  try {
    await prisma.eventItem.update({
      where: { id: eventId },
      data: { registration_open: registrationOpen },
    });
    revalidatePath("/admin/breeze-admin/events");
    revalidatePath("/admin/clubs");
    revalidatePath("/events");
    return { success: true };
  } catch (error) {
    return { success: false, error: "Failed to toggle registration" };
  }
}

export async function updateEvent(eventId: string, formData: FormData) {
  // Verify BREEZE admin access
  const adminCheck = await requireBreezeAdmin();
  if (adminCheck.authorized === false) {
    return { success: false, error: "Unauthorized" };
  }

  try {
    const supabase = await createClient();

    // Check if a new image file was provided
    const eventPoster = formData.get("event_poster") as File;
    let imageUrl: string | undefined = undefined;

    if (eventPoster && eventPoster.size > 0) {
      // Upload new image
      const { data, error } = await supabase.storage
        .from("assets")
        .upload(`${Date.now()}_${eventPoster.name}`, eventPoster);

      if (error) {
        return { success: false, error: "Failed to upload image" };
      }

      // Get the public URL for the uploaded image
      const { data: publicUrlData } = supabase.storage.from("assets").getPublicUrl(data.path);
      imageUrl = publicUrlData.publicUrl;
    }

    const eventData = {
      event_name: formData.get("event_name"),
      event_description: formData.get("event_description"),
      event_price: Number(formData.get("event_price")),
      event_venue: formData.get("event_venue"),
      event_date: formData.get("event_date"),
      event_org: formData.get("event_org"),
      event_type: formData.get("event_type") as "Cultural" | "Technical",
      event_end_date: formData.get("event_end_date") || null,
      event_pair_price: formData.get("event_pair_price") ? Number(formData.get("event_pair_price")) : null,
    };

    await prisma.eventItem.update({
      where: { id: eventId },
      data: {
        event_name: eventData.event_name?.toString() || "",
        event_description: eventData.event_description?.toString() || "",
        event_price: eventData.event_price,
        event_org: eventData.event_org?.toString() || "",
        event_venue: eventData.event_venue?.toString() || "",
        event_date: eventData.event_date?.toString() || "",
        event_type: eventData.event_type,
        event_end_date: eventData.event_end_date?.toString() || null,
        event_pair_price: eventData.event_pair_price,
        // Only update image_url if a new image was uploaded
        ...(imageUrl && { image_url: imageUrl }),
      },
    });

    revalidatePath("/admin/breeze-admin/events");
    revalidatePath("/admin/clubs");
    revalidatePath("/events");
    return { success: true };
  } catch (error) {
    console.error("Failed to update event:", error);
    return { success: false, error: "Failed to update event" };
  }
}

export async function deleteEvent(eventId: string) {
  // Verify BREEZE admin access
  const adminCheck = await requireBreezeAdmin();
  if (adminCheck.authorized === false) {
    return { success: false, error: "Unauthorized" };
  }

  try {
    await prisma.eventItem.delete({
      where: { id: eventId },
    });
    revalidatePath("/admin/breeze-admin/events");
    revalidatePath("/admin/clubs");
    revalidatePath("/events");
    return { success: true };
  } catch (error) {
    return { success: false, error: "Failed to delete event" };
  }
}
