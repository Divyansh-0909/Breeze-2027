"use client";
import React from "react";

/**
 * Performance-Optimized Dark Graffiti Backdrop
 * 
 * Reverted to a moody, dark background based on user feedback.
 * Removed SVG filters (feTurbulence, drop-shadows) and backdrop-blur
 * to completely eliminate scroll lag.
 */
export default function SectionGraffitiBackdrop() {
  return (
    <div className="absolute inset-0 overflow-hidden pointer-events-none z-0 bg-[#04060e]">
      
      {/* 
        Container for parallax to hook into. 
        will-change: transform added for GPU acceleration.
      */}
      <div className="parallax-graffiti absolute top-[-5%] left-0 right-0 bottom-[-5%]" style={{ willChange: "transform" }}>
        <svg width="100%" height="100%" className="absolute inset-0">
          <defs>
            <pattern id="chalk-mural" width="800" height="800" patternUnits="userSpaceOnUse">
              {/* Subtle line art matching the "dark" graffiti style from the tunnel ceiling */}
              <g stroke="rgba(244, 239, 226, 0.06)" strokeWidth="2" fill="none" strokeLinejoin="round" strokeLinecap="round">
                {/* Big scribbles */}
                <path d="M 100,-100 C 400,-50 600,200 400,500 C 200,800 0,600 -100,300 Z" />
                <path d="M 400,200 L 550,50 L 700,250 L 900,150 L 800,450 L 950,600 L 650,500 L 550,750 L 450,450 Z" />
                <path d="M -200,600 C 100,550 300,900 500,800 C 700,700 800,1000 600,1100 C 400,1200 0,900 -200,800 Z" />
                
                {/* Eyes */}
                <circle cx="200" cy="200" r="70" />
                <circle cx="200" cy="200" r="30" />
                <circle cx="580" cy="220" r="45" />
                <circle cx="580" cy="220" r="15" />
                <circle cx="350" cy="780" r="60" />
                <circle cx="350" cy="780" r="25" />
                
                {/* Text tags */}
                <text x="450" y="700" fill="rgba(244, 239, 226, 0.04)" stroke="none" fontSize="70" fontFamily="'Impact', sans-serif" transform="rotate(-15 450 700)">बोल</text>
                <text x="50" y="650" fill="rgba(244, 239, 226, 0.04)" stroke="none" fontSize="90" fontFamily="'Impact', sans-serif" transform="rotate(25 50 650)">GULLY</text>
                
                {/* Paint drips */}
                <path d="M 500,300 L 500,380 M 750,550 L 750,620 M 850,400 L 850,500" strokeWidth="6" />
              </g>

              {/* Faint, flat color washes (using opacity instead of blur for performance) */}
              <circle cx="200" cy="200" r="150" fill="rgba(208, 57, 44, 0.03)" />
              <circle cx="600" cy="600" r="200" fill="rgba(31, 95, 208, 0.02)" />
              <circle cx="100" cy="700" r="250" fill="rgba(214, 53, 127, 0.02)" />
            </pattern>
          </defs>

          {/* Render the tiling mural */}
          <rect width="100%" height="100%" fill="url(#chalk-mural)" />
        </svg>
      </div>
      
      {/* 
        Vignette overlay to keep the center focused and edges dark.
      */}
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,_rgba(4,6,14,0)_0%,_#04060e_100%)] pointer-events-none" />

    </div>
  );
}
