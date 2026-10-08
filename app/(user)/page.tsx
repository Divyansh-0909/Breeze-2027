import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = { title: "Gullyverse ? Breeze 2027" };

// The public layout owns the persistent immersive shell.
export default function Home() {
  return <noscript>Gullyverse requires JavaScript. <a href="/after-movie.mp4">Watch the Aftermovie</a> or <Link href="/events">browse festival information</Link>.</noscript>;
}
