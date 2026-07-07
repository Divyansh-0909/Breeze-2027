
"use client";

import React, { useEffect, useState } from 'react';

export default function Flower() {
  const [rotation, setRotation] = useState(0);

  useEffect(() => {
    
    const interval = setInterval(() => {
      setRotation(prevRotation => prevRotation + 0.4); 
    }, 100); 

    
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="absolute overflow-hidden flex justify-center align-center items-center w-full " >
      <img
        src="/images/landing-page/landing/11.png"
        alt="Rotating Flower"
        className=" overflow-hidden w-[90vw] sm:w-[64vw] z-0 justify-center align-center items-center self-center "
        style={{
          transform: `rotate(${rotation}deg)`,
          transition: 'transform 0.5s linear', 
        }}
      />
    </div>
  );
}
