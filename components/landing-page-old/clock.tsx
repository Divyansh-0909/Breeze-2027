"use client";

import { useState, useEffect } from 'react';

export default function CountdownTimer() {
  const targetDate = new Date('2025-02-14T00:00:00');

  const [timeLeft, setTimeLeft] = useState(calculateTimeLeft());

  useEffect(() => {
    const timer = setInterval(() => {
      setTimeLeft(calculateTimeLeft());
    }, 1000);

    return () => clearInterval(timer);
  }, []);

  const addLeadingZero = (num) => {
    return num < 10 ? `0${num}` : num;
  };

  function calculateTimeLeft() {
    const now = new Date();
    var difference = targetDate.getTime() - now.getTime();
    difference = difference / 1000;
    if (difference <= 0) return null;
    const SECONDS_IN_MINUTE = 60;
    const SECONDS_IN_HOUR = 60 * SECONDS_IN_MINUTE;
    const SECONDS_IN_DAY = 24 * SECONDS_IN_HOUR;
    const SECONDS_IN_MONTH = 30 * SECONDS_IN_DAY;

    var months = Math.floor(difference / SECONDS_IN_MONTH);
    difference %= SECONDS_IN_MONTH;
    var days = Math.floor(difference / SECONDS_IN_DAY);
    difference %= SECONDS_IN_DAY;
    var hours = Math.floor(difference / SECONDS_IN_HOUR);
    difference %= SECONDS_IN_HOUR;
    var minutes = Math.floor(difference / SECONDS_IN_MINUTE);
    difference %= SECONDS_IN_MINUTE;

    return {
      months: Math.floor(months),
      days: Math.floor(days),
      hours: Math.floor(hours),
      minutes: Math.floor(minutes),
      seconds: Math.floor(difference),
    };
  }

  return (
    <div>
      {timeLeft ? (
        <div className='bg-[#EC1B4B] px-[4vw] py-[2vw] rounded-[2vw] sm:rounded-[1vw]'>
          <div className='text-white text-[10vw] flex justify-center items-center gap-[1.5vw] font-elsie-swash-caps'>
            <div className='flex flex-col items-center justify-center text-[9vw]  font-fraunces-italic sm:text-[5vw] text-[#FADD98]'>
              <div>{addLeadingZero(timeLeft.months)}</div>
              <div className='text-[3.5vw] sm:text-[2vw] mt-[-2vw] text-[#FABF12] font-awesome-serif-italic'>months</div>
            </div>
            <div className='text-[6vw] relative bottom-[1vw] text-[#FABF12]'>:</div>
            <div className='flex flex-col items-center justify-center text-[9vw]  font-fraunces-italic sm:text-[5vw] text-[#FADD98]'>
              <div>{addLeadingZero(timeLeft.days)}</div>
              <div className='text-[3.5vw] sm:text-[2vw] mt-[-2vw] text-[#FABF12] font-awesome-serif-italic'>days</div>
            </div>
            <div className='text-[6vw] relative bottom-[1vw] text-[#FABF12]'>:</div>
            <div className='flex flex-col items-center justify-center text-[9vw]  font-fraunces-italic sm:text-[5vw] text-[#FADD98]'>
              <div>{addLeadingZero(timeLeft.hours)}</div>
              <div className='text-[3.5vw] sm:text-[2vw] mt-[-2vw] text-[#FABF12] font-awesome-serif-italic'>hours</div>
            </div>
            <div className='text-[6vw] relative bottom-[1vw] text-[#FABF12]'>:</div>
            <div className='flex flex-col items-center justify-center text-[9vw]  font-fraunces-italic sm:text-[5vw] text-[#FADD98]'>
              <div>{addLeadingZero(timeLeft.minutes)}</div>
              <div className='text-[3.5vw] sm:text-[2vw] mt-[-2vw] text-[#FABF12] font-awesome-serif-italic'>minutes</div>
            </div>
            <div className='text-[6vw] relative bottom-[1vw] text-[#FABF12]'>:</div>
            <div className='flex flex-col items-center justify-center text-[9vw]  font-fraunces-italic sm:text-[5vw] text-[#FADD98]'>
              <div>{addLeadingZero(timeLeft.seconds)}</div>
              <div className='text-[3.5vw] sm:text-[2vw] mt-[-2vw] text-[#FABF12] font-awesome-serif-italic'>seconds</div>
            </div>
          </div>
        </div>
      ) : (
        <div className='bg-[#EC1B4B] px-[4vw] py-[2vw] rounded-[2vw] sm:rounded-[1vw]'>
          <div className='text-white text-[10vw] flex justify-center items-center gap-[1.5vw] font-elsie-swash-caps'>
            <div className='flex flex-col items-center justify-center text-[9vw]  font-fraunces-italic sm:text-[5vw] text-[#FADD98]'>
              <div>00</div>
              <div className='text-[3.5vw] sm:text-[2vw] mt-[-2vw] text-[#FABF12] font-awesome-serif-italic'>months</div>
            </div>
            <div className='text-[6vw] relative bottom-[1vw] text-[#FABF12]'>:</div>
            <div className='flex flex-col items-center justify-center text-[9vw]  font-fraunces-italic sm:text-[5vw] text-[#FADD98]'>
              <div>00</div>
              <div className='text-[3.5vw] sm:text-[2vw] mt-[-2vw] text-[#FABF12] font-awesome-serif-italic'>days</div>
            </div>
            <div className='text-[6vw] relative bottom-[1vw] text-[#FABF12]'>:</div>
            <div className='flex flex-col items-center justify-center text-[9vw]  font-fraunces-italic sm:text-[5vw] text-[#FADD98]'>
              <div>00</div>
              <div className='text-[3.5vw] sm:text-[2vw] mt-[-2vw] text-[#FABF12] font-awesome-serif-italic'>hours</div>
            </div>
            <div className='text-[6vw] relative bottom-[1vw] text-[#FABF12]'>:</div>
            <div className='flex flex-col items-center justify-center text-[9vw]  font-fraunces-italic sm:text-[5vw] text-[#FADD98]'>
              <div>00</div>
              <div className='text-[3.5vw] sm:text-[2vw] mt-[-2vw] text-[#FABF12] font-awesome-serif-italic'>minutes</div>
            </div>
            <div className='text-[6vw] relative bottom-[1vw] text-[#FABF12]'>:</div>
            <div className='flex flex-col items-center justify-center text-[9vw]  font-fraunces-italic sm:text-[5vw] text-[#FADD98]'>
              <div>00</div>
              <div className='text-[3.5vw] sm:text-[2vw] mt-[-2vw] text-[#FABF12] font-awesome-serif-italic'>seconds</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}