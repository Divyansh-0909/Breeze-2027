import React from "react";
import Link from "next/link";
import { Card } from "@/components/ui/card";
import { Button } from "../ui/button";
import Image from "next/image";

interface MerchItem {
  product_name: string;
  product_description: string;
  product_price: number;
  id: string;
  image_url: string;
}

const BasicCards = ({ merch }: { merch: MerchItem[] }) => {
  return (
    <>
      {merch?.map((item, id) => (
        <Link
          key={id}
          className="group"
          href={`/merch/${item.id}`}
          target="_blank"
          rel="noopener noreferrer"
        >
          <div className="flex flex-col items-start">
            <div className="relative h-96 w-full rounded-lg overflow-hidden bg-yellow-500">
              <Image
                src={`${process.env.NEXT_PUBLIC_SUPABASE_URL}/storage/v1/object/public/${item.image_url}`}
                alt={`${item.product_name} poster`}
                fill
                className="object-cover transition-transform duration-300 hover:scale-105"
                sizes="(max-width: 768px) 60vw, 30vw"
                priority/>

            </div>
            <div className="w-full flex justify-between">
              <div className="">
                <p className="text-left text-xl px-2 py-1 font-semibold group-hover:underline">
                  {item.product_name}
                </p>
                <p className="text-left text-md px-2 font-normal text-sm">
                  {item.product_description}
                </p>
              </div>
              <p className="text-right self-center px-2 py-1 font-normal text-base">
                Rs. {item.product_price}
              </p>
            </div>
          </div>
        </Link>
      ))}
    </>
  );
};

export default BasicCards;
