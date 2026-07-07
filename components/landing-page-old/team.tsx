import Link from "next/link";
import React from 'react';
import localFont from 'next/font/local';
import { Fraunces } from 'next/font/google';
import { Inter } from "next/font/google";
import { Button } from "../ui/button";

const inter = Inter({ subsets: ["latin"], weight: ['300'], style: ['normal','italic'] });

const satoshi = localFont({
  src: '../../public/fonts/Satoshi-Regular.woff',
  weight: '800',
  style: 'normal',
});

const fraunces = Fraunces({ 
  subsets: ["latin"],
  display: 'swap',
  weight: ['600'], 
  style: ['normal', 'italic'] 
});

interface TeamMember {
    name: string;
    position: string;
    tag1: string;
    tag2: string;
    imageUrl: string;
  }
  const TeamCard: React.FC<TeamMember> = ({ name, position, tag1, tag2, imageUrl }) => (
    <div className="relative xl:w-[250px] xl:h-[320px] w-[200px] h-[260px] rounded-2xl overflow-hidden group antialiased transform-gpu border border-white/5">
      <div 
        className="absolute inset-0 bg-cover bg-center"
        style={{ 
          backgroundImage: `url(${imageUrl})`,
        }}
      />
      <div className="absolute inset-0 " />
      
      <div className="absolute bottom-0 left-0 p-4 w-full">
        <h2 className="text-white text-xs xl:text-sm font-medium">
          {name}
        </h2>
        
        <h3 className="text-white/90 text-sm italic xl:text-base font-medium mt-1 mb-2">
          {position}
        </h3>
        <div className="flex gap-1.5">
          <span className="px-2 py-0.5 border border-white/20 border-1 rounded-full text-[8px] xl:text-xs text-white backdrop-blur-sm">
            {tag1}
          </span>
          <span className="px-2 py-0.5 border border-white/20 border-1 rounded-full text-[8px] xl:text-xs text-white backdrop-blur-sm">
            {tag2}
          </span>
        </div>
      </div>
    </div>
  );

export default function Team() {
    const teamMembers: TeamMember[] = [
        {
            name: "Arsh Bhasin",
            position: "Design Lead",
            tag1: "Graphic Design",
            tag2: "Illustration",
            imageUrl: "https://media.breezesnu.com/arsh.svg"
        },
        {
            name: "Daksh Chopra",
            position: "Marketing Lead",
            tag1: "Social Media",
            tag2: "Poster lagado koi",
            imageUrl: "https://media.breezesnu.com/daksh.svg"
        },
        {
            name: "Priyanshi Sachan",
            position: "Videography Lead",
            tag1: "The cameraman",
            tag2: "Creativity",
            imageUrl: "https://media.breezesnu.com/video.svg"
        },
        {
            name: "Nimansh Endlay",
            position: "Tech Lead",
            tag1: "Code karta hai",
            tag2: "Python",
            imageUrl: "https://media.breezesnu.com/nimansh.png"
        },
        {
            name: "Amey Gautam",
            position: "Public Relations Lead",
            tag1: "Match dekha aaj?",
            tag2: "Cutie",
            imageUrl: "https://media.breezesnu.com/amey.svg"
        }
    ];
    return(
        <div className="flex flex-col justify-center items-center py-10 bg-[#2A7F84]">
            <div className={`${satoshi.className} italic text-white xl:text-5xl sm:text-3xl lg:text-4xl text-2xl `}>
            Meet the Maestros: The 
            </div>
            <div className={`${fraunces.className} italic text-white xl:text-5xl pt-2 sm:text-3xl  lg:text-4xl text-2xl `}>
            Breeze Team's Secret Sauce!
            </div>
            <div className={`${inter.className} italic text-white xl:w-[50%] text-center pt-6 pb-6 sm:text-base sm:w-[80%] lg:w-[60%] text-sm w-[90%]`}>
            Venture into the inner sanctum of Breeze, the magnetic college fest of Shiv Nadar University, where innovation thrives and inspiration reigns. Get to know the alchemists who blend passion, dedication, and artistry to bring this spectacular event to life!
            </div>
            <Button variant="ghost" className="sm:text-base inline-block py-2 px-5 rounded-[50px] text-sm ">
                <Link href="/team">
                    Meet the Team &#x27F6;
                </Link>
            </Button>
            <div className="flex gap-[30px] pt-12 flex-wrap justify-center">
            
            {teamMembers.map((member, index) => (
                    <TeamCard key={index} {...member} />
                ))}
            </div>
         
        </div>
    )
}
