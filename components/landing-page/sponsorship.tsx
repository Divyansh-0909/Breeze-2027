import React from "react";
import SponsComp from "../sponsorship-component/SponsImage";
import TopText from "../sponsorship-component/TopTesx";
import "../../app/globals.css";

interface SponsorsProps {
  className?: string;
}

export default function Sponsors({ className }: SponsorsProps) {
  return (
    <section
      id="sponsorship"
      className={`relative scroll-mt-[90px] rounded-t-[3rem] md:rounded-t-[5rem] overflow-hidden ${className}`}
      style={{
        background:
          "linear-gradient(to bottom, #000000 0%, rgb(44, 9, 73, 0.9) 25%, rgb(44, 9, 73, 1) 50%, rgb(44, 9, 73, 0.9) 90%, #000000 100%)",
      }}
    >
      <div className="radial-bg">
        <div className="flex flex-col justify-center shrink-0 max-w-full overflow-hidden">
          <TopText />
          <SponsComp />
        </div>
      </div>
    </section>
  );
}
