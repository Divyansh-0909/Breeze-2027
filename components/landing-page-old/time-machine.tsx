import { useState, useEffect } from "react"

import TimeCarousel from "./TimeCarousel"

import { Elsie_Swash_Caps } from 'next/font/google';
import { PT_Sans } from 'next/font/google';

const elsie = Elsie_Swash_Caps({ 
  subsets: ["latin"],
  display: 'swap',
  weight: ['900'], 
  style: ['normal'] 
});

const ptSans = PT_Sans({ 
  subsets: ["latin"],
  display: 'swap',
  weight: ['400'], 
  style: ['normal'] 
});


const cap = [
    {
      key: 1,
      img: "/images/landing-page/time machine/24.jpeg",
      title: "2024",
      
    },
    {
      key: 2,
      img: "images/landing-page/time machine/23.jpeg",
      title: "2023",
      
    },
    {
      key: 3,
      img: "images/landing-page/time machine/22.jpeg",
      title: "2022",
      
    },
  ]; 


export default function TimeMachine(){
    return(
        <div className="bg-[#FABF12] pt-6 sm:pt-8 md:pt-10 lg:pt-12 pb-4 flex flex-col  items-center">
            <div className={`${elsie.className} lg:text-6xl text-[#EF3F60] md:text-4xl xl:text-6xl`}>
            Time Machine
            </div>
            <div className={`${ptSans.className} lg:text-2xl text-white pb-4 text-center w-[80%] md:text-xl xl:text-2xl`}>
            Here are a few highlights from Breeze, across the years

            </div>
            <div>
              <TimeCarousel cap={cap}/>
            </div>
        


        </div>
    )
}