'use client'

import * as React from "react"
import { ChevronRight, User, ChevronDown, ChevronUp, Filter, DollarSign, Calendar, Menu } from 'lucide-react'
import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuPortal,
  DropdownMenuSub,
  DropdownMenuSubContent,
  DropdownMenuSubTrigger,
  DropdownMenuTrigger,
  DropdownMenuRadioGroup,
  DropdownMenuRadioItem,
} from "@/components/ui/dropdown-menu"

type PriceOption = "Free + Paid" | "Free" | "Paid"
type EventType = "Workshop" | "Webinar" | "Conference" | "Meetup"

export default function EnhancedProfileFilterDropdown() {
  const [selectedPrice, setSelectedPrice] = React.useState<PriceOption>("Free + Paid")
  const [isSubscriptionOpen, setIsSubscriptionOpen] = React.useState(false)
  const [isEventOpen, setIsEventOpen] = React.useState(false)
  const [selectedEvent, setSelectedEvent] = React.useState<EventType>("Workshop")

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="outline" className="rounded-full p-3 bg-[#FABF12] hover:bg-[#FABF12]/90">
          <Menu className="h-6 w-6" />
          <span className="sr-only">Open menu</span>
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent className="w-48 bg-[#FABF12] text-black">
        <DropdownMenuSub>
          <DropdownMenuSubTrigger>
            <User className="h-4 w-4" />
            <span className="sr-only">Profile</span>
          </DropdownMenuSubTrigger>
          <DropdownMenuPortal>
            <DropdownMenuSubContent className="bg-[#FABF12]">
              <DropdownMenuItem className="hover:bg-[#FABF12]/80">Favorites</DropdownMenuItem>
              <DropdownMenuItem className="hover:bg-[#FABF12]/80">Account</DropdownMenuItem>
              <DropdownMenuItem className="hover:bg-[#FABF12]/80">My Orders</DropdownMenuItem>
              <DropdownMenuItem className="hover:bg-[#FABF12]/80">Logout</DropdownMenuItem>
            </DropdownMenuSubContent>
          </DropdownMenuPortal>
        </DropdownMenuSub>
        <DropdownMenuSub>
          <DropdownMenuSubTrigger>
            <Filter className="mr-2 h-4 w-4" />
            <span className="sr-only">Filter</span>
          </DropdownMenuSubTrigger>
          <DropdownMenuPortal>
            <DropdownMenuSubContent className="bg-[#FABF12]">
              <DropdownMenuItem className="hover:bg-[#FABF12]/80">Below 500</DropdownMenuItem>
              <DropdownMenuItem className="hover:bg-[#FABF12]/80">500-1000</DropdownMenuItem>
              <DropdownMenuItem className="hover:bg-[#FABF12]/80">1000-1500</DropdownMenuItem>
            </DropdownMenuSubContent>
          </DropdownMenuPortal>
        </DropdownMenuSub>
        <DropdownMenuSub>
          <DropdownMenuSubTrigger>
            <span>Price</span>
          </DropdownMenuSubTrigger>
          <DropdownMenuPortal>
            <DropdownMenuSubContent className="bg-[#FABF12]">
              <DropdownMenuRadioGroup 
                value={selectedPrice} 
                onValueChange={(value) => setSelectedPrice(value as PriceOption)}
              >
                <DropdownMenuRadioItem 
                  className="hover:bg-[#FABF12]/80 data-[state=checked]:bg-[#FABF12]/60"
                  value="Free + Paid"
                >
                  Free + Paid
                </DropdownMenuRadioItem>
                <DropdownMenuRadioItem 
                  className="hover:bg-[#FABF12]/80 data-[state=checked]:bg-[#FABF12]/60"
                  value="Free"
                >
                  Free
                </DropdownMenuRadioItem>
                <DropdownMenuRadioItem 
                  className="hover:bg-[#FABF12]/80 data-[state=checked]:bg-[#FABF12]/60"
                  value="Paid"
                >
                  Paid
                </DropdownMenuRadioItem>
              </DropdownMenuRadioGroup>
            </DropdownMenuSubContent>
          </DropdownMenuPortal>
        </DropdownMenuSub>
        <DropdownMenuSub>
          <DropdownMenuSubTrigger>
            <span>Event Type</span>
          </DropdownMenuSubTrigger>
          <DropdownMenuPortal>
            <DropdownMenuSubContent className="bg-[#FABF12]">
              <DropdownMenuRadioGroup 
                value={selectedEvent} 
                onValueChange={(value) => setSelectedEvent(value as EventType)}
              >
                <DropdownMenuRadioItem 
                  className="hover:bg-[#FABF12]/80 data-[state=checked]:bg-[#FABF12]/60"
                  value="Workshop"
                >
                  Workshop
                </DropdownMenuRadioItem>
                <DropdownMenuRadioItem 
                  className="hover:bg-[#FABF12]/80 data-[state=checked]:bg-[#FABF12]/60"
                  value="Webinar"
                >
                  Webinar
                </DropdownMenuRadioItem>
                <DropdownMenuRadioItem 
                  className="hover:bg-[#FABF12]/80 data-[state=checked]:bg-[#FABF12]/60"
                  value="Conference"
                >
                  Conference
                </DropdownMenuRadioItem>
                <DropdownMenuRadioItem 
                  className="hover:bg-[#FABF12]/80 data-[state=checked]:bg-[#FABF12]/60"
                  value="Meetup"
                >
                  Meetup
                </DropdownMenuRadioItem>
              </DropdownMenuRadioGroup>
            </DropdownMenuSubContent>
          </DropdownMenuPortal>
        </DropdownMenuSub>
      </DropdownMenuContent>
    </DropdownMenu>
  )
}