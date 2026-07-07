import BasicCards from "@/components/events/BasicCards";
import { prisma } from "@/lib/prisma";

export const dynamic = "force-dynamic";
import Image from "next/image";
import localFont from "next/font/local";
import { Fraunces } from "next/font/google";
import Link from "next/link";
import { Button } from "@/components/ui/button";

const satoshi = localFont({
  src: "../../../public/fonts/Satoshi-Regular.woff",
  weight: "800",
  style: "normal",
});
const satoshi_bold = localFont({
  src: "../../../public/fonts/Satoshi-Bold.woff",
  weight: "800",
  style: "normal",
});

const maswen = localFont({
  src: "../../../public/fonts/Maswen-Outline.otf",
  weight: "400",
  style: "normal",
});

const fraunces = Fraunces({
  subsets: ["latin"],
  display: "swap",
  weight: ["400"],
  style: ["normal", "italic"],
});

const page = async ({
  searchParams,
}: {
  searchParams: Promise<{ page?: string }>;
}) => {
  const params = await searchParams;
  const cultural = await prisma.eventItem.findMany({
    select: {
      event_name: true,
      event_description: true,
      event_price: true,
      event_venue: true,
      event_org: true,
      event_date: true,
      image_url: true,
      id: true,
      registration_open: true,
    },
    where: {
      event_type: {
        equals: "Cultural",
      },
    },
    take: 5,
  });
  const technical = await prisma.eventItem.findMany({
    select: {
      event_name: true,
      event_description: true,
      event_price: true,
      event_venue: true,
      event_org: true,
      event_date: true,
      image_url: true,
      id: true,
      registration_open: true,
    },
    where: {
      event_type: {
        equals: "Technical",
      },
    },
    take: 5,
  });
  return (
    <div className="relative">
      <title>Events - Breeze '26</title>

      <div className="relative w-full h-[25vh] md:h-[60vh] lg:h-[70vh]">
        <Image
          src="/events-header.png"
          alt="Events Header"
          fill
          className="object-cover object-top"
          priority
        />
        {/* Black tint overlay */}
        <div className="absolute inset-0 bg-black/40" />
        {/* Text on bottom right */}
        <div className="absolute bottom-6 right-6 md:bottom-10 md:right-10 text-right">
          <p
            className={`font-urban-vogue text-white text-2xl md:text-4xl lg:text-5xl text-left mb-2 md:mb-4`}
          >
            20th-22nd February
          </p>
          <p
            className={`font-different-beginning italic text-white text-7xl md:text-9xl lg:text-[12rem] -mt-2 md:-mt-4 text-bottom`}
          >
            events
          </p>
        </div>
      </div>

      {/* Moving Text Banner */}
      <div className="relative w-full overflow-hidden pt-12 pb-6 bg-transparent">
        <div className="animate-events-marquee whitespace-nowrap flex">
          {[...Array(10)].map((_, i) => (
            <span
              key={i}
              className={`${maswen.className} text-[#FF903A] text-6xl md:text-8xl lg:text-9xl mx-8`}
            >
              BREEZE 2026
            </span>
          ))}
        </div>
      </div>

      <div className="flex flex-col gap-2 sm:gap-1 m-10 mb-0 px-2 sm:px-6">
        <h1 className="text-xl sm:text-2xl font-urban-vogue text-[#F6FC50]">
          संस्कारी AF
        </h1>
        <div className="flex justify-between items-center flex-wrap sm:flex-nowrap sm:gap-5 gap-3 ">
          <p
            className={`text-4xl sm:text-5xl font-thin ${satoshi_bold.className} font-bold`}
          >
            Cultural Events
          </p>
          <div className="flex justify-center items-center">
            <Link href="/events/cultural">
              <Button
                variant="link"
                className="text-lg sm:text-xl underline pl-0 sm:pl-4"
              >
                See All
              </Button>
            </Link>
            <Link href="/events/cultural">
              <Image
                src="/Icons/arrow-2.svg"
                alt="Icon"
                width={32}
                height={32}
                className="shrink-0 min-h-6 min-w-6"
              />
            </Link>
          </div>
        </div>
      </div>
      <div className="mt-4 px-12">
        <BasicCards event={cultural} />
      </div>
      <div className="flex flex-col gap-2 sm:gap-1 m-10 mb-0 px-2 sm:px-6">
        <h1 className="text-xl sm:text-2xl font-urban-vogue text-[#F6FC50]">
          Challenge Your Mind !
        </h1>
        <div className="flex justify-between items-center flex-wrap sm:flex-nowrap sm:gap-5 gap-3 ">
          <p
            className={`text-4xl sm:text-5xl font-thin ${satoshi_bold.className} font-bold`}
          >
            Technical Events
          </p>
          <div className="flex justify-center items-center">
            <Link href="/events/technical">
              <Button
                variant="link"
                className="text-lg sm:text-xl underline pl-0 sm:pl-4"
              >
                See All
              </Button>
            </Link>
            <Link href="/events/technical">
              <Image
                src="/Icons/arrow-2.svg"
                alt="Icon"
                width={37}
                height={37}
                className="shrink-0 min-h-10 min-w-10"
              />
            </Link>
          </div>
        </div>
      </div>
      <div className="mt-4 mb-40 px-12">
        <BasicCards event={technical} />
      </div>
    </div>
  );
};

export default page;
