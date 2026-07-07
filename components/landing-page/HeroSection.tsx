"use client";

import React, { useState, useEffect, useRef, useCallback } from "react";

export default function HeroSection() {
  const [timeLeft, setTimeLeft] = useState({
    months: 0,
    days: 0,
    hours: 0,
    minutes: 0,
    seconds: 0,
  });

  // Video loading states
  const [videoState, setVideoState] = useState<
    "idle" | "loading" | "canplay" | "playing" | "error"
  >("idle");
  const [isInView, setIsInView] = useState(false);
  const videoRef = useRef<HTMLVideoElement>(null);
  const sectionRef = useRef<HTMLElement>(null);

  // Countdown timer logic
  useEffect(() => {
    const target = new Date("2026-04-07T00:00:00");
    const updateTimer = () => {
      const now = new Date();
      const diff = target.getTime() - now.getTime();
      if (diff <= 0) {
        setTimeLeft({ months: 0, days: 0, hours: 0, minutes: 0, seconds: 0 });
        return;
      }
      const totalSeconds = Math.floor(diff / 1000);
      const seconds = totalSeconds % 60;
      const minutesTotal = Math.floor(totalSeconds / 60);
      const minutes = minutesTotal % 60;
      const hoursTotal = Math.floor(minutesTotal / 60);
      const hours = hoursTotal % 24;
      const daysTotal = Math.floor(hoursTotal / 24);
      // Approximate months using average month length (30.436875 days)
      const months = Math.floor(daysTotal / 30.436875);
      const days = Math.floor(daysTotal % 30.436875);
      setTimeLeft({ months, days, hours, minutes, seconds });
    };

    updateTimer();
    const interval = setInterval(updateTimer, 1000);
    return () => clearInterval(interval);
  }, []);

  // Intersection Observer - only load video when section is in view
  useEffect(() => {
    const section = sectionRef.current;
    if (!section) return;

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            setIsInView(true);
            observer.disconnect(); // Only need to trigger once
          }
        });
      },
      {
        rootMargin: "100px", // Start loading slightly before in view
        threshold: 0.1,
      }
    );

    observer.observe(section);
    return () => observer.disconnect();
  }, []);

  // Load and play video when in view
  useEffect(() => {
    const video = videoRef.current;
    if (!video || !isInView) return;

    setVideoState("loading");

    const handleCanPlay = () => {
      setVideoState("canplay");
      // Attempt to play the video
      video
        .play()
        .then(() => {
          setVideoState("playing");
        })
        .catch((error) => {
          console.log("Video autoplay failed:", error);
          // Still show the video even if autoplay fails
          setVideoState("canplay");
        });
    };

    const handleError = () => {
      console.error("Video failed to load");
      setVideoState("error");
    };

    const handlePlaying = () => {
      setVideoState("playing");
    };

    video.addEventListener("canplay", handleCanPlay);
    video.addEventListener("error", handleError);
    video.addEventListener("playing", handlePlaying);

    // Start loading the video
    video.load();

    return () => {
      video.removeEventListener("canplay", handleCanPlay);
      video.removeEventListener("error", handleError);
      video.removeEventListener("playing", handlePlaying);
    };
  }, [isInView]);

  const formatNum = (num: number) => num.toString().padStart(2, "0");

  // Determine if video should be visible (hide during loading for smooth transition)
  const showVideo = videoState === "canplay" || videoState === "playing";

  return (
    <section
      ref={sectionRef}
      className="relative h-[100vh] overflow-hidden rounded-bl-[20vh] rounded-br-[20vh]"
    >
      {/* Fallback gradient background - always visible as base layer */}
      <div className="absolute inset-0 z-0 hero-bg bg-gradient-to-br from-purple-900 via-purple-800 to-indigo-900" />

      {/* Loading shimmer effect - visible while loading */}
      {videoState === "loading" && (
        <div className="absolute inset-0 z-[1] overflow-hidden">
          <div
            className="absolute inset-0 bg-gradient-to-r from-transparent via-white/5 to-transparent animate-shimmer"
            style={{
              animation: "shimmer 2s infinite",
              backgroundSize: "200% 100%",
            }}
          />
        </div>
      )}

      {/* Video Background - only render when in view */}
      {isInView && (
        <video
          ref={videoRef}
          className={`absolute inset-0 w-full h-full object-cover z-[2] transition-opacity duration-1000 ${
            showVideo ? "opacity-100" : "opacity-0"
          }`}
          autoPlay
          loop
          muted
          playsInline
          preload="metadata"
          // Poster could be added here if you have a poster image
          // poster="/hero-poster.jpg"
        >
          {/* Primary high-resolution source */}
          <source src="/hero-video-high-resolution.mp4" type="video/mp4" />
          {/* Fallback to smaller video if high-res fails */}
          {/* <source src="/hero-video.mp4" type="video/mp4" /> */}
          {/* Your browser does not support the video tag. */}
        </video>
      )}

      {/* Gradient overlay for better text visibility */}
      <div className="absolute inset-0 z-[5] bg-gradient-to-b from-black/30 via-transparent to-black/40 pointer-events-none" />

      {/* Purple gradient overlay matching original design */}
      <div className="absolute inset-0 z-[6] bg-gradient-to-t from-purple-900/50 via-transparent to-transparent pointer-events-none" />

      {/* Content Layer */}
      <div className="absolute inset-0 z-10 flex flex-col items-center justify-center text-center px-4">
        {/* Countdown Timer */}
        <div className="flex items-center gap-8">
          <div className="flex flex-col items-center">
            <span className="timer-number text-9xl font-bold text-white">
              {formatNum(timeLeft.months)}
            </span>
            <span className="text-white text-lg mt-4">months</span>
          </div>
          <span className="text-6xl text-white opacity-80">:</span>
          <div className="flex flex-col items-center">
            <span className="timer-number text-9xl font-bold text-white">
              {formatNum(timeLeft.days)}
            </span>
            <span className="text-white text-lg mt-4">days</span>
          </div>
          <span className="text-6xl text-white opacity-80">:</span>
          <div className="flex flex-col items-center">
            <span className="timer-number text-9xl font-bold text-white">
              {formatNum(timeLeft.hours)}
            </span>
            <span className="text-white text-lg mt-4">hours</span>
          </div>
          <span className="text-6xl text-white opacity-80">:</span>
          <div className="flex flex-col items-center">
            <span className="timer-number text-9xl font-bold text-white">
              {formatNum(timeLeft.minutes)}
            </span>
            <span className="text-white text-lg mt-4">minutes</span>
          </div>
          <span className="text-6xl text-white opacity-80">:</span>
          <div className="flex flex-col items-center">
            <span className="timer-number text-9xl font-bold text-white">
              {formatNum(timeLeft.seconds)}
            </span>
            <span className="text-white text-lg mt-4">seconds</span>
          </div>
        </div>
      </div>

      {/* Shimmer animation keyframes */}
      <style jsx>{`
        @keyframes shimmer {
          0% {
            background-position: -200% 0;
          }
          100% {
            background-position: 200% 0;
          }
        }
        .animate-shimmer {
          background: linear-gradient(
            90deg,
            transparent 0%,
            rgba(255, 255, 255, 0.05) 50%,
            transparent 100%
          );
          background-size: 200% 100%;
        }
      `}</style>
    </section>
  );
}
