"use client";

import Image from "next/image";
import { useEffect, useState } from "react";

// Photo data with sizes and dispersed vertical positions
const photos = [
  { src: "/gallery/img-1.jpeg", width: 280, height: 380, top: 300 },
  { src: "/gallery/img-2.jpeg", width: 300, height: 420, top: 500 },
  { src: "/gallery/img-3.jpeg", width: 240, height: 320, top: 900 },
  { src: "/gallery/img-4.jpeg", width: 290, height: 400, top: 1100 },
  { src: "/gallery/img-5.jpeg", width: 260, height: 350, top: 1500 },
  { src: "/gallery/img-6.jpeg", width: 310, height: 430, top: 1650 },
  { src: "/gallery/img-7.jpeg", width: 270, height: 370, top: 2050 },
  { src: "/gallery/img-8.jpeg", width: 285, height: 390, top: 2250 },
  { src: "/gallery/img-9.jpeg", width: 255, height: 345, top: 2600 },
  { src: "/gallery/img-10.jpeg", width: 305, height: 420, top: 2800 },
];

export default function GalleryV2() {
  const [scrollY, setScrollY] = useState(0);
  const [dispersed, setDispersed] = useState(false);
  const [dispersionComplete, setDispersionComplete] = useState(false);
  const [galleryTop, setGalleryTop] = useState(0);
  const [viewportHeight, setViewportHeight] = useState(0);
  const [isInGallery, setIsInGallery] = useState(false);
  const galleryHeight = 3300;

  // Auto-disperse when component mounts and is in view
  useEffect(() => {
    const timer = setTimeout(() => {
      setDispersed(true);
      // Mark dispersion as complete after animation finishes
      setTimeout(() => {
        setDispersionComplete(true);
      }, 1500);
    }, 500); // Delay before dispersion starts

    return () => clearTimeout(timer);
  }, []);

  // Track scroll and gallery position
  useEffect(() => {
    const updateDimensions = () => {
      setViewportHeight(window.innerHeight);
      const galleryEl = document.getElementById("gallery-container");
      if (galleryEl) {
        const rect = galleryEl.getBoundingClientRect();
        setGalleryTop(window.scrollY + rect.top);
      }
    };

    const handleScroll = () => {
      const currentScroll = window.scrollY;
      setScrollY(currentScroll);
      
      // Check if we're within the gallery section
      const inGallery = currentScroll >= galleryTop && 
                        currentScroll < galleryTop + galleryHeight - viewportHeight;
      setIsInGallery(inGallery);
    };

    updateDimensions();
    window.addEventListener("scroll", handleScroll, { passive: true });
    window.addEventListener("resize", updateDimensions);
    handleScroll();
    
    return () => {
      window.removeEventListener("scroll", handleScroll);
      window.removeEventListener("resize", updateDimensions);
    };
  }, [galleryTop, viewportHeight]);

  // Calculate relative scroll within gallery section
  const relativeScroll = Math.max(0, scrollY - galleryTop);

  return (
    <div
      id="gallery-container"
      className="relative w-full bg-black"
      style={{ height: "3300px" }}
    >
      {/* Purple gradient circles for Breeze theme */}
      <div className="absolute inset-0 pointer-events-none z-0 overflow-hidden">
        <div
          className="absolute bg-purple-900 rounded-full opacity-40 blur-3xl"
          style={{ top: "-10%", right: "-5%", width: 400, height: 400 }}
        />
        <div
          className="absolute bg-pink-900 rounded-full opacity-30 blur-3xl"
          style={{ top: "30%", left: "-10%", width: 350, height: 350 }}
        />
        <div
          className="absolute bg-purple-800 rounded-full opacity-35 blur-3xl"
          style={{ bottom: "-5%", right: "20%", width: 300, height: 300 }}
        />
      </div>

      {/* Fixed centered text - only visible when gallery is in viewport */}
      {isInGallery && (
        <div
          className="fixed top-0 left-0 w-full h-screen flex items-center justify-center pointer-events-none"
          style={{ zIndex: 50 }}
        >
          <div className="relative text-center">
            <span className="block text-white text-5xl md:text-7xl lg:text-8xl tracking-[10px] font-bold uppercase">
              THE
            </span>
            <span className="block text-[#ff1fb7] text-6xl md:text-8xl lg:text-[140px] font-normal italic -mt-2 md:-mt-4">
              gallery
            </span>
          </div>
        </div>
      )}

      {/* Photo gallery */}
      <div className="absolute inset-0 w-full">
        {photos.map((photo, idx) => {
          // Calculate horizontal offset (alternating left/right)
          const leftPosition =
            idx % 2 === 0
              ? `${15 + ((idx * 7) % 20)}%`
              : `${55 + ((idx * 11) % 25)}%`;

          // Initial stacked position (center, near top)
          const initialTop = 200;
          const initialLeft = "50%";

          // Current position based on dispersion state
          const currentTop = dispersed ? photo.top : initialTop;
          const currentLeft = dispersed ? leftPosition : initialLeft;

          // Alternate z-index: some photos above text (z > 50), some below (z < 50)
          // Text has z-index 50, so use 60 for above and 40 for below
          // Indices 0, 3, 5, 6, 9 are above (5 is right-side)
          const photoZIndex = (idx % 3 === 0 || idx === 5) ? 60 : 40;

          // Scale based on scroll position (only after dispersion complete)
          let finalScale = 1;

          if (dispersionComplete) {
            // Shrink starts when top of photo touches viewport top
            // and completes when 50% of photo is scrolled out
            const photoTop = currentTop - photo.height / 2; // top edge of photo
            const distanceFromViewportTop = photoTop - relativeScroll;

            // Shrink distance is 50% of photo height
            const shrinkDistance = photo.height * 0.5;

            // Start shrinking when photo top reaches viewport top (distance = 0)
            // Complete shrinking when 50% is out (distance = -shrinkDistance)
            if (distanceFromViewportTop <= 0) {
              const shrinkProgress =
                Math.abs(distanceFromViewportTop) / shrinkDistance;
              finalScale = Math.max(1 - shrinkProgress, 0);
            }
          }

          return (
            <div
              key={idx}
              className="absolute"
              style={{
                top: `${currentTop}px`,
                left: currentLeft,
                transform: `translate(-50%, -50%) scale(${finalScale})`,
                transition: "top 1.5s ease-out, left 1.5s ease-out",
                zIndex: photoZIndex,
                transformOrigin: "center center",
              }}
            >
              <div className="overflow-hidden shadow-2xl">
                <Image
                  src={photo.src}
                  alt={`Gallery ${idx + 1}`}
                  width={photo.width}
                  height={photo.height}
                  className="block object-cover"
                  style={{
                    width: `${photo.width}px`,
                    height: `${photo.height}px`,
                  }}
                />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
