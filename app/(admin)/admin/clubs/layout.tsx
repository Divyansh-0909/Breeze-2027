"use client";
import Link from "next/link";
import { createClient } from "@/utils/supabase/client";
import { useRouter, usePathname } from "next/navigation";
import { useEffect, useState } from "react";
import { LogOut, Calendar, Users, Loader2, Building2 } from "lucide-react";

export default function ClubLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const router = useRouter();
  const pathname = usePathname();
  const supabase = createClient();
  const [userEmail, setUserEmail] = useState<string>("");
  const [clubName, setClubName] = useState<string>("");
  const [navigatingHref, setNavigatingHref] = useState<string | null>(null);

  useEffect(() => {
    supabase.auth.getUser().then(async ({ data }) => {
      if (data?.user?.email) {
        setUserEmail(data.user.email);
        const { data: role } = await supabase
          .from("Roles")
          .select("club_name")
          .eq("id", data.user.id)
          .maybeSingle();
        if (role?.club_name) {
          setClubName(role.club_name);
        }
      }
    });
  }, [supabase]);

  useEffect(() => {
    setNavigatingHref(null);
  }, [pathname]);

  const handleLogout = async () => {
    await supabase.auth.signOut();
    router.push("/admin/login");
  };

  const navItems = [
    { href: "/admin/clubs", label: "Manage Events", icon: Calendar, exact: true },
    { href: "/admin/clubs/participants", label: "Participants", icon: Users },
  ];

  const isActive = (href: string, exact?: boolean) => {
    if (exact) return pathname === href;
    return pathname.startsWith(href);
  };

  return (
    <div className="flex min-h-screen" style={{ background: "#0a0a0a" }}>
      {/* Top Progress Loader on page change */}
      {navigatingHref && (
        <div className="fixed top-0 left-0 right-0 z-[999] h-[2px] bg-gradient-to-r from-neutral-500 via-white to-neutral-300 animate-pulse" />
      )}

      {/* Sidebar */}
      <aside
        className="w-[240px] flex flex-col shrink-0 sticky top-0 h-screen select-none"
        style={{ background: "#111111", borderRight: "1px solid #1e1e1e" }}
      >
        {/* Brand */}
        <div className="px-4 h-[52px] flex items-center justify-between shrink-0" style={{ borderBottom: "1px solid #1e1e1e" }}>
          <div className="flex items-center gap-2.5">
            <div
              className="w-[22px] h-[22px] rounded flex items-center justify-center"
              style={{ background: "#1a1a1a", border: "1px solid #2a2a2a" }}
            >
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#e5e5e5" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                <path d="M12 2L2 7l10 5 10-5-10-5z" />
                <path d="M2 17l10 5 10-5" />
                <path d="M2 12l10 5 10-5" />
              </svg>
            </div>
            <div className="flex flex-col">
              <span className="text-[13px] font-semibold tracking-[-0.01em]" style={{ color: "#e5e5e5" }}>
                Club Panel
              </span>
            </div>
          </div>

          <div className="flex items-center gap-1.5 px-2 py-0.5 rounded-full text-[10px] font-medium" style={{ background: "#161616", border: "1px solid #222", color: "#34d399" }}>
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
            <span>Connected</span>
          </div>
        </div>

        {/* Nav */}
        <nav className="flex-1 px-2 py-3 space-y-1 overflow-y-auto">
          <div className="px-2.5 pb-1 text-[10px] font-semibold uppercase tracking-wider" style={{ color: "#555" }}>
            Club Management
          </div>
          {navItems.map((item) => {
            const active = isActive(item.href, item.exact);
            const isLoadingThis = navigatingHref === item.href && !active;
            const Icon = item.icon;
            return (
              <Link
                key={item.href}
                href={item.href}
                onClick={() => {
                  if (!active) setNavigatingHref(item.href);
                }}
                className="group flex items-center justify-between px-2.5 py-[7px] rounded-md text-[13px] font-medium transition-colors duration-100"
                style={{
                  color: active ? "#e5e5e5" : "#777",
                  background: active ? "#1a1a1a" : "transparent",
                }}
                onMouseEnter={(e) => {
                  if (!active) {
                    e.currentTarget.style.background = "#161616";
                    e.currentTarget.style.color = "#aaa";
                  }
                }}
                onMouseLeave={(e) => {
                  if (!active) {
                    e.currentTarget.style.background = "transparent";
                    e.currentTarget.style.color = "#777";
                  }
                }}
              >
                <div className="flex items-center gap-2.5 min-w-0">
                  <Icon size={15} strokeWidth={1.8} style={{ opacity: active ? 1 : 0.6 }} />
                  <span className="truncate">{item.label}</span>
                </div>

                {isLoadingThis && (
                  <Loader2 size={12} className="animate-spin text-neutral-400 shrink-0 ml-1" />
                )}
              </Link>
            );
          })}
        </nav>

        {/* Footer / User Profile & Logout */}
        <div className="p-2 shrink-0 space-y-1.5" style={{ borderTop: "1px solid #1e1e1e" }}>
          {/* User Badge */}
          <div className="flex items-center gap-2.5 px-2.5 py-2 rounded-md" style={{ background: "#141414", border: "1px solid #1d1d1d" }}>
            <div className="w-6 h-6 rounded-full flex items-center justify-center text-[11px] font-semibold text-neutral-200" style={{ background: "#222" }}>
              {clubName ? clubName.charAt(0).toUpperCase() : userEmail ? userEmail.charAt(0).toUpperCase() : "C"}
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-[12px] font-medium truncate" style={{ color: "#d5d5d5" }}>
                {clubName || "Club Admin"}
              </p>
              <div className="flex items-center gap-1 text-[10px]" style={{ color: "#666" }}>
                <Building2 size={10} className="text-neutral-400" />
                <span className="truncate">{userEmail || "Representative"}</span>
              </div>
            </div>
          </div>

          <button
            onClick={handleLogout}
            className="flex items-center gap-2.5 w-full px-2.5 py-[7px] rounded-md text-[12px] font-medium transition-colors duration-100 cursor-pointer"
            style={{ color: "#777", background: "transparent" }}
            onMouseEnter={(e) => {
              e.currentTarget.style.background = "#181414";
              e.currentTarget.style.color = "#f87171";
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = "transparent";
              e.currentTarget.style.color = "#777";
            }}
          >
            <LogOut size={14} strokeWidth={1.8} />
            Sign out
          </button>
        </div>
      </aside>

      {/* Main content */}
      <main className="flex-1 min-w-0 overflow-y-auto">
        {children}
      </main>
    </div>
  );
}

