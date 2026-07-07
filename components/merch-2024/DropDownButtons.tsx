import React from "react";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import Link from "next/link";

const DropDownButtons = () => {
  return (
    <div className="flex gap-2">
      <Link href="/cart">
        <Avatar className="bg-yellow-500 rounded-full justify-center items-center">
          <AvatarImage src="/Icons/cart.svg" alt="Cart" className="h-6 w-6 " />
          <AvatarFallback>Cart</AvatarFallback>
        </Avatar>
      </Link>
      {/* <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button
            variant="outline"
            size="icon"
            className="text-black border-0 rounded-full"
          >
            <Avatar className="bg-yellow-500 rounded-full justify-center items-center">
              <AvatarImage
                src="/Icons/Filter.png"
                alt="Filter"
                className="h-6 w-6 "
              />
              <AvatarFallback>Filter</AvatarFallback>
            </Avatar>
          </Button>
        </DropdownMenuTrigger>

        <DropdownMenuContent className="w-64 px-2 py-1 bg-yellow-500 border-b border-black">
          <Accordion type="single" collapsible>
            <AccordionItem value="item-1" className="border-b border-black">
              <AccordionTrigger className="text-black font-semibold">
                GENDER
              </AccordionTrigger>
              <AccordionContent className="p-2 text-black">
                MALE
              </AccordionContent>
              <AccordionContent className="p-2 text-black">
                FEMALE
              </AccordionContent>
            </AccordionItem>

            <AccordionItem value="item-2" className="border-b border-black">
              <AccordionTrigger className="text-black font-semibold">
                KIDS
              </AccordionTrigger>
              <AccordionContent className="p-2 text-black">
                YES
              </AccordionContent>
              <AccordionContent className="p-2 text-black">NO</AccordionContent>
            </AccordionItem>

            <AccordionItem value="item-3" className="border-b border-black">
              <AccordionTrigger className="text-black font-semibold">
                SHOP BY PRICE
              </AccordionTrigger>
              <AccordionContent className="p-2 text-black">
                Below 500
              </AccordionContent>
              <AccordionContent className="p-2 text-black">
                500-1000
              </AccordionContent>
              <AccordionContent className="p-2 text-black">
                1000-1500
              </AccordionContent>
              <AccordionContent className="p-2 text-black">
                1500-2000
              </AccordionContent>
              <AccordionContent className="p-2 text-black">
                Above 2000
              </AccordionContent>
            </AccordionItem>

            <AccordionItem value="item-4" className="border-b border-black">
              <AccordionTrigger className="text-black font-semibold">
                COLOUR
              </AccordionTrigger>
              <AccordionContent className="p-2 text-black">
                Black
              </AccordionContent>
              <AccordionContent className="p-2 text-black">
                Red
              </AccordionContent>
              <AccordionContent className="p-2 text-black">
                Blue
              </AccordionContent>
              <AccordionContent className="p-2 text-black">
                Green
              </AccordionContent>
              <AccordionContent className="p-2 text-black">
                Yellow
              </AccordionContent>
              <AccordionContent className="p-2 text-black">
                White
              </AccordionContent>
            </AccordionItem>

            <AccordionItem value="item-5" className="border-b border-black">
              <AccordionTrigger className="text-black font-semibold">
                SPORTS
              </AccordionTrigger>
            </AccordionItem>

            <AccordionItem value="item-6" className="border-b border-black">
              <AccordionTrigger className="text-black font-semibold">
                BRANDS
              </AccordionTrigger>
            </AccordionItem>

            <AccordionItem value="item-7" className="border-b border-black">
              <AccordionTrigger className="text-black font-semibold">
                ICON
              </AccordionTrigger>
            </AccordionItem>

            <AccordionItem value="item-8" className="border-b-0">
              <AccordionTrigger className="text-black font-semibold">
                BEST FOR
              </AccordionTrigger>
            </AccordionItem>
          </Accordion>
        </DropdownMenuContent>
      </DropdownMenu>

      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button
            variant="outline"
            size="icon"
            className="text-black border-0 rounded-full"
          >
            <Avatar className="bg-yellow-500 rounded-full justify-center items-center">
              <AvatarImage
                src="/Icons/User.svg"
                alt="Account"
                className="h-6 w-6 "
              />
              <AvatarFallback>Account</AvatarFallback>
            </Avatar>
          </Button>
        </DropdownMenuTrigger>

        <DropdownMenuContent className="w-64 px-2 bg-yellow-500 border-b border-black">
          <Accordion type="single" collapsible>
            <AccordionItem value="item-1" className="border-b border-black">
              <AccordionTrigger className="text-black font-semibold">
                FAVOURITES
              </AccordionTrigger>
            </AccordionItem>

            <AccordionItem value="item-2" className="border-b border-black">
              <AccordionTrigger className="text-black font-semibold">
                ACCOUNT
              </AccordionTrigger>
            </AccordionItem>

            <AccordionItem value="item-3" className="border-b border-black">
              <AccordionTrigger className="text-black font-semibold">
                MY ORDERS
              </AccordionTrigger>
            </AccordionItem>
            <AccordionItem value="item-4" className="border-b-0">
              <AccordionTrigger className="text-black font-semibold">
                LOGOUT
              </AccordionTrigger>
            </AccordionItem>
          </Accordion>
        </DropdownMenuContent>
      </DropdownMenu> */}
    </div>
  );
};

export default DropDownButtons;
