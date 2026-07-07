"use client";

import { useState } from "react";
import Image from "next/image";
import Link from "next/link";

export default function BuyMerch() {
  const [selectedSize, setSelectedSize] = useState("41");
  
  const sizes = ["39.5", "40", "41", "42", "43", "45", "46", "47"];

  return (
    <section className="relative w-full min-h-screen bg-[#0d0015] text-white py-10 lg:py-20 px-4 md:px-12 flex items-center justify-center">
      
      <div className="max-w-7xl mx-auto w-full grid grid-cols-1 lg:grid-cols-12 gap-8 lg:gap-12 items-start lg:items-center">
        
        {/* --- LEFT COLUMN: THUMBNAILS (Desktop Vertical) --- */}
        <div className="hidden lg:flex lg:col-span-1 flex-col gap-4">
          {[1, 2, 3, 4].map((item) => (
            <div key={item} className="w-20 h-20 bg-gray-800 border border-gray-700 relative cursor-pointer hover:border-white transition-colors">
               {/* <Image src={`/thumb${item}.jpg`} fill className="object-cover" alt="thumb" /> */}
            </div>
          ))}
        </div>

        {/* --- CENTER COLUMN: MAIN IMAGE --- */}
        <div className="col-span-1 lg:col-span-5 w-full flex flex-col">
           {/* Main Image Container */}
           <div className="relative h-[40vh] md:h-[50vh] lg:h-[70vh] w-full mb-6 lg:mb-0 bg-white/5 rounded-xl lg:bg-transparent lg:rounded-none">
             <Image 
               src="/merch/merch2.jpeg" 
               alt="Oversized Hoodie Nirvana"
               fill
               className="object-contain p-4 lg:p-0 mix-blend-lighten"
               priority
             />
           </div>

           {/* --- MOBILE ONLY: THUMBNAILS (Horizontal Scroll) --- */}
           {/* This appears below the image only on small screens */}
           <div className="flex lg:hidden gap-3 overflow-x-auto pb-2 mb-2 no-scrollbar">
              {[1, 2, 3, 4].map((item) => (
                <div key={item} className="flex-shrink-0 w-16 h-16 bg-gray-800 border border-gray-700 rounded-md relative cursor-pointer active:scale-95 transition-transform">
                   {/* <Image src={`/thumb${item}.jpg`} fill className="object-cover rounded-md" alt="thumb" /> */}
                </div>
              ))}
           </div>
        </div>

        {/* --- RIGHT COLUMN: DETAILS --- */}
        <div className="col-span-1 lg:col-span-6 flex flex-col gap-5 lg:gap-6 pl-0 lg:pl-10">
          
          {/* Header */}
          <div>
            <h1 className="text-3xl md:text-5xl font-light tracking-wide mb-2 leading-tight">
              Oversized Hoodie <br className="hidden md:block" /> Nirvana
            </h1>
            <div className="flex items-center justify-between">
                <p className="text-gray-400 text-sm mt-1">Colour • Black</p>
                {/* Mobile Price moved here for better use of space, or keep below */}
            </div>
          </div>

          {/* Price */}
          <div className="text-2xl md:text-3xl font-bold text-white">
            Rs. 1,500
          </div>

          {/* Size Selector */}
          <div>
            <div className="flex justify-between text-sm mb-3">
              <span className="text-gray-300">Size • EU Men</span>
              <button className="underline text-gray-400 hover:text-white text-xs md:text-sm">Size Guide</button>
            </div>
            
            <div className="grid grid-cols-4 sm:grid-cols-5 lg:grid-cols-4 gap-2 md:gap-3">
              {sizes.map((size) => (
                <button
                  key={size}
                  onClick={() => setSelectedSize(size)}
                  className={`
                    py-2.5 px-1 text-sm border rounded-md transition-all duration-200
                    ${selectedSize === size 
                      ? "border-green-400 text-green-400 bg-green-400/10" 
                      : "border-gray-700 text-gray-400 hover:border-gray-400 hover:text-white bg-transparent"}
                  `}
                >
                  {size}
                </button>
              ))}
            </div>
          </div>

          {/* Description */}
          <div className="my-1">
            <h3 className="text-lg font-medium mb-2">Description</h3>
            <p className="text-gray-400 text-sm leading-relaxed max-w-full lg:max-w-md">
              Lorem ipsum dolor sit amet, consectetur adipiscing elit. Ut et massa mi. 
              Lorem ipsum dolor sit amet, consectetur adipiscing elit. 
            </p>
          </div>

          {/* Add to Cart Button */}
          {/* Added active:scale-95 for better mobile touch feedback */}
          <Link href="/cart" className="w-full mt-2">
            <button className="w-full bg-[#ff0080] hover:bg-[#d6006b] active:bg-[#b3005a] active:scale-[0.98] text-white font-bold py-4 uppercase tracking-wider rounded-lg transition-all shadow-[0_0_20px_rgba(255,0,128,0.4)]">
              Add to cart
            </button>
          </Link>

        </div>
      </div>

    </section>
  );
}