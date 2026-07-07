"use client";
import React, { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence, PanInfo } from "motion/react";
import { X } from "lucide-react";
import { teamMembers, TeamMember } from "@/components/details"; // Ensure this matches your file path

// --- CONFIGURATION ---
const CARD_WIDTH_SIDE = 260;
const CARD_WIDTH_CENTER = 300;   
const SPACING = 360;             
const EXPANDED_WIDTH = "60vw";   
const EXPANDED_HEIGHT = "70vh";  
const EXPANDED_PUSH = 900;       

interface CardProps {
  member: TeamMember;
  offset: number;
  isActive: boolean;
  isExpanded: boolean;
  onClick: () => void;
  onClose: (e: React.MouseEvent) => void;
}

const Card: React.FC<CardProps> = ({ member, offset, isActive, isExpanded, onClick, onClose }) => {
  
  // 1. Horizontal Position
  let xPos = offset * SPACING;
  if (isExpanded) {
    if (isActive) xPos = 0; 
    else if (offset > 0) xPos += EXPANDED_PUSH; 
    else if (offset < 0) xPos -= EXPANDED_PUSH;
  }

  // 2. Vertical Position
  const yPos = isExpanded && isActive ? 0 : Math.abs(offset) * -30;

  // 3. Dimensions
  const width = isActive 
    ? (isExpanded ? EXPANDED_WIDTH : CARD_WIDTH_CENTER) 
    : CARD_WIDTH_SIDE;
    
  const height = isActive 
    ? (isExpanded ? EXPANDED_HEIGHT : 400)
    : 340;

  return (
    <motion.div
      onClick={onClick}
      className="absolute"
      initial={false}
      animate={{
        x: xPos,
        y: yPos,
        width,
        height,
        zIndex: isActive ? 100 : 10 - Math.abs(offset),
        opacity: Math.abs(offset) > 3 ? 0 : 1,
        scale: 1, 
      }}
      transition={{
        type: "spring",
        stiffness: 280,
        damping: 30,
      }}
      transformTemplate={({ x, y, scale }) => {
        const rotateValue = isActive && isExpanded ? 0 : offset * -5;
        return `translate(-50%, -50%) translate3d(${x}, ${y}, 0) scale(${scale}) rotateY(${rotateValue}deg)`;
      }}
      style={{
        left: "50%",
        top: "50%", 
        transformStyle: "preserve-3d",
      }}      
    >
      {/* PURPLE THEME */}
      <motion.div
        className={`relative h-full w-full rounded-2xl overflow-hidden border bg-[#0A0A0A] transition-all duration-500 cursor-pointer ${
          isActive
            ? "border-purple-500 shadow-[0_0_50px_rgba(168,85,247,0.4)]"
            : "border-white/10 shadow-lg group hover:border-purple-500/50"
        }`}
      >
        {/* --- IMAGE --- */}
        <div className="absolute inset-0 z-0">
          <motion.img
            src={member.image}
            alt={member.name}
            className="h-full w-full object-cover"
            animate={{
              filter: isActive ? "grayscale(0%)" : "grayscale(100%) opacity(0.5)",
              scale: isExpanded && isActive ? 1.05 : 1
            }}
            transition={{ duration: 0.4 }}
          />
          <div className="absolute inset-0 bg-gradient-to-t from-[#0A0A0A] via-[#0A0A0A]/40 to-transparent" />
          
          <motion.div 
            className="absolute inset-0 bg-black/70"
            initial={{ opacity: 0 }}
            animate={{ opacity: isExpanded && isActive ? 1 : 0 }} 
          />
        </div>

        {/* --- CONTENT CONTAINER --- */}
        <div className="relative z-10 h-full w-full p-6">
            
            {/* EXPANDED CONTENT */}
            <AnimatePresence>
                {isActive && isExpanded && (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        transition={{ delay: 0.1, duration: 0.3 }}
                        className="h-full flex flex-col"
                    >
                        {/* Close Button */}
                        <div 
                           onClick={onClose}
                           className="absolute top-4 right-4 p-2 bg-black/50 hover:bg-purple-900/30 border border-white/10 hover:border-purple-500/50 rounded-full backdrop-blur-md transition-all cursor-pointer z-50"
                        >
                            <X className="text-white" size={20} />
                        </div>

                        {/* Title Section */}
                        <div className="mt-8 mb-6">
                            <h2 className="text-5xl font-bold text-white mb-2 tracking-tight">{member.name}</h2>
                            <p className="text-2xl text-purple-400 font-medium tracking-wide">{member.role}</p>
                        </div>

                        {/* Scrollable Details */}
                        <div className="flex-1 overflow-y-auto pr-2 scrollbar-thin scrollbar-thumb-slate-700 scrollbar-track-transparent">
                             <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                                <div>
                                    <h4 className="text-sm font-bold text-purple-500/70 uppercase tracking-wider mb-3">About</h4>
                                    <p className="text-slate-300 text-lg leading-relaxed font-light">
                                        {member.bio}
                                    </p>
                                </div>
                                <div className="flex flex-col gap-4">
                                    {/* --- UPDATED SECTION START --- */}
                                    {/* Removed 'stats' and replaced with 'year' */}
                                    <div className="bg-purple-950/20 p-4 rounded-xl border border-purple-500/20 backdrop-blur-sm">
                                        <span className="block text-xs text-purple-400/70 uppercase tracking-wider">Class of</span>
                                        <span className="block text-3xl font-bold text-white mt-1">{member.year}</span>
                                    </div>
                                    {/* --- UPDATED SECTION END --- */}
                                </div>
                             </div>
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
      </motion.div>
    </motion.div>
  );
};

export default function TeamPage() {
  const [activeIndex, setActiveIndex] = useState(2);
  const [isExpanded, setIsExpanded] = useState(false);
  const lastScrollTime = useRef(0);

  const setIndex = (index: number) => {
    setIsExpanded(false);
    setActiveIndex(index);
  };

  const handleNext = () => setIndex((activeIndex + 1) % teamMembers.length);
  const handlePrev = () => setIndex((activeIndex - 1 + teamMembers.length) % teamMembers.length);

  useEffect(() => {
    const handleWheel = (e: WheelEvent) => {
        if (isExpanded) return;
        const now = Date.now();
        if (now - lastScrollTime.current < 300) return;
        if (Math.abs(e.deltaY) > 30) {
            if (e.deltaY > 0) handleNext();
            else handlePrev();
            lastScrollTime.current = now;
        }
    };
    window.addEventListener("wheel", handleWheel, { passive: true });
    return () => window.removeEventListener("wheel", handleWheel);
  }, [activeIndex, isExpanded]);

  // Auto-scroll effect
  useEffect(() => {
    if (isExpanded) return;

    const timer = setTimeout(() => {
      handleNext();
    }, 1800); // 1000ms wait + approx 800ms for comfortable reading/transition

    return () => clearTimeout(timer);
  }, [activeIndex, isExpanded]);

  const handleDragEnd = (event: any, info: PanInfo) => {
    if (isExpanded) return;
    if (info.offset.x < -50) handleNext();
    else if (info.offset.x > 50) handlePrev();
  };

  const onCardClick = (index: number) => {
    if (index === activeIndex) setIsExpanded(true);
    else setIndex(index);
  };

  return (
    <div className="relative w-full h-screen bg-[#050505] flex flex-col justify-center items-center overflow-hidden font-sans">
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_0%,rgba(124,58,237,0.15),transparent_60%)]" />

      {/* Header */}
      <motion.div 
        animate={{ opacity: isExpanded ? 0 : 1, y: isExpanded ? -100 : 0 }}
        className="absolute top-16 text-center z-40 pointer-events-none"
      >
        <h1 className="text-5xl font-bold text-white mb-2 tracking-tight">Meet The Team</h1>
        <p className="text-purple-400/70">Scroll to explore • Click to expand</p>
      </motion.div>

      {/* CAROUSEL TRACK */}
      <motion.div 
        className="relative w-full h-full flex justify-center items-center perspective-1000 cursor-grab active:cursor-grabbing"
        drag={isExpanded ? false : "x"}
        dragConstraints={{ left: 0, right: 0 }}
        dragElastic={0.05}
        onDragEnd={handleDragEnd}
        animate={{ y: isExpanded ? 0 : 60 }} 
        transition={{ type: "spring", stiffness: 200, damping: 25 }}
      >
        <AnimatePresence mode="popLayout">
          {teamMembers.map((member, index) => {
            let offset = index - activeIndex;
            const len = teamMembers.length;
            if (offset > len / 2) offset -= len;
            else if (offset < -len / 2) offset += len;

            if (Math.abs(offset) > 4) return null;

            return (
              <Card
                key={member.id}
                member={member}
                offset={offset}
                isActive={offset === 0}
                isExpanded={isExpanded && offset === 0}
                onClick={() => onCardClick(index)}
                onClose={(e) => {
                    e.stopPropagation();
                    setIsExpanded(false);
                }}
              />
            );
          })}
        </AnimatePresence>
      </motion.div>
    </div>
  );
}