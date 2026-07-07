"use client";
import All from "./Collection/All";
import Winter from "./Collection/Winter";
import New from "./Collection/New";
import Best from "./Collection/Best";
import Luxury from "./Collection/Luxury";
import Men from "./Collection/Men";
import Buttons from "./Buttons";
import NavArrows from "./NavArrows";
import Heading from "./Heading";
import OurMerch from "./OurMerch";
import { useState } from "react";
export default function Merch()
{
  const [selectedBadge, setSelectedBadge] = useState("NEW ARRIVALS");
  const renderContent = () => {
    switch (selectedBadge) {
      case "ALL":
        return <All />;
      case "WINTERS COLLECTION":
        return <Winter />;
      case "NEW ARRIVALS":
        return <New />;
      case "BEST SELLERS":
        return <Best />;
      case "MEN'S COLLECTION":
        return <Men />;
      case "LUXURY COLLECTION":
        return <Luxury />;
      default:
        return <div>No content available</div>; // Default content if no case matches
    }
  };
  return (
    <main>
      <div className="max-sm:flex max-sm:items-center max-sm:flex-col max-sm:justify-center">
        <OurMerch/>
        <div className="flex items-center justify-between">
          <Heading />
          <NavArrows />
        </div>
      </div>
      <Buttons selectedBadge={selectedBadge} setSelectedBadge={setSelectedBadge} />
      {renderContent()}
    </main>
  )
}

