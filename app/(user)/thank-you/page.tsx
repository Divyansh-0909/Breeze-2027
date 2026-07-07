import { Metadata } from "next";
import Link from "next/link";
import Image from "next/image";

export const metadata: Metadata = {
  title: "Thank You - Breeze '26",
};

export default function Page() {
  return (
    <div className="flex flex-col items-center justify-center bg-[#FABF12] gap-[6vw] sm:gap-[4vw] pt-[27vw] sm:pt-[18vw] h-screen pb-[10vh]">
      <div className="relative">
        <Image
          src="/images/thank-you.png"
          alt="Thank you"
          width={300}
          height={300}
          className="relative z-10 w-[25vw] sm:w-[15vw]"
        />
        <Image
          src="/images/thank-back.png"
          alt="Background"
          width={350}
          height={350}
          className="absolute top-0 left-0 z-0"
          style={{ transform: "scale(1.4)", width: "25vw" }}
        />
      </div>
      <div className="text-center">
        <div className=" text-[3.5vw] sm:text-[2vw] italic font-serif">
          Thank you for your payment!
        </div>
        <div className=" text-[2vw] sm:text-[1vw]">
          We will send you an email confirmation as soon as we have verified the
          payment
        </div>
      </div>

      <Link href="/">
        <button className="text-white text-[2.1vw] rounded-[5vw] p-[2.5vw] sm:text-[1.1vw] sm:rounded-[4vw] sm:p-[1.5vw] bg-black">
          {" "}
          &#x2190; Back to Home
        </button>
      </Link>
    </div>
  );
}
