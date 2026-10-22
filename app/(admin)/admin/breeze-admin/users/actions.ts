"use server";

import { createAdminClient } from "@/utils/supabase/admin";
import { prisma } from "@/lib/prisma";
import { requireBreezeAdmin } from "@/lib/auth";

export async function addUser(
  newEmail: string,
  newPassword: string,
  newRole: string
) {
  const adminCheck = await requireBreezeAdmin();
  if (adminCheck.authorized === false) {
    return false;
  }

  try {
    const adminSupabase = createAdminClient();
    const normalizedEmail = newEmail.trim().toLowerCase();
    const normalizedRole = newRole.trim().toUpperCase();

    const { data, error } = await adminSupabase.auth.admin.createUser({
      email: normalizedEmail,
      password: newPassword,
      email_confirm: true,
    });

    if (error || !data.user) {
      console.error("Error creating user:", error);
      return false;
    }

    await prisma.roles.upsert({
      where: { id: data.user.id },
      update: {
        email: normalizedEmail,
        club_name: normalizedRole,
      },
      create: {
        id: data.user.id,
        email: normalizedEmail,
        club_name: normalizedRole,
      },
    });

    return true;
  } catch (err) {
    console.error("addUser error:", err);
    return false;
  }
}

export async function deleteUser(userId: string) {
  const adminCheck = await requireBreezeAdmin();
  if (adminCheck.authorized === false) {
    return false;
  }

  try {
    const adminSupabase = createAdminClient();
    await adminSupabase.auth.admin.deleteUser(userId);
    await prisma.roles.delete({ where: { id: userId } });
    return true;
  } catch (err) {
    console.error("deleteUser error:", err);
    return false;
  }
}


