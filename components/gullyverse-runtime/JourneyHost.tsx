"use client";
import dynamic from "next/dynamic";
const Journey=dynamic(()=>import("./NativeJourney"),{ssr:false});
export default function JourneyHost(){return <Journey assetBase="/models/gullyverse/locked-rev15z-clean-v2/" groundBase="/models/gullyverse/locked-rev15z-m2a-contact-ground/"/>;}
