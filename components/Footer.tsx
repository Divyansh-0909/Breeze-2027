// components/Footer.tsx
"use client";

import React, { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import SocialLinks from "./sociallinks";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faLocationDot } from "@fortawesome/free-solid-svg-icons";

const BracketHeader = ({ text }: { text: string }) => {
  const [isOpen, setIsOpen] = useState(false);
  const ref = useRef(null);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) setIsOpen(true);
      },
      { threshold: 0.1 }
    );
    if (ref.current) observer.observe(ref.current);
    return () => observer.disconnect();
  }, []);

  return (
    <div
      ref={ref}
      className="font-mono text-sm uppercase tracking-widest flex items-center overflow-hidden transition-all duration-1000 ease-out"
      style={{ maxWidth: isOpen ? "100%" : "20px", opacity: isOpen ? 1 : 0.3 }}
    >
      <span className="shrink-0 text-white">[</span>
      <span
        className={`px-3 whitespace-nowrap transition-all duration-700 delay-200 text-white ${
          isOpen ? "opacity-100 translate-x-0" : "opacity-0 -translate-x-4"
        }`}
      >
        {text}
      </span>
      <span className="shrink-0 text-white">]</span>
    </div>
  );
};

export default function Footer({
  className = "",
  nextPage = "/",
}: {
  className?: string;
  nextPage?: string;
}) {
  const router = useRouter();
  const [hasMounted, setHasMounted] = useState(false);
  const [progress, setProgress] = useState(0);
  const [visible, setVisible] = useState(false);
  const [loadingNext, setLoadingNext] = useState(false);
  const [blurAmount, setBlurAmount] = useState(0);

  const footerRef = useRef<HTMLDivElement | null>(null);
  const letterRefs = useRef<(HTMLSpanElement | null)[]>([]);
  const overscrollAcc = useRef(0);
  const touchStartY = useRef(0);
  const decreaseTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const animationFrameRef = useRef<number | null>(null);
  const isDecreasingRef = useRef(false);
  const OVERSCROLL_THRESHOLD = 800;

  // Fix Hydration Error: Only render logic after mount
  useEffect(() => {
    setHasMounted(true);
  }, []);

  // Reset progress bar state when route changes
  useEffect(() => {
    setProgress(0);
    setVisible(false);
    setLoadingNext(false);
    setBlurAmount(0);
    overscrollAcc.current = 0;
  }, [nextPage]);

  useEffect(() => {
    if (!hasMounted) return;

    const handleNavigation = () => {
      setLoadingNext(true);
      router.push(nextPage);
    };

    const stopDecrease = () => {
      isDecreasingRef.current = false;
      if (decreaseTimerRef.current) {
        clearTimeout(decreaseTimerRef.current);
        decreaseTimerRef.current = null;
      }
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
        animationFrameRef.current = null;
      }
    };

    const runDecrease = () => {
      if (!isDecreasingRef.current) return;

      overscrollAcc.current = Math.max(0, overscrollAcc.current - 20);
      const newProgress = (overscrollAcc.current / OVERSCROLL_THRESHOLD) * 100;
      setProgress(newProgress);

      if (overscrollAcc.current <= 0) {
        stopDecrease();
        setProgress(0);
        setVisible(false);
      } else {
        animationFrameRef.current = requestAnimationFrame(runDecrease);
      }
    };

    const startDecreaseTimer = () => {
      stopDecrease();

      if (overscrollAcc.current <= 0) return;

      decreaseTimerRef.current = setTimeout(() => {
        isDecreasingRef.current = true;
        animationFrameRef.current = requestAnimationFrame(runDecrease);
      }, 800);
    };

    const updateProgress = (delta: number) => {
      if (loadingNext) return;

      const isAtBottom =
        window.innerHeight + window.scrollY >=
        document.documentElement.scrollHeight - 50;

      // User is scrolling down at the bottom - increase progress
      if (isAtBottom && delta > 0) {
        stopDecrease();

        setVisible(true);
        overscrollAcc.current += delta;
        const nextProgress = Math.min(
          (overscrollAcc.current / OVERSCROLL_THRESHOLD) * 100,
          100
        );
        setProgress(nextProgress);

        if (nextProgress >= 100) {
          handleNavigation();
        } else {
          startDecreaseTimer();
        }
      }
      // User scrolls up - start decrease timer
      else if (delta < 0 && overscrollAcc.current > 0) {
        startDecreaseTimer();
      }
    };

    const onWheel = (e: WheelEvent) => {
      updateProgress(e.deltaY);
    };
    const onTouchStart = (e: TouchEvent) => {
      touchStartY.current = e.touches[0].clientY;
    };
    const onTouchMove = (e: TouchEvent) => {
      const deltaY = touchStartY.current - e.touches[0].clientY;
      const isAtBottom =
        window.innerHeight + window.scrollY >=
        document.documentElement.scrollHeight - 80;
      if (isAtBottom && deltaY > 0) {
        if (e.cancelable) e.preventDefault();
        updateProgress(deltaY * 2);
      } else if (deltaY < 0) {
        updateProgress(deltaY);
      }
      touchStartY.current = e.touches[0].clientY;
    };
    const onTouchEnd = () => {
      if (
        overscrollAcc.current > 0 &&
        overscrollAcc.current < OVERSCROLL_THRESHOLD
      ) {
        startDecreaseTimer();
      }
    };

    window.addEventListener("wheel", onWheel, { passive: false });
    window.addEventListener("touchstart", onTouchStart, { passive: true });
    window.addEventListener("touchmove", onTouchMove, { passive: false });
    window.addEventListener("touchend", onTouchEnd);

    return () => {
      window.removeEventListener("wheel", onWheel);
      window.removeEventListener("touchstart", onTouchStart);
      window.removeEventListener("touchmove", onTouchMove);
      window.removeEventListener("touchend", onTouchEnd);
      stopDecrease();
    };
  }, [hasMounted, router, loadingNext, nextPage]);

  useEffect(() => {
    const handleScroll = () => {
      if (!footerRef.current) return;
      const rect = footerRef.current.getBoundingClientRect();
      const footerHeight = rect.height;
      // Calculate how much of the footer is visible in the viewport
      const visibleHeight = Math.min(
        window.innerHeight - rect.top,
        footerHeight
      );
      const visibilityRatio = visibleHeight / footerHeight;

      // Only start blur effect when footer is 75% visible (visibilityRatio >= 0.75)
      // Then scale the blur from 0 to 15 based on remaining 25% visibility
      if (visibilityRatio >= 0.75) {
        // Map 0.75-1.0 visibility to 0-1 for blur calculation
        const blurProgress = (visibilityRatio - 0.75) / 0.25;
        setBlurAmount(blurProgress * 15);
      } else {
        setBlurAmount(0);
      }
    };
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  // Letter animation effect for BREEZE text - just make visible and enable hover
  useEffect(() => {
    if (!hasMounted) return;

    const footerObserver = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting) {
          letterRefs.current.forEach((ref, index) => {
            if (!ref) return;
            
            // Staggered visibility - each letter appears slightly after the previous
            setTimeout(() => {
              ref.style.opacity = '1';
              ref.style.transform = 'translateY(0)';
              ref.classList.add("letter-visible");
              ref.classList.add("letter-hover-enabled");
            }, index * 50);
          });
          footerObserver.unobserve(entries[0].target);
        }
      },
      { threshold: 0.2 }
    );

    const parent = letterRefs.current[0]?.parentElement;
    if (parent) {
      footerObserver.observe(parent);
    }

    return () => {
      footerObserver.disconnect();
    };
  }, [hasMounted]);

  // Hydration Guard
  if (!hasMounted) return null;

  return (
    <>
      {/* Blur Overlay */}
      <div
        className="fixed inset-0 pointer-events-none z-20"
        style={{
          backdropFilter: `blur(${blurAmount}px)`,
          WebkitBackdropFilter: `blur(${blurAmount}px)`,
          background: `linear-gradient(to bottom, rgba(0,0,0,${Math.min(
            blurAmount / 50,
            0.2
          )}) 0%, transparent 100%)`,
          transition: "backdrop-filter 0.3s ease-out",
        }}
      />

      {/* Progress Indicator */}
      <div
        className={`fixed bottom-6 left-1/2 -translate-x-1/2 md:translate-x-0 md:left-auto md:bottom-10 md:right-10 z-[100] flex items-center gap-4
        text-white text-[10px] tracking-[0.3em] font-bold transition-all duration-500 whitespace-nowrap
        ${
          visible
            ? "opacity-100 translate-y-0"
            : "opacity-0 translate-y-4 pointer-events-none"
        }`}
      >
        <span>NEXT PAGE</span>
        <div className="relative w-16 md:w-20 h-[2px] bg-white/20 overflow-hidden">
          <div
            className="absolute h-full bg-white transition-all duration-150 ease-out"
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>

      <footer
        ref={footerRef}
        id="contact"
        className={`relative w-full flex flex-col z-30 scroll-mt-[90px] ${className}`}
        style={{ background: "linear-gradient(to top, #2a003e 0%, #000 100%)" }}
      >
        <div className="w-full px-6 sm:px-10 md:px-16 lg:px-24 py-12 md:py-16 lg:py-20 z-10">
          <div className="flex flex-col gap-12 md:gap-16">
            {/* Row 1: Tagline + Get In Touch */}
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 md:gap-8">
              <div className="space-y-0.5 md:space-y-1">
                <p className="text-sm sm:text-lg md:text-xl lg:text-2xl xl:text-3xl tracking-[0.15em] md:tracking-[0.2em] uppercase text-white/80 font-medium">
                  The Flagship Techno
                </p>
                <p className="text-sm sm:text-lg md:text-xl lg:text-2xl xl:text-3xl tracking-[0.15em] md:tracking-[0.2em] uppercase text-white/80 font-medium">
                  Cultural Fest of SNU
                </p>
              </div>

              <a
                href="/get-in-touch"
                className="inline-block hover:opacity-80 transition-opacity"
              >
                <span className="text-xl sm:text-2xl md:text-3xl lg:text-4xl font-bold text-white uppercase tracking-wider hover:text-purple-300 transition-colors">
                  Get In Touch →
                </span>
              </a>
            </div>

            {/* Row 2: Location + Find Us At */}
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 md:gap-8">
              <a
                href="https://maps.app.goo.gl/efznnSuGsLuSqLFm7"
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-3 group hover:opacity-80 transition-opacity"
              >
                <FontAwesomeIcon 
                  icon={faLocationDot} 
                  className="text-2xl sm:text-3xl md:text-4xl text-purple-400 group-hover:text-purple-300 transition-colors" 
                />
                <span className="text-sm sm:text-base md:text-lg lg:text-xl text-white/80 group-hover:text-white transition-colors">
                  Shiv Nadar University, Greater Noida
                </span>
              </a>

              <div className="flex flex-col items-start md:items-end space-y-3 md:space-y-4">
                <span className="text-lg sm:text-xl md:text-2xl lg:text-3xl font-bold text-white uppercase tracking-wider">
                  Find Us At
                </span>
                <SocialLinks />
              </div>
            </div>
          </div>
        </div>

        {/* Animated BREEZE Text - Outside padded container */}
        <style jsx global>{`
          .scroll-letter {
            opacity: 0;
            transform: translateY(80px);
            will-change: transform, opacity, top;
            cursor: pointer;
            text-shadow: 0 0 8px rgba(255, 255, 255, 0.3);
            transition: top 0.3s ease-out !important;
          }
          .letter-visible {
            text-shadow: 0 0 8px rgba(255, 255, 255, 0.3);
          }
          .letter-hover-enabled {
            transition: top 0.3s ease-out !important;
          }
          .letter-hover-enabled:hover {
            text-shadow: 0 0 15px rgba(255, 255, 255, 0.8);
            color: #e9fff9;
          }

          @media (max-width: 768px) {
            .scroll-letter { font-size: 10rem !important; }
          }
          @media (max-width: 640px) {
            .scroll-letter { font-size: 7rem !important; }
          }
          @media (max-width: 480px) {
            .scroll-letter { font-size: 5rem !important; margin: 0 -1px; }
          }
        `}</style>

        <div
          className="hidden lg:block relative w-full h-56 overflow-hidden"
        >
          <div
            className="absolute inset-x-0 bottom-0 flex justify-center items-start md:text-[10rem] lg:text-[15rem] xl:text-[20rem] tracking-wider font-bold"
            style={{ perspective: "1000px", fontFamily: "'Chathura', sans-serif", top: "0px" }}
          >
            {"BREEZE".split("").map((letter, index) => (
              <span
                key={index}
                ref={(el: HTMLSpanElement | null): void => {
                  letterRefs.current[index] = el;
                }}
                className="scroll-letter h-auto relative -top-20 hover:-top-28 text-white"
              >
                {letter}
              </span>
            ))}
          </div>
        </div>
      </footer>
    </>
  );
}
