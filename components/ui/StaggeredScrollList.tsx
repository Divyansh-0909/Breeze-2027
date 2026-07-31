"use client";

import React, { useEffect, useRef, useState } from "react";

export type ConnectingLine = {
  /** The SVG element as raw markup. Ensure paths do not have inline stroke-dasharray/offset so the wrapper can override them. */
  svgMarkup: React.ReactNode;
  /** e.g. "-10%" or "-50px" to align the line correctly relative to its item */
  offsetX?: string;
  /** e.g. "10%" or "20px" */
  offsetY?: string;
  /** Length of the path, large enough to cover the whole stroke */
  dasharrayValue?: number;
};

export function StaggeredList({ children }: { children: React.ReactNode }) {
  return (
    <div className="relative w-full flex flex-col">
      {children}
    </div>
  );
}

export function StaggeredListItem({
  children,
  index,
  connectingLine,
  isMobileBreakpoint = 768,
}: {
  children: React.ReactNode;
  index: number;
  connectingLine?: ConnectingLine;
  /** Hides the connecting line if viewport width is below this value */
  isMobileBreakpoint?: number;
}) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [progress, setProgress] = useState(0);
  const [isMobile, setIsMobile] = useState(true);

  // Responsive check
  useEffect(() => {
    const checkMedia = () => setIsMobile(window.innerWidth < isMobileBreakpoint);
    checkMedia();
    window.addEventListener("resize", checkMedia);
    return () => window.removeEventListener("resize", checkMedia);
  }, [isMobileBreakpoint]);

  // Scroll Progress Calculation
  useEffect(() => {
    if (!connectingLine || isMobile) return;

    let ticking = false;

    const updateProgress = () => {
      if (!containerRef.current) return;
      const rect = containerRef.current.getBoundingClientRect();
      const viewportHeight = window.innerHeight;

      // Starts when the bottom of the item's container reaches the bottom of the viewport
      // i.e., rect.bottom = viewportHeight => rect.top = viewportHeight - rect.height
      const scrollStart = viewportHeight - rect.height;
      
      // Completes when the top of the container reaches the top of the viewport
      // i.e., rect.top = 0
      const scrollEnd = 0;
      
      const maxScrollDistance = scrollStart - scrollEnd;

      let p = 0;

      if (maxScrollDistance > 0) {
        // Container is shorter than viewport
        p = ((scrollStart - rect.top) / maxScrollDistance) * 100;
      } else if (maxScrollDistance < 0) {
        // Container is taller than viewport (fallback logic)
        // Starts when top enters, ends when bottom leaves
        const start = viewportHeight;
        const end = -rect.height;
        p = ((start - rect.top) / (start - end)) * 100;
      } else {
        p = rect.top <= 0 ? 100 : 0;
      }

      // Clamp to 0-100
      p = Math.max(0, Math.min(100, p));
      
      setProgress(p);
      ticking = false;
    };

    const handleScroll = () => {
      if (!ticking) {
        window.requestAnimationFrame(updateProgress);
        ticking = true;
      }
    };

    window.addEventListener("scroll", handleScroll, { passive: true });
    window.addEventListener("resize", handleScroll, { passive: true });
    
    // Initial run
    updateProgress();

    return () => {
      window.removeEventListener("scroll", handleScroll);
      window.removeEventListener("resize", handleScroll);
    };
  }, [connectingLine, isMobile]);

  const dasharray = connectingLine?.dasharrayValue || 2000;
  // dasharray - (dasharray * progress) / 100
  const dashoffset = dasharray - (dasharray * progress) / 100;

  return (
    <div
      ref={containerRef}
      className="relative w-full"
      style={{ zIndex: index + 10 }}
    >
      {/* Item Content (higher z-index) */}
      <div className="relative z-10 w-full">
        {children}
      </div>

      {/* Connecting Line (lower z-index) */}
      {connectingLine && !isMobile && (
        <div
          className="absolute pointer-events-none"
          style={{
            zIndex: 0,
            top: "100%", // Start at the bottom of the container
            left: 0,
            width: "100%",
            transform: `translate(${connectingLine.offsetX || "0px"}, ${
              connectingLine.offsetY || "0px"
            })`,
          }}
        >
          {/* Wrap the SVG markup to inject dynamic CSS vars and styles */}
          <div
            className="staggered-line-wrapper"
            style={{
              "--dasharray": dasharray,
              "--dashoffset": dashoffset,
            } as React.CSSProperties}
          >
            <style>{`
              .staggered-line-wrapper path {
                stroke-dasharray: var(--dasharray);
                stroke-dashoffset: var(--dashoffset);
              }
            `}</style>
            {connectingLine.svgMarkup}
          </div>
        </div>
      )}
    </div>
  );
}
