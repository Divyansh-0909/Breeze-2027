import React from "react";
import Image from "next/image";
import SponsorsScroll from "./SponsScroll";

export default function SponsComp() {
  return (
    <div className="self-center relative overflow-hidden">
      <div className="absolute inset-y-0 left-0 w-1/4 bg-gradient-to-r to-transparent pointer-events-none"></div>
      <SponsorsScroll />
      <div className="absolute inset-y-0 right-0 w-1/4 bg-gradient-to-l to-transparent pointer-events-none"></div>
    </div>
  );
}
