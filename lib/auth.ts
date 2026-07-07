import { createClient } from "@/utils/supabase/server";
import { NextResponse } from "next/server";

export type AuthResult =
    | { authenticated: true; userId: string; clubName: string; isBreezeAdmin: boolean }
    | { authenticated: false; response: NextResponse };

/**
 * Verify user authentication and get their role.
 * Returns user info if authenticated, or a NextResponse error if not.
 * 
 * Usage in API routes:
 * ```
 * const auth = await verifyAuth();
 * if (!auth.authenticated) return auth.response;
 * // auth.userId, auth.clubName, auth.isBreezeAdmin are now available
 * ```
 */
export async function verifyAuth(): Promise<AuthResult> {
    try {
        const supabase = await createClient();
        const { data: { user }, error: authError } = await supabase.auth.getUser();

        if (authError || !user) {
            return {
                authenticated: false,
                response: NextResponse.json(
                    { error: "Unauthorized" },
                    { status: 401 }
                ),
            };
        }

        const { data: role, error: roleError } = await supabase
            .from("Roles")
            .select("club_name")
            .eq("id", user.id)
            .single();

        if (roleError || !role) {
            return {
                authenticated: false,
                response: NextResponse.json(
                    { error: "No role assigned" },
                    { status: 403 }
                ),
            };
        }

        return {
            authenticated: true,
            userId: user.id,
            clubName: role.club_name,
            isBreezeAdmin: role.club_name === "BREEZE",
        };
    } catch {
        return {
            authenticated: false,
            response: NextResponse.json(
                { error: "Authentication failed" },
                { status: 500 }
            ),
        };
    }
}

/**
 * Require BREEZE admin access. Returns error response if not admin.
 * 
 * Usage:
 * ```
 * const adminCheck = await requireBreezeAdmin();
 * if (!adminCheck.authorized) return adminCheck.response;
 * ```
 */
export async function requireBreezeAdmin(): Promise<
    | { authorized: true; userId: string }
    | { authorized: false; response: NextResponse }
> {
    const auth = await verifyAuth();

    if (auth.authenticated === false) {
        return { authorized: false, response: auth.response };
    }

    if (!auth.isBreezeAdmin) {
        return {
            authorized: false,
            response: NextResponse.json(
                { error: "Forbidden: BREEZE admin access required" },
                { status: 403 }
            ),
        };
    }

    return { authorized: true, userId: auth.userId };
}
