"use client";

import { useState } from "react";
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faChevronRight } from '@fortawesome/free-solid-svg-icons';
import { faChevronLeft } from '@fortawesome/free-solid-svg-icons';


export default function TimeCarousel({ cap }) {
  const [imgindex, setimgindex] = useState(0);

  function prevImg() {
    setimgindex(imgindex > 0 ? imgindex - 1 : cap.length - 1);
  }

  function nextImg() {
    setimgindex(imgindex < cap.length - 1 ? imgindex + 1 : 0);
  }

  return (
    <div>
      <div className="relative box-border w-[90vw] h-[55vw] mx-auto border-[0.7vw] overflow-hidden rounded-[3.3vw] border-solid border-[#e6287d]">
        <button
          onClick={nextImg}
          className="absolute top-1/2 transform -translate-y-1/2 left-0 hover:bg-opacity-50 p-[1.5vw] rounded-[50%]"
        >
          <FontAwesomeIcon
            icon={faChevronLeft}
            style={{ color: '#FFFFFF' }}
            className="text-[4vw]" 
          />
        </button>
        <button
          onClick={prevImg}
          className="absolute top-1/2 transform -translate-y-1/2 right-0 hover:bg-opacity-50 p-[1.5vw] rounded-[50%]"
        >
          <FontAwesomeIcon
            icon={faChevronRight}
            style={{ color: '#FFFFFF'}}
            className="text-[4vw]"
          />        
          </button>
        <img
          src={cap[imgindex].img}
          alt={cap[imgindex].title}
          className="w-full h-full object-cover"
        />
      </div>

      <div className="flex flex-row-reverse justify-center gap-[2vw] mt-[2vw] lg:text-xl font-bold w-full">
        {cap.map((item, index) => (
          <div
            key={item.key}
            className={`cursor-pointer ${imgindex === index ? "text-[#271d03]" : "text-[#96730b]"}`}
            onClick={() => setimgindex(index)}
          >
            {item.title}
          </div>
        ))}
      </div>
    </div>
  );
}