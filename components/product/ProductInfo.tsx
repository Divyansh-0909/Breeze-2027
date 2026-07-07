'use client';

import { SizeProvider, SizeSelector } from './SizeSelector';
import {AddToCartMerch} from './AddToCart';

const ProductInfo = ({
  id,
  name,
  price,
  sizes,
}: {
  id: string;
  name: string;
  price: number;
  sizes: string[];
}) => {
  return (
    <div className="w-full sm:w-1/2 p-6 mx-auto space-y-8 sm:mt-5">
      <div className="flex items-center space-x-3 sm:mt-10">
        <div className="w-10 h-10 bg-gray-300 rounded-full shadow-md"></div>
        <h2 className="text-gray-700 font-medium text-lg tracking-wide">BREEZE 2026</h2>
      </div>

      <h1 className="text-black text-2xl sm:text-4xl font-bold leading-tight">{name}</h1>
      <h2 className="text-black mt-3 text-3xl sm:text-5xl font-bold">Rs. {price}</h2>

      <div className="space-y-2">
        <div className="flex items-center space-x-2">
          <p className="text-black font-medium">Colour</p>
          <div className="flex items-center space-x-1">
            <p className="text-black">●</p>
            <p className="text-gray-500">Black</p>
          </div>
        </div>
        <div className="flex space-x-2">
          <div className="w-8 h-8 bg-yellow-400 rounded-md"></div>
          <div className="w-8 h-8 bg-yellow-400 rounded-md"></div>
          <div className="w-8 h-8 bg-yellow-400 rounded-md"></div>
          <div className="w-8 h-8 bg-yellow-400 rounded-md"></div>
        </div>
      </div>

      <div className="space-y-2">
        <div className="flex items-center space-x-2">
          <p className="text-black font-medium">Size</p>
          <div className="flex items-center space-x-1">
            <p className="text-black">●</p>
            <p className="text-gray-500">EU Men</p>
          </div>
        </div>

        <SizeProvider>
          <SizeSelector sizes={sizes} />
          <p className="mt-4 text-gray-600 underline text-sm cursor-pointer">
            Size Guide
          </p>
          <AddToCartMerch merch_id={id}/>
        </SizeProvider>
      </div>
    </div>
  );
};

export default ProductInfo;
