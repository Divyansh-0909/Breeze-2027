import React from "react";
import { GoArrowUpRight } from "react-icons/go";
import { Separator } from "@/components/ui/separator";
import Link from "next/link";
import Image from "next/image";

export const metadata = {
  title: "Sponsors - Breeze '26",
  description: "Sponsors of Breeze '26",
};

const Sponsors = () => {
  return (
    <div className="bg-[#FABF12] ">
      <div className="h-fit w-full flex flex-col items-center gap-8 relative pb-20 top-24 text-white">
        <div className="flex gap-2 w-full justify-center flex-wrap">
          <div className="w-5/12 m-2 bg-yellow-600  bg-opacity-50 rounded-3xl md:h-96 h-40 max-xl:w-10/12 relative">
            <div className="absolute top-0 right-0">
              <GoArrowUpRight className="md:w-36 md:h-36 w-12 h-12" />
            </div>
            <div className="absolute bottom-0 left-0 text-3xl m-4 md:text-5xl md:w-2/3 font-normal">
              Thank you to our{" "}
              <span className="font-fraunces-italic">Current</span> Partners!
            </div>
          </div>
          <Link
            href="https://stoknchill.com/"
            className="w-1/5 m-2 bg-opacity-50 rounded-s-3xl md:h-96 h-40 max-xl:w-10/12 max-xl:rounded-2xl p-4 flex justify-center items-center hover:-translate-y-2 transition-all"
          >
            {/* <Link href="https://stoknchill.com/"> */}
            <Image
              src="/images/sponsors/StokNChill.png"
              alt="Sponsor"
              width={400}
              height={400}
              className="max-w-full max-h-full object-contain rounded-2xl"
            />
            {/* </div> */}
          </Link>
          <Link
            href="https://www.group-108.com/"
            className="w-1/5 m-2 bg-opacity-50 rounded-e-3xl md:h-96 h-44 max-xl:w-10/12 max-xl:rounded-2xl flex justify-center items-center hover:-translate-y-2 transition-all"
          >
            {/* <Link href="https://www.group-108.com/" > */}
            <Image
              src="/images/sponsors/Group108.png"
              alt="Sponsor"
              width={400}
              height={400}
              className="max-w-[92%] max-h-full object-contain md:rounded-2xl"
            />
          </Link>
          {/* </div> */}
        </div>
        {/* <div className="flex gap-2 w-full   justify-center flex-wrap">
          <div className="md:w-1/6 w-36 bg-opacity-50 rounded-s-3xl md:h-48 h-36 md:max-xl:w-2/6 max-xl:rounded-xl md:p-4 p-3 flex justify-center items-center">
            <img
              src="/images/sponsors/AMD.png"
              alt="Sponsor"
              className="max-w-full max-h-full object-contain  rounded-2xl"
            />
          </div>
          <div className="md:w-1/6 bg-opacity-50 w-36 md:h-48 md:max-xl:w-2/6 max-xl:rounded-xl md:p-4 p-5 flex justify-center items-center">
            <img
              src="/images/sponsors/Jio.png"
              alt="Sponsor"
              className="max-w-full max-h-full object-contain rounded-2xl"
            />
          </div>
          <div className="md:w-1/6  w-36 bg-opacity-50 md:h-48 h-36 md:max-xl:w-2/6 max-xl:rounded-xl p-4 flex justify-center items-center">
            {" "}
            <img
              src="/images/sponsors/Ebay.png"
              alt="Sponsor"
              className="max-w-full max-h-full object-contain rounded-2xl"
            />
          </div>
          <div className="md:w-1/6 w-36 bg-opacity-50  md:h-48 h-36 md:max-xl:w-2/6 max-xl:rounded-xl p-4 flex justify-center items-center">
            <img
              src="/images/sponsors/Pepsi.png"
              alt="Sponsor"
              className="max-w-full max-h-full object-contain rounded-2xl"
            />
          </div>
          <div className="md:w-1/6 w-72 bg-opacity-50 rounded-e-3xl h-48  md:max-xl:w-2/6 max-xl:rounded-xl md:p-4 p-5 flex justify-center items-center">
            <img
              src="/images/sponsors/TSeries.png"
              alt="Sponsor"
              className="max-w-full max-h-full object-contain md:rounded-2xl"
            />
          </div>
        </div>
        <div className="flex  md:gap-2 gap-2 w-full justify-center flex-wrap">
          <div className="md:w-1/6 bg-opacity-50 rounded-s-3xl md:h-48 h-36 w-36 md:max-xl:w-2/6 max-xl:rounded-xl md:p-4 p-5 flex justify-center items-center">
            <img
              src="/images/sponsors/L&T.png"
              alt="Sponsor"
              className="max-w-full max-h-full object-contain rounded-2xl"
            />
          </div>
          <div className="md:w-1/6 bg-opacity-50  md:h-48 h-36 w-36 md:max-xl:w-2/6 max-xl:rounded-xl p-4 flex justify-center items-center">
            <img
              src="/images/sponsors/Kingfisher.png"
              alt="Sponsor"
              className="max-w-full max-h-full object-contain rounded-2xl"
            />
          </div>
          <div className="md:w-1/6 bg-opacity-50 h-36 md:h-48 w-36 md:max-xl:w-2/6 max-xl:rounded-xl md:p-4 p-2 flex justify-center items-center">
            <img
              src="/images/sponsors/Radisson.png"
              alt="Sponsor"
              className="max-w-full max-h-full object-contain rounded-2xl"
            />
          </div>
          <div className="md:w-1/6 bg-opacity-50 h-36 md:h-48 w-36 md:max-xl:w-2/6 max-xl:rounded-xl md:p-4 p-3 flex justify-center items-center">
            <img
              src="/images/sponsors/RedFM.png"
              alt="Sponsor"
              className="max-w-full max-h-full object-contain md:rounded-2xl"
            />
          </div>
          <div className="md:w-1/6 w-72 bg-opacity-50 rounded-e-3xl md:h-48 h-36 md:max-xl:w-2/6 max-xl:rounded-xl p-4 flex justify-center items-center">
            <img
              src="/images/sponsors/Mtv.png"
              alt="Sponsor"
              className="max-w-full max-h-full object-contain md:rounded-2xl"
            />
          </div>
        </div>
        <div className="flex md:gap-2 md:pl-0 md:pr-0 pl-5 pr-5 w-full justify-center items-center">
          <div className="md:w-7/12 m-2 w-60 relative bg-opacity-50 rounded-s-3xl md:h-72 h-56 p-4 md:max-xl:w-10/12 max-xl:rounded-2xl flex justify-center items-center">
            <div className="md:flex-row flex flex-col justify-center items-center gap-6 md:gap-10 md:p-6">
              <img
                src="/images/sponsors/RedBull.png"
                alt="Sponsor"
                className="md:max-w-[40%] w-[90%]  md:max-h-full object-contain md:rounded-2xl"
              />
              <img
                src="/images/sponsors/Saavn.png"
                alt="Sponsor"
                className="md:max-w-[40%] w-[100%] md:max-h-full object-contain md:rounded-2xl"
              />
            </div>
          </div>
          <div className="md:w-3/12 w-60 m-2 bg-opacity-50 rounded-e-3xl md:h-72 h-56 md:p-8 p-3 md:max-xl:w-10/12 max-xl:rounded-2xl flex justify-center items-center">
            <img
              src="/images/sponsors/SBI.png"
              alt="Sponsor"
              className="md:max-w-full md:max-h-full w-[80%] object-contain rounded-2xl"
            />
          </div>
        </div>

        <div className="flex gap-2 w-full justify-center flex-wrap">
          <div className="md:w-1/6 bg-opacity-50 rounded-s-3xl md:h-48 h-36 w-36 md:max-xl:w-2/6 max-xl:rounded-xl md:p-4 p-2 flex justify-center items-center">
            <img
              src="/images/sponsors/PayU.png"
              alt="Sponsor"
              className="md:max-w-full md:max-h-full object-contain rounded-2xl"
            />
          </div>
          <div className="md:w-1/6 bg-opacity-50 h-36 md:h-48 w-36 md:max-xl:w-2/6 max-xl:rounded-xl p-4 flex justify-center items-center">
            <img
              src="/images/sponsors/Wildcraft.png"
              alt="Sponsor"
              className="max-w-full max-h-full object-contain md:rounded-2xl"
            />
          </div>
          <div className="md:w-1/6 bg-opacity-50 md:h-48 h-36 w-36 md:max-xl:w-2/6 max-xl:rounded-xl md:p-4 p-2 flex justify-center items-center">
            {" "}
            <img
              src="/images/sponsors/Spykar.png"
              alt="Sponsor"
              className="max-w-full max-h-full object-contain rounded-2xl"
            />
          </div>
          <div className="md:w-1/6 bg-opacity-50  h-36 w-36 md:h-48 md:max-xl:w-2/6 max-xl:rounded-xl p-4 flex justify-center items-center">
            <img
              src="/images/sponsors/Daikin.png"
              alt="Sponsor"
              className="max-w-full max-h-full object-contain md:rounded-2xl"
            />
          </div>
          <div className="md:w-1/6 bg-opacity-50 rounded-e-3xl md:h-48 w-72 h-36 md:max-xl:w-2/6 max-xl:rounded-xl p-4 flex justify-center items-center">
            <img
              src="/images/sponsors/Playstation.png"
              alt="Sponsor"
              className="max-w-full max-h-full object-contain rounded-2xl"
            />
          </div>
        </div> */}
        <Separator />
      </div>
    </div>
  );
};

export default Sponsors;
