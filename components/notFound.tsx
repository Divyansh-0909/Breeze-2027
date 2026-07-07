"use client";
import Image from "next/image";
import Link from "next/link";

const NotFound: React.FC = () => {
  return (
    <div className="relative flex items-center justify-center min-h-screen w-full overflow-hidden bg-black">
      <title>404 - Page Not Found</title>

      {/* Giant 404 Text Background */}
      <div className="absolute inset-0 flex items-center justify-center pointer-events-none select-none overflow-hidden">
        <span
          className="font-black tracking-tighter text-center"
          style={{
            fontSize: "50vw",
            lineHeight: 0.8,
            color: "#B5BB00",
            margin: "auto",
          }}
        >
          404
        </span>
      </div>

      {/* Full Page Image */}
      <div className="absolute inset-0 z-[2]">
        <Image
          src="/404-image.png"
          alt="404 Illustration"
          fill
          className="object-contain object-center"
          priority
          quality={100}
          unoptimized
        />
      </div>

      {/* Gradient Overlay from Bottom */}
      <div
        className="absolute inset-0 pointer-events-none z-[1]"
        style={{
          background:
            "linear-gradient(to top, #B5BB00 0%, rgba(181, 187, 0, 0.6) 25%, rgba(181, 187, 0, 0.3) 50%, rgba(181, 187, 0, 0) 70%)",
        }}
      />

      {/* Return Home Button */}
      <div className="absolute bottom-24 left-1/2 -translate-x-1/2 z-[3]">
        <Link
          href="/"
          className="inline-block text-[#B5BB00] bg-black border-2 border-[#B5BB00]
            px-10 py-4 rounded-xl text-lg font-semibold
            hover:bg-[#B5BB00] hover:text-black hover:scale-105 transition-all duration-300
            shadow-lg hover:shadow-xl"
        >
          Return to Home
        </Link>
      </div>
    </div>
  );
};

export default NotFound;
