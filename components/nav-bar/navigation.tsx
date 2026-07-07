"use client";
import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "../../lib/utils";
import {
  NavigationMenu,
  NavigationMenuItem,
  NavigationMenuLink,
  NavigationMenuList,
} from "@radix-ui/react-navigation-menu";

export function Navbar() {
  const pathname = usePathname();

  return (
    <NavigationMenu>
      <NavigationMenuList className="space-x-6 mt-2 hidden md:flex">
        <NavigationMenuItem>
          <Link href="/" legacyBehavior passHref>
            <NavigationMenuLink
              className={cn(
                "transition-colors hover:text-[#313628] text-[15px] font-bold",
                pathname === "/"
                  ? "text-navbar_text_select"
                  : "text-navbar_text"
              )}
            >
              Home
            </NavigationMenuLink>
          </Link>
        </NavigationMenuItem>

        <NavigationMenuItem>
          <Link href="/sponsors" legacyBehavior passHref>
            <NavigationMenuLink
              className={cn(
                "transition-colors hover:text-[#313628] text-[15px] font-bold",
                pathname === "/sponsors"
                  ? "text-navbar_text_select"
                  : "text-navbar_text"
              )}
            >
              Sponsors
            </NavigationMenuLink>
          </Link>
        </NavigationMenuItem>

        <NavigationMenuItem>
          <Link href="/team" legacyBehavior passHref>
            <NavigationMenuLink
              className={cn(
                "transition-colors hover:text-[#313628] text-[15px] font-bold",
                pathname === "/team"
                  ? "text-navbar_text_select"
                  : "text-navbar_text"
              )}
            >
              Team
            </NavigationMenuLink>
          </Link>
        </NavigationMenuItem>

        <NavigationMenuItem>
          <Link href="/get-in-touch" legacyBehavior passHref>
            <NavigationMenuLink
              className={cn(
                "transition-colors hover:text-[#313628] text-[15px] font-bold",
                pathname === "/get-in-touch"
                  ? "text-navbar_text_select"
                  : "text-navbar_text"
              )}
            >
              Contact Us
            </NavigationMenuLink>
          </Link>
        </NavigationMenuItem>
      </NavigationMenuList>
    </NavigationMenu>
  );
}

const ListItem = React.forwardRef<
  React.ElementRef<"a">,
  React.ComponentPropsWithoutRef<"a">
>(({ className, title, children, ...props }, ref) => {
  return (
    <li>
      <NavigationMenuLink asChild>
        <a
          ref={ref}
          className={cn(
            "block select-none space-y-1 rounded-md p-3 leading-none no-underline outline-none transition-colors hover:bg-accent hover:text-accent-foreground focus:bg-accent focus:text-accent-foreground",
            className
          )}
          {...props}
        >
          <div className="text-sm font-medium leading-none">{title}</div>
          <p className="line-clamp-2 text-sm leading-snug text-muted-foreground">
            {children}
          </p>
        </a>
      </NavigationMenuLink>
    </li>
  );
});
ListItem.displayName = "ListItem";
