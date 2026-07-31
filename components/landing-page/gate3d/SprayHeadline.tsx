"use client";
import React, { useMemo } from "react";

/**
 * A spray-painted headline styled exactly like the `GULLYVERSE` wall lettering
 * on the tunnel entrance: Aerosoldier font, drip/spray texture, subtle rotation
 * for hand-painted imperfection.
 *
 * All decoration is CSS — no canvas, no image. The drips are pseudo-elements
 * with carefully placed thin bars that mimic paint runs, and the overspray is a
 * blurred text-shadow halo.
 */

const DISPLAY = "'Aerosoldier', 'Impact', 'Arial Black', system-ui, sans-serif";
const CREAM = "#f4efe2";

/** Deterministic seeded PRNG (matches textures.ts) */
function rng(seed: number): () => number {
  let a = seed >>> 0;
  return () => {
    a = (a + 0x6d2b79f5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

interface Drip {
  left: string;
  height: string;
  width: string;
  opacity: number;
  delay: string;
}

export default function SprayHeadline({
  text,
  subtitle,
  className = "",
}: {
  text: string;
  subtitle?: string;
  className?: string;
}): React.ReactElement {
  // Procedural drips — deterministic so they look the same on every load
  const drips: Drip[] = useMemo(() => {
    const r = rng(8823);
    return Array.from({ length: 12 }, () => ({
      left: `${8 + r() * 84}%`,
      height: `${14 + r() * 32}px`,
      width: `${1.5 + r() * 2.5}px`,
      opacity: 0.35 + r() * 0.45,
      delay: `${r() * 2}s`,
    }));
  }, []);

  return (
    <div
      className={`relative inline-block ${className}`}
      style={{ transform: "rotate(-1.4deg)" }}
    >
      {/* Overspray halo */}
      <h2
        aria-hidden="true"
        style={{
          fontFamily: DISPLAY,
          color: "transparent",
          textShadow: `0 0 40px rgba(244,239,226,0.18), 0 0 80px rgba(244,239,226,0.08)`,
          fontSize: "inherit",
          lineHeight: "inherit",
          position: "absolute",
          inset: 0,
          pointerEvents: "none",
        }}
      >
        {text}
      </h2>

      {/* Main lettering */}
      <h2
        style={{
          fontFamily: DISPLAY,
          color: CREAM,
          textShadow: `
            3px 4px 0px rgba(6,6,9,0.9),
            0 0 18px rgba(244,239,226,0.12),
            0 8px 30px rgba(0,0,0,0.7)
          `,
          lineHeight: 1,
          letterSpacing: "0.04em",
          position: "relative",
        }}
      >
        {text}
      </h2>

      {/* Drip lines — paint runs below the letterforms */}
      <div
        aria-hidden="true"
        style={{
          position: "absolute",
          left: 0,
          right: 0,
          bottom: "-4px",
          height: "48px",
          pointerEvents: "none",
          overflow: "visible",
        }}
      >
        {drips.map((d, i) => (
          <span
            key={i}
            style={{
              position: "absolute",
              left: d.left,
              top: 0,
              width: d.width,
              height: d.height,
              background: `linear-gradient(to bottom, ${CREAM}, transparent)`,
              opacity: d.opacity,
              borderRadius: "0 0 1px 1px",
            }}
          />
        ))}
      </div>

      {/* Subtitle (e.g. Hindi transliteration) */}
      {subtitle && (
        <p
          style={{
            fontFamily: "'Satoshi', system-ui, sans-serif",
            color: "rgba(255,194,75,0.55)",
            fontSize: "0.28em",
            letterSpacing: "0.35em",
            textTransform: "uppercase",
            fontWeight: 700,
            marginTop: "0.35em",
          }}
        >
          {subtitle}
        </p>
      )}
    </div>
  );
}
