"use client";

import Link from "next/link";
import React from "react";
import { usePathname } from "next/navigation";
import { Home as HomeIcon, ShoppingCart } from "lucide-react";

import { cn } from "@/lib/utils";

interface NavbarProps {
  className?: string;
}

const linkClass =
  "whitespace-nowrap text-[11px] font-bold uppercase tracking-[0.08em] text-white/60 transition-colors duration-200 hover:text-white focus-visible:text-white focus-visible:outline-none sm:text-xs";

export default function Navbar({ className }: NavbarProps) {
  const pathname = usePathname();
  const isActive = (href: string) =>
    href === "/" ? pathname === "/" : pathname === href || pathname.startsWith(`${href}/`);

  const navLink = (
    label: string,
    href: string,
    onClick?: React.MouseEventHandler<HTMLAnchorElement>
  ) => (
    <Link
      href={href}
      onClick={onClick}
      className={cn(linkClass, isActive(href) && "text-white")}
      aria-current={isActive(href) ? "page" : undefined}
    >
      {label}
    </Link>
  );

  const handleHomeClick = (event: React.MouseEvent<HTMLAnchorElement>) => {
    if (pathname !== "/") return;
    if (
      event.metaKey ||
      event.ctrlKey ||
      event.shiftKey ||
      event.altKey ||
      event.button !== 0
    ) {
      return;
    }

    const handled = !window.dispatchEvent(
      new Event("breeze:return-home", { cancelable: true })
    );
    if (handled) event.preventDefault();
  };

  const handleContactClick = (event: React.MouseEvent<HTMLAnchorElement>) => {
    if (pathname !== "/") return;
    if (
      event.metaKey ||
      event.ctrlKey ||
      event.shiftKey ||
      event.altKey ||
      event.button !== 0
    ) {
      return;
    }

    const handled = !window.dispatchEvent(
      new Event("breeze:open-contact", { cancelable: true })
    );
    if (handled) event.preventDefault();
  };

  return (
    <nav
      aria-label="Primary navigation"
      className={cn(
        "pointer-events-none fixed inset-x-0 top-3 z-[200] flex items-start justify-between gap-2 px-3 sm:top-4 sm:px-5 md:px-8",
        className
      )}
    >
      <div className="pointer-events-auto flex items-center gap-3 rounded-2xl border border-neutral-500/40 bg-black/80 px-3 py-2 shadow-lg shadow-black/25 sm:gap-5 sm:px-4">
        <Link
          href="/"
          onClick={handleHomeClick}
          aria-label="Home"
          aria-current={isActive("/") ? "page" : undefined}
          className={cn(
            "flex items-center justify-center text-white/60 transition-colors duration-200 hover:text-white focus-visible:text-white focus-visible:outline-none",
            isActive("/") && "text-white"
          )}
        >
          <HomeIcon aria-hidden="true" className="h-4 w-4" strokeWidth={2} />
        </Link>
        {navLink("Events", "/events")}
      </div>

      <div className="pointer-events-auto ml-auto flex items-center gap-3 rounded-2xl border border-neutral-500/40 bg-black/80 px-3 py-2 shadow-lg shadow-black/25 sm:gap-5 sm:px-4">
        {navLink("Contact", "/get-in-touch", handleContactClick)}
        <Link
          href="/cart"
          aria-label="Cart"
          aria-current={isActive("/cart") ? "page" : undefined}
          className={cn(
            "flex items-center justify-center text-white/60 transition-colors duration-200 hover:text-white focus-visible:text-white focus-visible:outline-none",
            isActive("/cart") && "text-white"
          )}
        >
          <ShoppingCart aria-hidden="true" className="h-4 w-4" strokeWidth={2} />
        </Link>
      </div>
    </nav>
  );
}
