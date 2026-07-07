"use client";

import React, { useEffect, useState, useRef } from "react";

interface StatProps {
  label: string;
  target: number;
  suffix?: string;
  isVisible: boolean;
}

const AnimatedNumber = ({
  target,
  suffix = "+",
  isVisible,
}: {
  target: number;
  suffix?: string;
  isVisible: boolean;
}) => {
  const [display, setDisplay] = useState("0");
  const hasAnimated = useRef(false);

  useEffect(() => {
    if (!isVisible || hasAnimated.current) return;

    hasAnimated.current = true;
    let start = 0;
    const duration = 1500; // faster animation
    const stepTime = 16; // ~60fps
    const totalSteps = duration / stepTime;
    const increment = target / totalSteps;

    const timer = setInterval(() => {
      start += increment;
      if (start >= target) {
        start = target;
        clearInterval(timer);
      }
      setDisplay(Math.floor(start).toLocaleString("en-IN") + suffix);
    }, stepTime);

    return () => clearInterval(timer);
  }, [target, suffix, isVisible]);

  return (
    <div className="relative w-[180px] sm:w-[220px] md:w-[260px] h-[80px] sm:h-[90px] md:h-[100px] flex items-center justify-center">
      <span className="absolute text-5xl sm:text-6xl md:text-7xl font-extrabold text-orange-500 leading-none select-none">
        {display}
      </span>
    </div>
  );
};

const StatItem = ({ label, target, suffix, isVisible }: StatProps) => (
  <div className="flex flex-col items-center justify-center text-center space-y-3">
    <AnimatedNumber target={target} suffix={suffix} isVisible={isVisible} />
    <p className="text-white text-2xl sm:text-3xl md:text-4xl lg:text-5xl font-semibold">
      {label}
    </p>
  </div>
);

export default function StatsSection() {
  const sectionRef = useRef<HTMLElement>(null);
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true);
          observer.disconnect(); // Only trigger once
        }
      },
      { threshold: 0.3 } // Trigger when 30% visible
    );

    if (sectionRef.current) {
      observer.observe(sectionRef.current);
    }

    return () => observer.disconnect();
  }, []);

  return (
    <section
      ref={sectionRef}
      className="relative w-full bg-gradient-to-b from-black via-neutral-950 to-black text-white py-24"
    >
      <div className="max-w-7xl mx-auto px-6 flex flex-col sm:flex-row justify-evenly items-center gap-16 sm:gap-20 md:gap-24">
        <StatItem
          label="Social media reach"
          target={500000}
          isVisible={isVisible}
        />
        <StatItem label="Registrations" target={2500} isVisible={isVisible} />
        <StatItem label="Footfall" target={27000} isVisible={isVisible} />
      </div>
    </section>
  );
}
