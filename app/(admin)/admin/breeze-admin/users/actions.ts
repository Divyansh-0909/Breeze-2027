"use server";

import { createClient } from "@/utils/supabase/server";
import { prisma } from "@/lib/prisma";
import { requireBreezeAdmin } from "@/lib/auth";

export async function addUser(
  newEmail: string,
  newPassword: string,
  newRole: string
) {
  // Verify BREEZE admin access
  const adminCheck = await requireBreezeAdmin();
  if (adminCheck.authorized === false) {
    return false;
  }

  const supabase = await createClient();
  const { data, error } = await supabase.auth.signUp({ email: newEmail, password: newPassword, phone: "" })
  if (error) {
    console.log(error);
    return false;
  }
  if (data) {
    await prisma.roles.create({
      data: {
        id: data.user.id,
        email: newEmail,
        club_name: newRole.toUpperCase(),
      },
    });
    return true;
  }
  return false;
}

export async function deleteUser(userId: string) {
  // Verify BREEZE admin access
  const adminCheck = await requireBreezeAdmin();
  if (adminCheck.authorized === false) {
    return false;
  }

  try {
    await prisma.roles.delete({ where: { id: userId } });
    return true;
  } catch {
    return false;
  }
}

