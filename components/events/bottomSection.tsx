import React from "react";
import Image from "next/image";
import { Button } from "@/components/ui/button";
import Link from "next/link";

const BottomSection = () => {
  return (
    <section className="relative h-screen">
      {/* Pseudo-element with the blurred background */}
      <div className="absolute inset-0 bg-[url('/Images/Merch-2.png')] bg-cover bg-center bg-no-repeat"></div>

      {/* Content on top of the blurred background */}
      <div className="absolute bottom-0 w-full flex items-center justify-center ">
        {/* Scrolling bar container */}
        <div className="relative w-full overflow-hidden">
          <div
            className="flex gap-4 sm:gap-6 md:gap-10 items-center text-white px-2 sm:px-4 md:px-6 py-2 whitespace-nowrap animate-scroll"
            style={{ animation: "scroll 20s linear infinite" }}
          >
            {/* Text and Button Set */}
            <span className="text-sm sm:text-base md:text-lg font-semibold">
              Lorem ipsum dolor sit amet, consectetur adipiscing elit
            </span>
            <Link href="/events/all">
              <Button
                variant="outline"
                className="bg-transparent text-white pr-1 pl-2 sm:pl-4 py-1 sm:py-2 rounded-full shadow-md"
              >
                View all 
                <div className="rounded-full bg-white w-6 sm:w-8 h-6 sm:h-8 flex justify-center items-center ml-2">
                  <Image
                    src="/Icons/arrow.svg"
                    alt="Icon"
                    width={15}
                    height={15}
                  />
                </div>
              </Button>
            </Link>

            {/* Repeated Text and Button Set */}
            <span className="text-sm sm:text-base md:text-lg font-semibold">
              Lorem ipsum dolor sit amet, consectetur adipiscing elit
            </span>
            <Link href="/events/all">
              <Button
                variant="outline"
                className="bg-transparent text-white pr-1 pl-2 sm:pl-4 py-1 sm:py-2 rounded-full shadow-md"
              >
                View all 
                <div className="rounded-full bg-white w-6 sm:w-8 h-6 sm:h-8 flex justify-center items-center ml-2">
                  <Image
                    src="/Icons/arrow.svg"
                    alt="Icon"
                    width={15}
                    height={15}
                  />
                </div>
              </Button>
            </Link>
          </div>
        </div>
      </div>
    </section>
  );
};

export default BottomSection;
