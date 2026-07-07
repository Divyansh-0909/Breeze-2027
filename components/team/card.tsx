import React from "react";
import Image from "next/image";

type BoxProps = {
  name: string;
  title: string;
  img?: string;
};

export default function Box({ name, title, img }: BoxProps) {
  return (
    <div className="grid w-[266.4px] h-[381px] grid-cols-[2fr_1fr_1fr] grid-rows-[16fr_1fr_1fr] lg:w-[280px] lg:h-[401px] xl:w-[333px] xl:h-[477px] group transition-transform duration-300 hover:-translate-y-2">
      <div className="border-2 mb-4 rounded-xl col-span-3">
        <Image
          src={img || ""}
          alt={name}
          width={333}
          height={300}
          className="w-full h-full object-cover rounded-xl"
        />
      </div>
      <div className="text-sm font-medium col-span-3 text-left text-muted-foreground">
        {title}
      </div>
      <div className="font-bold text-sm col-span-3 text-left text-foreground">
        {name}
      </div>
    </div>
  );
}
