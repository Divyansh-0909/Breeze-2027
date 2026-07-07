import React from "react";
import { Card, CardFooter } from "@/components/ui/card";

const PhotoCard = () => {
  return (
    <div className="col-span-1 md:col-span-2 flex flex-col items-start">
      {/* Image */}
      <div className="relative h-96 w-full">
        <div className="absolute inset-0 bg-[url('/images/Merch-item.png')] bg-cover bg-center bg-no-repeat rounded-lg"></div>
        <Card className="absolute inset-0 bg-transparent ">
          <CardFooter className="absolute bottom-0 w-full text-center p-0">
            <div className="backdrop-blur-sm bg-black bg-opacity-10 py-5 px-10">
              <p className="text-white opacity-90 font-normal">
                Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do
                eiusmod tempor incididunt ut labore.
              </p>
            </div>
          </CardFooter>
        </Card>
      </div>
    </div>
  );
};

export default PhotoCard;
