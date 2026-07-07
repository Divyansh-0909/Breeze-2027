"use client";
import React, { useState } from "react";
import { FaBars } from "react-icons/fa";
import { Sheet, SheetContent, SheetHeader } from "../../components/ui/sheet";
import {
  NavigationMenu,
  NavigationMenuList,
  NavigationMenuItem,
  NavigationMenuLink,
} from "@radix-ui/react-navigation-menu";
import Link from "next/link";
import { usePathname } from "next/navigation";

const SideBar = () => {
  const [isOpen, setIsOpen] = useState(false);
  const pathname = usePathname();

  const toggleSidebar = () => {
    if (window.innerWidth < 1024) {
      setIsOpen(!isOpen);
    }
  };

  const handleLinkClick = () => {
    if (isOpen) {
      setIsOpen(false);
    }
  };

  const isActiveLink = (path) => {
    if (path === "/merch") {
      return pathname.startsWith("/merch") || pathname.startsWith("/product")
        ? "text-navbar_text_select"
        : "text-navbar_text";
    }
    return pathname === path ? "text-navbar_text_select" : "text-navbar_text";
  };

  return (
    <div className="mt-3 md:hidden">
      <div className="mb-2 md:mb-0">
        <FaBars
          className="mr-3 md:mr-10 text-white cursor-pointer md:hidden"
          onClick={toggleSidebar}
        />
      </div>
      <div className={`sidebar lg:block ${isOpen ? "" : "hidden"}`}>
        <Sheet open={isOpen} onOpenChange={setIsOpen}>
          <SheetContent className="border-0 m-0 bg-orange-600">
            <SheetHeader className="mt-10">
              <NavigationMenu>
                <NavigationMenuList className="flex flex-col space-y-4">
                  <NavigationMenuItem>
                    <Link href="/" legacyBehavior passHref>
                      <NavigationMenuLink
                        className={`text-[15px] font-bold ${isActiveLink("/")}`}
                        onClick={handleLinkClick}
                      >
                        Home
                      </NavigationMenuLink>
                    </Link>
                  </NavigationMenuItem>

                  <NavigationMenuItem>
                    <Link href="/sponsors" legacyBehavior passHref>
                      <NavigationMenuLink
                        className={`text-[15px] font-bold ${isActiveLink(
                          "/sponsors"
                        )}`}
                        onClick={handleLinkClick}
                      >
                        Sponsors
                      </NavigationMenuLink>
                    </Link>
                  </NavigationMenuItem>

                  <NavigationMenuItem>
                    <Link href="/team" legacyBehavior passHref>
                      <NavigationMenuLink
                        className={`text-[15px] font-bold ${isActiveLink(
                          "/team"
                        )}`}
                        onClick={handleLinkClick}
                      >
                        Team
                      </NavigationMenuLink>
                    </Link>
                  </NavigationMenuItem>

                  <NavigationMenuItem>
                    <Link href="/get-in-touch" legacyBehavior passHref>
                      <NavigationMenuLink
                        className={`text-[15px] font-bold ${isActiveLink(
                          "/get-in-touch"
                        )}`}
                        onClick={handleLinkClick}
                      >
                        Contact Us
                      </NavigationMenuLink>
                    </Link>
                  </NavigationMenuItem>
                </NavigationMenuList>
              </NavigationMenu>
            </SheetHeader>
          </SheetContent>
        </Sheet>
      </div>
    </div>
  );
};

export default SideBar;
