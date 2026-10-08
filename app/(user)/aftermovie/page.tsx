import type { Metadata } from "next";

export const metadata: Metadata = { title: "Aftermovie ? Breeze 2027" };

// Direct entry is resolved by the shell without replaying the entrance.
export default function AftermoviePage() {
  return <noscript><a href="/after-movie.mp4">Watch the Breeze Aftermovie</a></noscript>;
}
