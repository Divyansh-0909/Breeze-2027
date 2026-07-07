"use client";

import { useEffect, useRef, useState } from "react";

type SoundButtonProps = {
  isPlaying: boolean;
  onToggle: () => void;
};

export default function SoundButton({ isPlaying, onToggle }: SoundButtonProps) {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const audioRef = useRef<HTMLAudioElement | null>(null);

  const [hasMounted, setHasMounted] = useState(false);
  const [currentTrackIndex, setCurrentTrackIndex] = useState(0);

  // ✅ LOCAL MP3 PLAYLIST (public/music)
  const playlist = ["/music/FireFire.mp3", "/music/2.mp3"];

  // Wave animation physics
  const amplitude = useRef(0);
  const targetAmplitude = useRef(0);
  const velocity = useRef(0);
  const phase = useRef(0);

  useEffect(() => {
    setHasMounted(true);
  }, []);

  // 🔊 AUDIO CONTROL (SAFE FOR ALL BROWSERS)
  useEffect(() => {
    if (!audioRef.current) return;

    if (isPlaying) {
      audioRef.current.play().catch(() => {}); // ignore autoplay warning
    } else {
      audioRef.current.pause();
    }
  }, [isPlaying, currentTrackIndex]);

  const handleEnded = () => {
    setCurrentTrackIndex((prev) => (prev + 1) % playlist.length);
  };

  // 🌊 Canvas waveform animation
  useEffect(() => {
    if (!hasMounted) return;
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const size = canvas.width;
    const center = size / 2;
    const radius = size / 2 - 6;
    let rafId: number;

    const draw = () => {
      ctx.clearRect(0, 0, size, size);

      targetAmplitude.current = isPlaying ? 10 : 0;

      const stiffness = 0.03;
      const damping = 0.85;
      const force = (targetAmplitude.current - amplitude.current) * stiffness;

      velocity.current = velocity.current * damping + force;
      amplitude.current += velocity.current;

      ctx.save();
      ctx.translate(center, center);
      ctx.beginPath();
      ctx.strokeStyle = "#FFD700";
      ctx.lineWidth = 4;
      ctx.lineCap = "round";

      const steps = 72;
      const visibleWidth = radius * 2 * 0.6;
      const startX = -visibleWidth / 2;

      for (let i = 0; i <= steps; i++) {
        const x = startX + (i / steps) * visibleWidth;
        const angle = (i / steps) * Math.PI * 2;
        const y = Math.sin(angle + phase.current) * amplitude.current;

        if (i === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
      }

      ctx.stroke();
      ctx.restore();

      phase.current += isPlaying ? 0.04 : 0.01;

      rafId = requestAnimationFrame(draw);
    };

    draw();
    return () => cancelAnimationFrame(rafId);
  }, [isPlaying, hasMounted]);

  if (!hasMounted) return null;

  return (
    <div className="relative">
      {/* 🔊 Audio Element */}
      <audio
        ref={audioRef}
        src={playlist[currentTrackIndex]}
        preload="auto"
        onEnded={handleEnded}
      />

      {/* UI Button */}
      <button
        onClick={onToggle}
        className="w-12 h-12 rounded-full flex items-center justify-center
                   bg-purple-900/80 hover:bg-purple-800
                   transition-all duration-300"
      >
        <canvas
          ref={canvasRef}
          width={80}
          height={80}
          className="w-full h-full"
        />
      </button>
    </div>
  );
}
