import { createServerClient } from "@supabase/ssr";
import { NextResponse, type NextRequest } from "next/server";

export async function updateSession(request: NextRequest) {
  let supabaseResponse = NextResponse.next({
    request,
  });

  const supabase = createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: {
        getAll() {
          return request.cookies.getAll();
        },
        setAll(cookiesToSet) {
          cookiesToSet.forEach(({ name, value, options }) =>
            request.cookies.set(name, value)
          );
          supabaseResponse = NextResponse.next({
            request,
          });
          cookiesToSet.forEach(({ name, value, options }) =>
            supabaseResponse.cookies.set(name, value, options)
          );
        },
      },
    }
  );

  // IMPORTANT: Avoid writing any logic between createServerClient and
  // supabase.auth.getUser(). A simple mistake could make it very hard to debug
  // issues with users being randomly logged out.

  const {
    data: { user },
  } = await supabase.auth.getUser();
  const isLoginRoute = request.nextUrl.pathname.startsWith("/admin/login");

  if (!user && !isLoginRoute) {
    const url = request.nextUrl.clone();
    url.pathname = "/admin/login";
    return NextResponse.redirect(url);
  }

  if (user) {
    let clubName: string | null = null;

    // Check role by ID first
    const { data: roleById } = await supabase
      .from("Roles")
      .select("club_name")
      .eq("id", user.id)
      .maybeSingle();

    if (roleById?.club_name) {
      clubName = roleById.club_name;
    } else if (user.email) {
      // Fallback to checking role by email (case-insensitive)
      const { data: roleByEmail } = await supabase
        .from("Roles")
        .select("club_name")
        .ilike("email", user.email)
        .maybeSingle();
      if (roleByEmail?.club_name) {
        clubName = roleByEmail.club_name;
      }
    }

    // If user is already logged in and attempts to access /admin/login
    if (isLoginRoute) {
      const url = request.nextUrl.clone();
      if (clubName === "BREEZE") {
        url.pathname = "/admin/breeze-admin";
        return NextResponse.redirect(url);
      } else if (clubName) {
        url.pathname = "/admin/clubs";
        return NextResponse.redirect(url);
      }
    }

    // If user has no assigned role, prevent access to protected admin portals
    if (!clubName && !isLoginRoute) {
      const url = request.nextUrl.clone();
      url.pathname = "/admin/login";
      url.searchParams.set("error", "no_role");
      return NextResponse.redirect(url);
    }

    // If a club user tries to access BREEZE admin routes
    if (
      clubName !== "BREEZE" &&
      (request.nextUrl.pathname.startsWith("/admin/breeze-admin") ||
        request.nextUrl.pathname.startsWith("/api/breeze-admin"))
    ) {
      const url = request.nextUrl.clone();
      url.pathname = "/admin/clubs";
      return NextResponse.redirect(url);
    }
  }
  // IMPORTANT: You *must* return the supabaseResponse object as it is. If you're
  // creating a new response object with NextResponse.next() make sure to:
  // 1. Pass the request in it, like so:
  //    const myNewResponse = NextResponse.next({ request })
  // 2. Copy over the cookies, like so:
  //    myNewResponse.cookies.setAll(supabaseResponse.cookies.getAll())
  // 3. Change the myNewResponse object to fit your needs, but avoid changing
  //    the cookies!
  // 4. Finally:
  //    return myNewResponse
  // If this is not done, you may be causing the browser and server to go out
  // of sync and terminate the user's session prematurely!

  return supabaseResponse;
}
