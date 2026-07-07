'use client';

import React, { useEffect, useState } from "react";
import '../app/globals.css';

interface TimeLeft {
  totalDays: number;
  hours: number;
  minutes: number;
  seconds: number;
}

function calculateTimeLeft(targetDate: string): TimeLeft {
  const difference = +new Date(targetDate) - +new Date();
  let timeLeft: TimeLeft = { totalDays: 0, hours: 0, minutes: 0, seconds: 0 }; 

  if (difference > 0) {
    const totalSeconds = Math.floor(difference / 1000);
    const totalMinutes = Math.floor(totalSeconds / 60);
    const totalHours = Math.floor(totalMinutes / 60);
    const totalDays = Math.floor(totalHours / 24); 

    timeLeft = {
      totalDays: totalDays, 
      hours: totalHours % 24,
      minutes: totalMinutes % 60,
      seconds: totalSeconds % 60,
    };
  }
  return timeLeft;
}

export default function TimerPage() {
  const targetDate = "2026-03-31T23:59:59";
  const [timeLeft, setTimeLeft] = useState<TimeLeft>(calculateTimeLeft(targetDate));
  const [isClient, setIsClient] = useState(false);

  useEffect(() => {
    setIsClient(true); 
    
    const timer = setInterval(() => {
      setTimeLeft(calculateTimeLeft(targetDate));
    }, 1000);
    
    return () => clearInterval(timer);
  }, []);

  // Hydration fix for SSR/Client mismatch
  if (!isClient) {
    const initialTime = calculateTimeLeft(targetDate);
    
    return (
      <div className="flex flex-col items-center justify-center text-center pb-7 font-audiowide">
        {/* Adjusted: Increased gap from gap-2 to gap-4 */}
        <div className="flex items-end gap-4 text-6xl font-extrabold tracking-wide">
          
          <div className="flex flex-col items-center">
            <span>{String(initialTime.totalDays).padStart(2, "0")}</span> 
            <span className="text-2xl font-medium mt-1">Days</span>
          </div>

          <span className="text-4xl pb-12 pl-6 pr-6">:</span> {/* Adjusted: Increased padding (pl-6 pr-6) */}

          <div className="flex flex-col items-center">
            <span>{String(initialTime.hours).padStart(2, "0")}</span>
            <span className="text-2xl font-medium mt-1">Hours</span>
          </div>

          <span className="text-4xl pb-12 pl-6 pr-6">:</span> {/* Adjusted: Increased padding (pl-6 pr-6) */}

          <div className="flex flex-col items-center">
            <span>{String(initialTime.minutes).padStart(2, "0")}</span>
            <span className="text-2xl font-medium mt-1">Minutes</span>
          </div>

          <span className="text-4xl pb-12 pl-6 pr-6">:</span> {/* Adjusted: Increased padding (pl-6 pr-6) */}

          <div className="flex flex-col items-center">
            <span>{String(initialTime.seconds).padStart(2, "0")}</span>
            <span className="text-2xl font-medium mt-1">Seconds</span>
          </div>
        </div>
      </div>
    );
  }

  // Client-rendered dynamic content
  return (
    <div className="flex flex-col items-center justify-center text-center pb-7 font-audiowide">
      {/* Adjusted: Increased gap from gap-2 to gap-4 */}
      <div className="flex items-end gap-4 text-6xl font-extrabold tracking-wide">
        
        {/* Days Display (Uses totalDays) */}
        <div className="flex flex-col items-center">
          <span>{String(timeLeft.totalDays).padStart(2, "0")}</span>
          <span className="text-2xl font-medium mt-1">Days</span>
        </div>

        <span className="text-4xl pb-12 pl-6 pr-6">:</span> {/* Adjusted: Increased padding (pl-6 pr-6) */}

        {/* Hours */}
        <div className="flex flex-col items-center">
          <span>{String(timeLeft.hours).padStart(2, "0")}</span>
          <span className="text-2xl font-medium mt-1">Hours</span>
        </div>

        <span className="text-4xl pb-12 pl-6 pr-6">:</span> {/* Adjusted: Increased padding (pl-6 pr-6) */}

        {/* Minutes */}
        <div className="flex flex-col items-center">
          <span>{String(timeLeft.minutes).padStart(2, "0")}</span>
          <span className="text-2xl font-medium mt-1">Minutes</span>
        </div>

        <span className="text-4xl pb-12 pl-6 pr-6">:</span> {/* Adjusted: Increased padding (pl-6 pr-6) */}

        {/* Seconds */}
        <div className="flex flex-col items-center">
          <span>{String(timeLeft.seconds).padStart(2, "0")}</span>
          <span className="text-2xl font-medium mt-1">Seconds</span>
        </div>
      </div>
    </div>
  );
}