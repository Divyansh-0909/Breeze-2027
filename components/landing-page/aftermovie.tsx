"use client";

import { Fraunces, PT_Sans } from "next/font/google";
import localFont from "next/font/local";
import React, { useState } from "react";
import Image from "next/image";
import "../../app/globals.css";

const fraunces = Fraunces({
  subsets: ["latin"],
  display: "swap",
  weight: ["400"],
  style: ["normal", "italic"],
});

const ptSans = PT_Sans({
  subsets: ["latin"],
  display: "swap",
  weight: ["400"],
  style: ["normal"],
});

const acid = localFont({
  src: "../../public/fonts/acid-grotesk.woff",
  weight: "800",
  style: "normal",
});

interface AfterMovieProps {
  className?: string;
}

export default function AfterMovie({ className }: AfterMovieProps) {
  const [playVideo, setPlayVideo] = useState(false);

  return (
    <div className={`radial-bg ${className || ""}`}>
      {/* MODIFICATION HERE: Changed pt-8 to pt-16 and added pb-16 */}
      <div className="flex flex-col justify-center text-center pt-16 pb-16">
        <h1
          className={`${fraunces.className} text-[#FBC013] text-3xl sm:text-4xl md:text-5xl lg:text-6xl italic`}
        >
          Breeze ‘22 Aftermovie
        </h1>

        <div className="relative mt-8 md:mt-12 px-2 md:px-[10%]">
          <div className="relative w-full aspect-video rounded-xl overflow-hidden cursor-pointer bg-black">
            {!playVideo ? (
              /* Thumbnail */
              <div
                className="relative w-full h-full group"
                onClick={() => setPlayVideo(true)}
              >
                <Image
                  src="https://img.youtube.com/vi/etUeoHcrbQU/maxresdefault.jpg"
                  alt="Breeze 22 Aftermovie"
                  fill
                  className="object-cover"
                />

                {/* Dark overlay */}
                <div className="absolute inset-0 bg-black/40 group-hover:bg-black/50 transition" />

                {/* Play button */}
                <div className="absolute inset-0 flex items-center justify-center">
                  <div className="h-20 w-20 rounded-full bg-[#FBC013] flex items-center justify-center shadow-xl group-hover:scale-110 transition">
                    <svg
                      className="h-8 w-8 text-black ml-1"
                      fill="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path d="M8 5v14l11-7z" />
                    </svg>
                  </div>
                </div>
              </div>
            ) : (
              /* YouTube iframe (loads only after click) */
              <iframe
                src="https://www.youtube.com/embed/etUeoHcrbQU?autoplay=1"
                title="YouTube video player"
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                allowFullScreen
                className="w-full h-full"
              />
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
