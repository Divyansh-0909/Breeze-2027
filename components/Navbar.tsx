"use client";

import Link from "next/link";
import Image from "next/image";
import heroimg from "./breeze.png";
import React, { useState, useEffect } from "react";
import { usePathname } from "next/navigation";
import { FaBars } from "react-icons/fa";
import SoundButton from "./SoundButton";
import { Sheet, SheetContent, SheetHeader } from "./ui/sheet";
import { cn } from "@/lib/utils";
import "../app/globals.css";

interface NavbarProps {
  className?: string;
}

const Navbar = ({ className }: NavbarProps) => {
  const pathname = usePathname();

  type NavLink =
    | { name: string; href: string }
    | { name: string; scrollTo: string };

  const navLinks: NavLink[] = [
    { name: "Home", href: "/" },
    { name: "Events", href: "/events" },
    // { name: "Merch", href: "/merch" }, // Temporarily disabled
    { name: "Team", href: "/team" },
    { name: "Contact Us", href: "/get-in-touch" },
  ];

  const [isPlaying, setIsPlaying] = useState(false);
  const [isOpen, setIsOpen] = useState(false);
  const [prevScrollPos, setPrevScrollPos] = useState(0);
  const [visible, setVisible] = useState(true);

  const handleTogglePlay = () => {
    setIsPlaying((prev) => !prev);
  };

  const toggleSidebar = () => {
    setIsOpen(!isOpen);
  };

  const handleLinkClick = () => {
    if (isOpen) {
      setIsOpen(false);
    }
  };

  // Hide/show navbar on scroll
  useEffect(() => {
    const handleScroll = () => {
      const currentScrollPos = window.scrollY;
      setVisible(prevScrollPos > currentScrollPos || currentScrollPos < 10);
      setPrevScrollPos(currentScrollPos);
    };

    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, [prevScrollPos]);

  const isActiveLink = (path: string) => {
    if (path === "/merch") {
      return pathname.startsWith("/merch") || pathname.startsWith("/product");
    }
    return pathname === path;
  };

  const renderLink = (link: NavLink) =>
    "scrollTo" in link ? (
      <button
        key={link.name}
        onClick={() =>
          document
            .getElementById(link.scrollTo)
            ?.scrollIntoView({ behavior: "smooth" })
        }
        className="text-white/75 text-[15px] font-bold transition-colors hover:text-white"
      >
        {link.name}
      </button>
    ) : (
      <Link
        key={link.name}
        href={link.href}
        className={cn(
          "text-[15px] font-bold whitespace-nowrap transition-colors hover:text-white",
          isActiveLink(link.href) ? "text-white" : "text-white/75"
        )}
      >
        {link.name}
      </Link>
    );

  return (
    <nav
      className={cn(
        "w-full fixed top-0 left-0 z-50 transition-transform duration-300",
        visible ? "translate-y-0" : "-translate-y-full",
        className
      )}
    >
      {/* Split navbar: Home/Events pinned to the far left edge, Team/Contact
          Us/cart pinned to the far right. The center stays clear for the 3D
          signage board on the front top truss. */}
      <div className="flex items-center px-5 md:px-8 pt-[5.5vh]">
        {/* LEFT: links on a black panel, extreme left */}
        <div className="hidden md:flex items-center gap-6 bg-black/70 backdrop-blur-md border border-white/10 rounded-xl px-6 py-2.5 [text-shadow:0_1px_8px_rgba(0,0,0,0.9)]">
          {navLinks.slice(0, 3).map(renderLink)}
        </div>
        {/* <SoundButton isPlaying={isPlaying} onToggle={handleTogglePlay} /> */}

        {/* RIGHT: links + cart on a black panel, extreme right */}
        <div className="ml-auto flex items-center gap-4 md:gap-6 bg-black/70 backdrop-blur-md border border-white/10 rounded-xl px-4 md:px-6 py-1.5">
          <div className="hidden md:flex items-center gap-6 [text-shadow:0_1px_8px_rgba(0,0,0,0.9)]">
            {navLinks.slice(3).map(renderLink)}
          </div>
          <Link
            href="/cart"
            className="flex items-center justify-center w-10 h-10 transition duration-200 hover:bg-purple-900 rounded [filter:drop-shadow(0_1px_4px_rgba(0,0,0,0.9))]"
            aria-label="Cart"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="20"
              height="20"
              viewBox="0 0 24 24"
              fill="none"
              stroke="white"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <circle cx="9" cy="21" r="1" />
              <circle cx="20" cy="21" r="1" />
              <path d="M1 1h4l2.6 13.4a2 2 0 0 0 2 1.6h9.7a2 2 0 0 0 2-1.6L23 6H6" />
            </svg>
          </Link>

          {/* MOBILE MENU BUTTON */}
          <button
            className="md:hidden [filter:drop-shadow(0_1px_4px_rgba(0,0,0,0.9))]"
            onClick={toggleSidebar}
            aria-label="Menu"
          >
            <FaBars className="text-white text-xl cursor-pointer" />
          </button>
        </div>
      </div>

      {/* MOBILE SIDEBAR */}
      <Sheet open={isOpen} onOpenChange={setIsOpen}>
        <SheetContent className="border-0 m-0 bg-[#1a0a2e] border-l border-purple-900/30">
          <SheetHeader className="mt-10">
            <nav className="flex flex-col space-y-4">
              {navLinks.map((link) =>
                "scrollTo" in link ? (
                  <button
                    key={link.name}
                    onClick={() => {
                      document
                        .getElementById(link.scrollTo)
                        ?.scrollIntoView({ behavior: "smooth" });
                      handleLinkClick();
                    }}
                    className="text-navbar_text text-[15px] font-bold text-left"
                  >
                    {link.name}
                  </button>
                ) : (
                  <Link
                    key={link.name}
                    href={link.href}
                    onClick={handleLinkClick}
                    className={cn(
                      "text-[15px] font-bold",
                      isActiveLink(link.href)
                        ? "text-navbar_text_select"
                        : "text-navbar_text"
                    )}
                  >
                    {link.name}
                  </Link>
                )
              )}
            </nav>
          </SheetHeader>
        </SheetContent>
      </Sheet>
    </nav>
  );
};

export default Navbar;
