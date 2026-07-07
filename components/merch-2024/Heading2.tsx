import React from "react";
import DropDownButton from "./DropDownButtons";

const Heading2 = () => {
  return (
    <div className="flex flex-col gap-2 sm:gap-1 m-10 mb-0">
      <h1 className="text-2xl font-normal">OUR MERCH</h1>
      <div className="flex justify-between items-center flex-wrap sm:flex-nowrap sm:gap-5 gap-3 ">
        <p
          className="text-5xl font-thin font-fraunces-italic-bold"
        >
          Checkout The Entire Collection!
        </p>
        <div className="flex justify-center items-center">
          <DropDownButton></DropDownButton>
        </div>
      </div>
    </div>
  );
};

export default Heading2;
