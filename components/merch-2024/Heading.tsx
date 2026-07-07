import React from "react";
import { Button } from "@/components/ui/button";
import Image from "next/image";
import Link from "next/link";

const Heading = () => {
  return (
    <div className="flex flex-col gap-2 sm:gap-1 m-10 mb-0">
      <h1 className="text-2xl font-normal">OUR MERCH</h1>
      <div className="flex justify-between items-center flex-wrap sm:flex-nowrap sm:gap-5 gap-3 ">
        <p
          className="text-5xl font-thin font-fraunces-italic-bold"
          
        >
          The Coolest Merch Around
        </p>
        <div className="flex justify-center items-center">
          <Link href="/merch/all">
            <Button variant="link" className="text-xl font-bold pl-0 sm:pl-4">
              Shop Now
            </Button>
          </Link>
          <Link href="/merch/all">
            <Image
              src="/Icons/arrow-2.svg"
              alt="Icon"
              width={45}
              height={45}
              className="shrink-0 min-h-10 min-w-10"
            />
          </Link>
        </div>
      </div>
    </div>
  );
};

export default Heading;
