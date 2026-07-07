'use client';

import { createContext, useContext, useState, ReactNode } from 'react';

const SizeContext = createContext<any>(null);

export const useSizeContext = () => {
  const context = useContext(SizeContext);
  if (!context) {
    return { selectedSize: null, setSelectedSize: () => {} };
  }
  return context;
};

export const SizeSelector = ({ sizes }: { sizes: string[] }) => {
  const { selectedSize, setSelectedSize } = useSizeContext();

  return (
    <div className="mt-1 flex flex-wrap gap-2 sm:pr-20">
      {sizes.map((size) => (
        <button
          key={size}
          className={`w-16 h-8 text-black font-semibold rounded-lg border-2 ${
            selectedSize === size
              ? 'bg-black text-white border-black'
              : 'bg-white text-black border-gray-400'
          } mt-0.5 transition-colors duration-300`} 
          onClick={() => setSelectedSize(size)} 
        >
          {size}
        </button>
      ))}
    </div>
  );
};

export const SizeProvider = ({ children }: { children: ReactNode }) => {
  const [selectedSize, setSelectedSize] = useState<string | null>(null);

  return (
    <SizeContext.Provider value={{ selectedSize, setSelectedSize }}>
      {children}
    </SizeContext.Provider>
  );
};


