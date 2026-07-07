import CountDown from "@/components/landing-page-old/clock";
import Flower from "@/components/landing-page-old/Flower";
import React from "react";

export default function Landing() {
  return (
    <div>
      <div className="grid grid-rows-[auto_auto] gric-cols-1 ">
        <div className="relative flex w-full h-[70vw] sm:h-[25.86vw] bg-[#FABF12]">
          <div className="absolute inset-0 flex items-center justify-center">
            <Flower />
            <div className="z-10">
              <CountDown />
            </div>
          </div>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-3 grid-rows-1 w-full">
          <div className="w-full h-auto">
            <video
              src="https://media.breezesnu.com/flower.mp4"
              autoPlay
              loop
              muted
              playsInline
              className="w-full h-full object-cover sticky z-10"
            />
          </div>
          <div className="w-full h-auto">
            <video
              src="https://media.breezesnu.com/hoodie.mp4"
              autoPlay
              loop
              muted
              playsInline
              className="w-full h-full object-cover sticky z-10"
            />
          </div>
          <div className="relative w-full h-auto">
            <video
              src="https://media.breezesnu.com/third.mp4"
              autoPlay
              loop
              muted
              playsInline
              className="w-full h-full object-cover sticky"
            />
            <div className="absolute top-0 left-0 w-full p-2 sm:p-3 sm:pt-4 md:p-[3vw]">
              <div className="flex justify-between items-center gap-2 sm:gap-4">
                <a
                  href="https://maps.app.goo.gl/W2tgttq8cAftvPdr8"
                  target="_blank"
                  className="flex-grow"
                >
                  <div
                    className="flex items-center justify-between 
                                        backdrop-blur-sm border-[#FABF12] border-[2px] 
                                        rounded-full p-2 sm:p-3 md:px-[1.8vw]"
                  >
                    <div className="flex items-center mr-2">
                      <img
                        src="\images\landing-page\landing\3.1.png"
                        alt=""
                        className="w-6 sm:w-[1.5vw] mr-2"
                      />
                      <div className="flex flex-col">
                        <div className="text-white text-xs lg:text-sm">
                          Shiv Nadar University
                        </div>
                        <div className="sm:hidden lg:block text-white text-[0.7xs] sm:text-xs opacity-80">
                          Breeze Main Arena
                        </div>
                      </div>
                    </div>
                    <img
                      src="\images\landing-page\landing\3.2.png"
                      alt=""
                      className="w-6 sm:w-[1.5vw]"
                    />
                  </div>
                </a>
                <div
                  className="p-2 sm:p-3 
                                    border-[#FABF12] border-[2px] 
                                    backdrop-blur-sm rounded-full"
                >
                  <img
                    src="\images\landing-page\landing\3.3.png"
                    alt=""
                    className="w-6 sm:w-[1.5vw]"
                  />
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
