"use client"

import * as React from "react"
import { ChevronDown, ChevronUp } from 'lucide-react'

import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuRadioGroup,
  DropdownMenuRadioItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"

type SubscriptionOption = "Free + Paid" | "Free" | "Paid"
type EventType = "Workshop" | "Webinar" | "Conference" | "Meetup"

export default function CombinedDropdowns() {
  // States for Subscription Type Dropdown
  const [selectedSubscription, setSelectedSubscription] = React.useState<SubscriptionOption>("Free + Paid")
  const [isSubscriptionOpen, setIsSubscriptionOpen] = React.useState(false)

  // States for Event Type Dropdown
  const [selectedEvent, setSelectedEvent] = React.useState<EventType>("Workshop")
  const [isEventOpen, setIsEventOpen] = React.useState(false)

  return (
    <div className=" flex gap-[3vw] flex-col md:flex-row">
      {/* Subscription Type Dropdown */}
      <div>
      <DropdownMenu open={isSubscriptionOpen} onOpenChange={setIsSubscriptionOpen}>
        <DropdownMenuTrigger asChild>
          <Button 
            style={{ backgroundColor: '#FABF12', borderColor: '#FABF12' }}
            className="text-white hover:bg-opacity-90 border flex items-center justify-between min-w-[150px] rounded-[4vw]"
          >
            <span>{selectedSubscription}</span>
            {isSubscriptionOpen ? <ChevronUp className="ml-2 h-4 w-4" /> : <ChevronDown className="ml-2 h-4 w-4" />}
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent 
          style={{ backgroundColor: '#FCD34D' }} 
          className="w-56 border-yellow-400"
        >
          <DropdownMenuRadioGroup 
            value={selectedSubscription} 
            onValueChange={(value) => setSelectedSubscription(value as SubscriptionOption)}
          >
            <DropdownMenuRadioItem
              value="Free + Paid"
              className="text-white focus:bg-yellow-500 focus:text-white cursor-pointer"
            >
              Free + Paid
            </DropdownMenuRadioItem>
            <DropdownMenuRadioItem
              value="Free"
              className="text-white focus:bg-yellow-500 focus:text-white cursor-pointer"
            >
              Free
            </DropdownMenuRadioItem>
            <DropdownMenuRadioItem
              value="Paid"
              className="text-white focus:bg-yellow-500 focus:text-white cursor-pointer"
            >
              Paid
            </DropdownMenuRadioItem>
          </DropdownMenuRadioGroup>
        </DropdownMenuContent>
      </DropdownMenu>
     </div>

     <div>
      {/* Event Type Dropdown */}
      <DropdownMenu open={isEventOpen} onOpenChange={setIsEventOpen}>
        <DropdownMenuTrigger asChild>
          <Button 
            style={{ backgroundColor: '#FABF12', borderColor: '#FABF12' }}
            className="text-white hover:bg-opacity-90 border flex items-center justify-between min-w-[150px] rounded-[4vw]"
          >
            <span>{selectedEvent}</span>
            {isEventOpen ? <ChevronUp className="ml-2 h-4 w-4" /> : <ChevronDown className="ml-2 h-4 w-4" />}
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent 
          style={{ backgroundColor: '#FCD34D' }} 
          className="w-56 border-yellow-400"
        >
          <DropdownMenuRadioGroup 
            value={selectedEvent} 
            onValueChange={(value) => setSelectedEvent(value as EventType)}
          >
            <DropdownMenuRadioItem
              value="Workshop"
              className="text-white focus:bg-yellow-500 focus:text-white cursor-pointer"
            >
              Workshop
            </DropdownMenuRadioItem>
            <DropdownMenuRadioItem
              value="Webinar"
              className="text-white focus:bg-yellow-500 focus:text-white cursor-pointer"
            >
              Webinar
            </DropdownMenuRadioItem>
            <DropdownMenuRadioItem
              value="Conference"
              className="text-white focus:bg-yellow-500 focus:text-white cursor-pointer"
            >
              Conference
            </DropdownMenuRadioItem>
            <DropdownMenuRadioItem
              value="Meetup"
              className="text-white focus:bg-yellow-500 focus:text-white cursor-pointer"
            >
              Meetup
            </DropdownMenuRadioItem>
          </DropdownMenuRadioGroup>
        </DropdownMenuContent>
      </DropdownMenu>

      </div>
    </div>
  )
}
