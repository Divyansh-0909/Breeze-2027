import ScrollList from "./ScrollList";
import React from "react";

const Carousel = () => {
  return (
    <div className="w-full inline-flex overflow-hidden justify-center align-center bg-[#222] h-[152px] ">
        <ScrollList></ScrollList>
    </div>
  );
};

export default Carousel;