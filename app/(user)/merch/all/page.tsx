import { redirect } from "next/navigation";
import React from "react";
import Heading2 from "@/components/merch-2024/Heading2";
import BasicCards from "@/components/merch-2024/BasicCards";
import BottomButtons from "@/components/merch-2024/BottomButtons";
import { prisma } from "@/lib/prisma";

const Page = async ({ searchParams }) => {
  // Temporarily redirect users away from merch pages
  redirect("/");

  /* Original merch/all page content - temporarily disabled
  const merch = await prisma.merchItem.findMany({select: {product_name: true, product_description: true, product_price: true, id: true, image_url: true}});
  const currentPage = Number(searchParams.page) || 1;
  const totalItems = merch.length;
  const startIndex = (currentPage - 1) * 8;
  const merchForPage = merch.slice(startIndex, startIndex + 8);
  return (
    <div className="pt-20">
      <Heading2 />
      <div className="m-10 mt-0">
        <div className="flex justify-center py-10">
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-7 w-full">
            <BasicCards merch={merchForPage} />
          </div>
        </div>
      </div>
      <BottomButtons
        currentPage={currentPage}
        totalItems={totalItems}
      />
    </div>
  );
  */
};

export default Page;