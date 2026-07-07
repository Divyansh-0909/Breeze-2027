"use client";

import { useLayoutEffect, useRef } from "react";
import Image from "next/image";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";

// Ensure plugin is registered
gsap.registerPlugin(ScrollTrigger);

export default function MerchScroll() {
  const containerRef = useRef<HTMLDivElement>(null);
  const overlayWrapperRef = useRef<HTMLDivElement>(null);
  const gridWrapperRef = useRef<HTMLDivElement>(null);

  useLayoutEffect(() => {
    const ctx = gsap.context(() => {
      // --- INITIAL STATES ---
      gsap.set(overlayWrapperRef.current, { width: 0, height: 0 });
      gsap.set(gridWrapperRef.current, { width: 0, height: 0, opacity: 0 });

      const tl = gsap.timeline({
        scrollTrigger: {
          trigger: containerRef.current,
          start: "top top",
          end: "+=200%", 
          pin: true,     
          scrub: 1,      
          anticipatePin: 1,
          // Mobile Optimization: prevents jitter on touch scroll
          fastScrollEnd: true, 
        },
      });

      // --- VISIBILITY SNAP (Instant On/Off) ---
      tl.to(gridWrapperRef.current, { opacity: 1, duration: 0 }, 0.005);

      // --- STAGE 1: Expand to Square ---
    
      tl.to([overlayWrapperRef.current, gridWrapperRef.current], {
        width: "35vh", // Initial square size
        height: "35vh",
        duration: 3,
        ease: "none",
      }, 0); 

      // --- STAGE 2: Expand to Full Screen ---
      tl.to([overlayWrapperRef.current, gridWrapperRef.current], {
        width: "100vw",
        height: "100vh", 
        duration: 7,
        ease: "none",
      });
      
    }, containerRef);

    return () => ctx.revert();
  }, []);

  const gridColor = "border-blue-600";
  const dotColor = "bg-blue-600";
  // Responsive dots: smaller on mobile
  const cornerSize = "w-1 h-1 md:w-2 md:h-2";

  return (
    <section
      ref={containerRef}
      // Use min-h-[100dvh] for mobile browser address bar support
      className="relative min-h-[100dvh] w-full bg-[#f2f2f2] overflow-hidden flex items-center justify-center"
    >
      {/* --- LAYER 1: BACKGROUND --- */}
      <div className="absolute inset-0 z-0 w-full h-full">
        <Image
          src="/merch/merch1.jpeg"
          alt="Merch Background"
          fill
          className="object-cover"
          priority 
        />
      </div>

      {/* --- LAYER 2: EXPANDING IMAGE CONTAINER --- */}
      <div
        ref={overlayWrapperRef}
        // Added 'will-change-transform' and max-width for mobile safety
        className="relative z-20 overflow-hidden flex items-center justify-center bg-black shadow-2xl will-change-[width,height]"
        style={{ width: "0px", height: "0px" }}
      >
        <div className="absolute inset-0 z-0">
          <Image
            src="/merch/merch2.jpeg"
            alt="Merch Detail"
            fill
            className="object-cover object-center"
          />
        </div>
      </div>

      {/* --- LAYER 3: GRID CONTAINER --- */}
      <div
        ref={gridWrapperRef}
        // Added 'will-change-transform'
        className="absolute z-30 flex items-center justify-center pointer-events-none will-change-[width,height]"
        style={{ width: "0px", height: "0px", opacity: 0 }} 
      >
        
        {/* --- INFINITE LINES --- */}
        {/* We use border-[1.5px] on mobile (default) and 2px on desktop (md:) for cleaner look */}
        
        {/* Top Line */}
        <div className={`absolute top-0 left-1/2 -translate-x-1/2 w-[200vw] border-t-[1.5px] md:border-t-[2px] border-dashed ${gridColor} opacity-80`} />
        
        {/* Bottom Line */}
        <div className={`absolute bottom-0 left-1/2 -translate-x-1/2 w-[200vw] border-b-[1.5px] md:border-b-[2px] border-dashed ${gridColor} opacity-80`} />
        
        {/* Left Line */}
        <div className={`absolute left-0 top-1/2 -translate-y-1/2 h-[200vh] border-l-[1.5px] md:border-l-[2px] border-dashed ${gridColor} opacity-80`} />
        
        {/* Right Line */}
        <div className={`absolute right-0 top-1/2 -translate-y-1/2 h-[200vh] border-r-[1.5px] md:border-r-[2px] border-dashed ${gridColor} opacity-80`} />


        {/* --- CORNER DOTS --- */}
        <div className={`absolute top-0 left-0 ${cornerSize} ${dotColor} -translate-x-1/2 -translate-y-1/2`} />
        <div className={`absolute top-0 right-0 ${cornerSize} ${dotColor} translate-x-1/2 -translate-y-1/2`} />
        <div className={`absolute bottom-0 left-0 ${cornerSize} ${dotColor} -translate-x-1/2 translate-y-1/2`} />
        <div className={`absolute bottom-0 right-0 ${cornerSize} ${dotColor} translate-x-1/2 translate-y-1/2`} />

      </div>
    </section>
  );
}