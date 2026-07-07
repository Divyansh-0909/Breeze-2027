"use client";

import { useState } from "react";
import merch from "@/components/landing-page-old/merchList";
import { ScrollArea, ScrollBar } from "@/components/ui/scroll-area";

export default function ProCard() {
  const [selectedCategory, setSelectedCategory] = useState("best");

  const filteredMerch =
    selectedCategory === "All"
      ? merch
      : merch.filter((item) => item.cat.includes(selectedCategory));

  return (
    <div className="flex flex-col ">
      <div className="flex gap-2 pt-2 flex-wrap justify-start md:pb-8 pl-4">
        {["All", "winter", "new", "best", "women's", "luxuary"].map(
          (category) => (
            <button
              key={category}
              onClick={() => setSelectedCategory(category)}
              className={`border-black lg:py-1 lg:px-4 rounded-3xl md:text-[14px] text-[12px] px-2  ${
                selectedCategory === category
                  ? "bg-[#FABF12] text-white border-0"
                  : "bg-white border-2"
              }`}
            >
              {category === "All"
                ? "All"
                : category.charAt(0).toUpperCase() +
                  category.slice(1) +
                  " Collection"}
            </button>
          )
        )}
      </div>

      <div>
        <ScrollArea className="w-full px-2 overflow-x-auto">
          <div
            className="
                            mb-4 gap-4 
                            md:flex md:flex-nowrap  
                            grid grid-rows-2 auto-cols-max gap-0  
                        "
            style={{ gridAutoFlow: "column" }}
          >
            {filteredMerch.map((item) => (
              <div
                key={item.key}
                className="flex flex-col p-4 w-[220px] md:w-[250px] h-[300px] md:h-auto lg:w-[300px] xl:w-[375px]"
              >
                <div className="border-2 rounded-3xl border-black w-full h-[300px] md:h-[250px] xl:h-[400px] lg:h-[300px] ">
                  <img
                    src=""
                    alt=""
                    className="w-full h-full object-cover rounded-t-lg"
                  />
                </div>
                <div className="mt-2 font-bold text-[15px] xl:text-[20px]">
                  {item.title}
                </div>
                <div className="text-gray-600  text-xs lg:text-[16px]">
                  ${item.price}
                </div>
              </div>
            ))}
          </div>
          <ScrollBar orientation="horizontal" />
        </ScrollArea>
      </div>
    </div>
  );
}
