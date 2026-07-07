import React from "react";
import DropDown from "@/components/events/DropDown";

const Heading2 = ({content}: {content: string}) => {
  return (
    <div>
        <div className="flex flex-col justify-center items-center pt-[3vw] text-center">
          <h2 className="text-[17px] sm:text-[2.5vw] lg:text-[1.8vw] font-medium">
            BREEZE 2026 EVENTS
          </h2>
          <h1 className="text-[32px] sm:text-[4.5vw] lg:text-[3.5vw] font-normal"> Checkout our power-packed </h1>
          <h1 className="text-[32px] sm:text-[4.5vw]  lg:text-[3.5vw] mt-[-1.3vw] font-normal"> <span className="font-fraunces-italic text-4xl sm:text-[5vw]  lg:text-[4vw]  "> event  </span>lineup </h1>
          <p className="text-[12px] sm:text-[2vw] lg:text-[1.6vw] font-normal">{content}</p>
         
        </div>
        {/* <div className="pt-[4vw]">
          <DropDown />
        </div> */}
    </div>
        
  );
};

export default Heading2;
