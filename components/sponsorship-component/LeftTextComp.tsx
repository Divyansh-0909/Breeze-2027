import React from "react";

export default function LeftTextComp() {
  return (
    <div className="flex-none flex flex-col align-flex-start max-w-[744px] max-h-[480px] mb-12">
      
      {/* Heading */}
      <div className="text-white font-satoshi text-[84px] leading-[92px] mt-8 mb-6">
        Discover Our
      </div>
      <div className="text-white font-satoshi text-[84px] leading-[92px] mb-10">
        <span className="font-fraunces italic">Exceptional</span> Partners
      </div>

      {/* Description */}
      <div className="text-white font-satoshi text-[28px] leading-[34px] max-w-[679px] pb-6">
        Explore the vibrant tapestry of partners who make Breeze come alive, and {`let's`} celebrate the spirit of collaboration that defines our festival!
      </div>

      {/* Button */}
      <div className="flex rounded-full mt-[17px] h-[64px] max-w-[257.3px] bg-white text-black items-center justify-center cursor-pointer">
        Check them out
      </div>
    </div>
  );
}
