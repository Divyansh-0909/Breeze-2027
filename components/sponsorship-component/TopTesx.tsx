import React from "react";
import { Fraunces } from "next/font/google";

const fraunces = Fraunces({
  subsets: ["latin"],
  variable: "--font-fraunces",
  display: "swap",
  weight: ["400", "700"],
  style: ["normal", "italic"],
});

export default function TopText() {
  return (
    <div className="flex flex-col justify-center text-center items-center px-4">
      {/* Heading */}
      <h1
        className={`font-satoshi w-full 
                text-[28px] sm:text-[36px] lg:text-[46px] xl:text-[56px] 
                leading-tight pt-8 mt-8 mb-6 lg:px-[20%] xl:pb-4`}
      >
        Discover Our{" "}
        <span className={`${fraunces.className} text-[#EC1B4B] italic`}>
          Exceptional
        </span>{" "}
        Partners!
      </h1>

      {/* Paragraph */}
      <p
        className="font-satoshi text-sm sm:text-base lg:text-lg xl:text-xl 
                w-[80%] sm:w-[60%] lg:w-full lg:px-[25%] mb-8 italic"
      >
        Explore the vibrant tapestry of partners who make Breeze come alive, and
        let's celebrate the spirit of collaboration that defines our festival!
      </p>
    </div>
  );
}
