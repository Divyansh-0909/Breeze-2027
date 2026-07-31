"use client";
import React, { useEffect, useState } from "react";
import dynamic from "next/dynamic";

/**
 * /past-performers — the WALL OF ECHOES section.
 *
 * Opens with a brief fade-from-black so the transition from the WebGL tunnel
 * to this CSS page doesn't have a hard cut. The gallery component is lazy-
 * loaded (client only) because it references the DOM directly for scroll-
 * linked animation.
 */

const PastPerformersGallery = dynamic(
  () => import("../../../components/landing-page/gate3d/PastPerformersGallery"),
  {
    ssr: false,
    loading: () => (
      <div
        style={{
          position: "fixed",
          inset: 0,
          background: "#070a14",
          zIndex: 100,
        }}
      />
    ),
  }
);

export default function PastPerformersPage(): React.ReactElement {
  // Fade-from-black transition to hide the WebGL → CSS route seam
  const [entered, setEntered] = useState(false);

  useEffect(() => {
    // Brief delay so the black screen is established before fading in
    const t = window.setTimeout(() => setEntered(true), 80);
    return () => window.clearTimeout(t);
  }, []);

  return (
    <>
      {/* Content */}
      <main
        style={{
          opacity: entered ? 1 : 0,
          transition: "opacity 0.6s ease-in",
          minHeight: "100vh",
          minWidth: "100vw",
          background: "#070a14",
        }}
      >
        <PastPerformersGallery />
      </main>

      {/* Initial black overlay — fades out as content fades in */}
      <div
        aria-hidden="true"
        style={{
          position: "fixed",
          inset: 0,
          background: "#070a14",
          zIndex: 50,
          pointerEvents: "none",
          opacity: entered ? 0 : 1,
          transition: "opacity 0.7s ease-out",
        }}
      />
    </>
  );
}
