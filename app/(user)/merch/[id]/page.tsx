import { redirect } from "next/navigation";
import ProductImage from "@/components/product/ProductImage";
import ProductInfo from "@/components/product/ProductInfo";
import Description from "@/components/product/Description";
import { prisma } from "@/lib/prisma";

export default async function Page({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  // Temporarily redirect users away from merch pages
  redirect("/");

  /* Original merch/[id] page content - temporarily disabled
  const prod = await prisma.merchItem.findUnique({
    where: { id: (await params).id },
  });
  // Sizes for the product, assumed it is same for all since there is no sizes in db schema
  const sizes = ["XS", "S", "M", "L", "XL"];
  const tempImgArr = ['/images/product-placeholder.png', '/images/circa-72-placeholder.png', '/images/Merch-item.png', '/images/Merch-hero.png', '/image5.jpg','/image6.jpg'];
  
  return (
    <div className="flex flex-col min-h-screen">
      <title>Breeze Merch - {prod.product_name}</title>
      <div className="flex-1 overflow-y-auto py-8 sm:gap-4 sm:px-4 sm:py-8 flex flex-col sm:flex-row justify-between mt-10">
        <ProductImage imageUrls={tempImgArr} />
        <ProductInfo
          id={prod.id}
          name={prod.product_name}
          price={prod.product_price}
          sizes={sizes} // Passing sizes prop to ProductInfo
        />
      </div>
      <Description description={prod.product_description} />
    </div>
  );
  */
}
