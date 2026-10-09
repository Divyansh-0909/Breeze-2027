// Rolling-digit readout for the live clock and countdowns. Each digit is
// a 0–9 column translated on transform only (cheap); punctuation renders
// static. The columns inherit the surrounding font/size and sit on the
// text baseline (NOT vertical-align:top, which floats them above the line).
// tabular-nums keeps static and rolling runs the same width. rAF-driven,
// so it pauses for free when the tab is hidden; static text under
// prefers-reduced-motion.
"use client";
import React from "react";
import { motion, useReducedMotion } from "motion/react";

export default function RollDigits({
  value,
  className,
  style,
  label,
}: {
  value: string;
  className?: string;
  style?: React.CSSProperties;
  label?: string;
}): React.ReactElement {
  const reduce = useReducedMotion();
  if (reduce) {
    return (
      <span className={className} style={style} aria-label={label ?? value}>
        {value}
      </span>
    );
  }
  return (
    <span
      className={className}
      style={{
        ...style,
        display: "inline-block",
        whiteSpace: "nowrap",
        fontVariantNumeric: "tabular-nums",
        lineHeight: "inherit",
      }}
      role="timer"
      aria-label={label ?? value}
    >
      {value.split("").map((ch, i) =>
        /[0-9]/.test(ch) ? (
          <span
            key={i}
            aria-hidden
            style={{
              display: "inline-block",
              overflow: "hidden",
              height: "1em",
              width: "0.62em",
              // inline-blocks with overflow clip to the bottom margin edge,
              // which IS the text baseline — digits sit exactly on the line
              verticalAlign: "baseline",
              lineHeight: 1,
            }}
          >
            <motion.span
              aria-hidden
              style={{ display: "block" }}
              animate={{ y: `${-Number(ch)}em` }}
              transition={{ type: "tween", duration: 0.45, ease: [0.3, 0.9, 0.3, 1] }}
            >
              {Array.from({ length: 10 }, (_, d) => (
                <span
                  key={d}
                  style={{ display: "block", height: "1em", lineHeight: 1 }}
                >
                  {d}
                </span>
              ))}
            </motion.span>
          </span>
        ) : (
          <span key={i} aria-hidden>
            {ch}
          </span>
        )
      )}
    </span>
  );
}
