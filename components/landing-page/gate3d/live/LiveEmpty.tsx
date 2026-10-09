// Friendly empty states for the Live view (hand-built Empty: the repo has
// no Empty primitive, and this is three lines). Used when the day hasn't
// started, is over, or has no acts at all.
"use client";
import React from "react";

export default function LiveEmpty({
  kind,
}: {
  kind: "before" | "after" | "empty";
}): React.ReactElement {
  const copy =
    kind === "before"
      ? {
          mark: "○",
          title: "The gully is still waking up.",
          body: "The first act hasn't started yet — the lineup below is in start order.",
        }
      : kind === "after"
        ? {
            mark: "●",
            title: "That's a wrap for today.",
            body: "Every act has played. Thanks for coming down to the gully.",
          }
        : {
            mark: "—",
            title: "No acts on the timeline yet.",
            body: "The schedule is still being set. Check back closer to showtime.",
          };
  return (
    <div className="flex flex-col items-center px-6 py-8 text-center">
      <span
        aria-hidden
        className="mb-2 block h-3 w-3 rounded-full"
        style={{ background: "#ffc24b", boxShadow: "0 0 12px rgba(255,194,75,0.8)" }}
      />
      <p className="text-[18px] font-extrabold text-[#f4efe2]">{copy.title}</p>
      <p className="mt-1 max-w-[280px] text-[14px] text-[rgba(244,239,226,0.7)]">
        {copy.body}
      </p>
      <span className="sr-only">{copy.mark}</span>
    </div>
  );
}
