import { Fraunces } from 'next/font/google';
import { PT_Sans } from 'next/font/google';
import localFont from 'next/font/local';


const fraunces = Fraunces({ 
  subsets: ["latin"],
  display: 'swap',
  weight: ['400'], 
  style: ['normal', 'italic'] 
});

const ptSans = PT_Sans({ 
  subsets: ["latin"],
  display: 'swap',
  weight: ['400'], 
  style: ['normal'] 
});

const acid = localFont({
  src: '../../public/fonts/acid-grotesk.woff',
  weight: '800',
  style: 'normal',
});

export default function AfterMovie() {
  return (
    <div className="">
      <div className=" flex flex-col justify-center text-center pt-8">
        <h2 className="text-white pt-3 sm:pt-4 md:pt-5 pb-2 text-2xl sm:text-3xl md:text-4xl lg:text-5xl">
          Check out the
        </h2>
        <h1 className={`${fraunces.className} text-[#FBC013]  text-3xl sm:text-4xl md:text-5xl lg:text-6xl italic`}>Breeze ‘22 Aftermovie</h1>
        <p className={`${ptSans.className} text-white 
            text-sm sm:text-base md:text-lg lg:text-xl
            mt-2 sm:mt-3 md:mt-4
            w-[90%] sm:w-4/5 md:w-[80vw]
            self-center 
            pb-2 sm:pb-3 md:pb-[2vw]`}>
          From the moment the lighting equipments lands on campus, it is an
          exhilarating experience for everyone that is on campus. Each corner is
          brimming with excitement and it is a fest that energizes the mind and
          the spirit. BREEZE is about the invaluable life lessons it teaches us.
          As we immerse ourselves in the joy and energy of BREEZE, we carry with
          us the invaluable experiences and cherished memories that define this
          exceptional event.
        </p>

        <div className="relative mt-8 md:mt-12">
          <div className="px-2 md:px-[10%] [@media(min-aspect-ratio:0.8)]:md:px-[25%]">
            <div className="relative w-full aspect-video">
              <iframe 
                width="100%" 
                height="100%" 
                src="https://www.youtube.com/embed/etUeoHcrbQU?si=c4jeSU8hw7Lqp4f9" 
                title="YouTube video player" 
                frameBorder="0" 
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" 
                referrerPolicy="strict-origin-when-cross-origin"
                allowFullScreen
                className="rounded-xl"
              />
            </div>
            <div className={`${acid.className} text-[#FBC013] flex justify-center flex-wrap my-6 sm:my-8 md:my-10 gap-4 sm:gap-8 md:gap-[4vw]`}>
              <div>
                <h3 className="text-white text-2xl sm:text-3xl md:text-[2vw]">300+</h3>
                <p className="text-white text-base sm:text-xl md:text-[1.5vw]">Events Organised</p>
              </div>
              <div>
                <h3 className="text-white text-2xl sm:text-3xl md:text-[2vw]">10K+</h3>
                <p className="text-white text-base sm:text-xl md:text-[1.5vw]">Yearly Footfall</p>
              </div>
              <div>
                <h3 className="text-white text-2xl sm:text-3xl md:text-[2vw]">50+</h3>
                <p className="text-white text-base sm:text-xl md:text-[1.5vw]">Clubs & Societies</p>
              </div>
            </div>
          </div>

          <img
            src="/images/landing-page/l-elephant.png"
            alt=""
            className="hidden md:block absolute bottom-0 left-0 w-[20%] 
              [@media(min-aspect-ratio:0.8)]:w-[23%]"
          />
          <img
            src="/images/landing-page/r-elephant.png"
            alt=""
            className="hidden md:block absolute bottom-0 right-0 w-[20%] 
              [@media(min-aspect-ratio:0.8)]:w-[23%]"
          />
        </div>
      </div>
    </div>
  );
}