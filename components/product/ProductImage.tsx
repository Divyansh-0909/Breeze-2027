"use client";
import { useState } from 'react';
import Image from 'next/image';

const ProductImage = ({ imageUrls }: { imageUrls: string[] }) => {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [showHiddenThumbnails, setShowHiddenThumbnails] = useState(false);

  const handleNext = () => {
    setCurrentIndex((prevIndex) => (prevIndex + 1) % imageUrls.length);
  };

  const handlePrevious = () => {
    setCurrentIndex((prevIndex) =>
      (prevIndex - 1 + imageUrls.length) % imageUrls.length
    );
  };

  const visibleThumbnails = showHiddenThumbnails
    ? imageUrls.slice(4) 
    : imageUrls.slice(0, 4); 

  const hiddenThumbnailsCount = imageUrls.length - 4;

  return (
    <div className="w-full sm:w-1/2 p-6 sm:mt-8 mx-auto">
      <div className="relative flex justify-center items-center mb-6">
        <button
          className="absolute left-2 sm:left-6 z-10 bg-gray-300 hover:bg-gray-400 text-black rounded-full p-2"
          onClick={handlePrevious}
        >
          &#8249;
        </button>
        <div className="relative sm:w-[500px] sm:h-[500px] w-[320px] h-[320px]">
          <Image
            src={imageUrls[currentIndex]}
            alt={`Product Image ${currentIndex + 1}`}
            layout="fill"
            objectFit="cover"
            className="rounded-xl shadow-lg"
          />
        </div>
        <button
          className="absolute right-2 sm:right-6 z-10 bg-gray-300 hover:bg-gray-400 text-black rounded-full p-2"
          onClick={handleNext}
        >
          &#8250;
        </button>
      </div>

      <div className="relative flex justify-center mt-4">
        <div
          className={`flex space-x-3 overflow-x-auto ${
            visibleThumbnails.length < 4 ? 'justify-center' : ''
          }`}
          style={{ maxWidth: '500px', width: '100%' }}
        >
          {visibleThumbnails.map((imageUrl, index) => (
            <div
              key={index}
              className={`relative w-16 h-16 sm:w-24 sm:h-24 ${
                imageUrls.indexOf(imageUrl) === currentIndex
                  ? 'border-2 border-black'
                  : ''
              } rounded-xl shadow-lg cursor-pointer`}
              onClick={() => setCurrentIndex(imageUrls.indexOf(imageUrl))}
            >
              <Image
                src={imageUrl}
                alt={`Thumbnail ${imageUrls.indexOf(imageUrl) + 1}`}
                layout="fill"
                objectFit="cover"
                className="rounded-xl"
              />
            </div>
          ))}

          {imageUrls.length > 4 && (
            <div
              className="w-16 h-16 sm:w-24 sm:h-24 border border-black rounded-xl flex justify-center items-center cursor-pointer"
              onClick={() => setShowHiddenThumbnails((prev) => !prev)}
            >
              <p className="text-black">
                {showHiddenThumbnails
                  ? 'Back'
                  : `+${hiddenThumbnailsCount} More`}
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ProductImage;