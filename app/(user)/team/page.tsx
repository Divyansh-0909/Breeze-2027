"use client";

import { ArrowUpRight } from "lucide-react";
import { useEffect, useState } from "react";
import TeamApproach from "./BackstageCorridor";
import styles from "./team-scene.module.css";

export default function TeamPage() {
  const [arrived, setArrived] = useState(false);
  const [instant, setInstant] = useState(false);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const shouldJump = params.get("review") === "board" || window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (shouldJump) {
      setInstant(true);
      setArrived(true);
    }
  }, []);

  const skipApproach = () => {
    setInstant(true);
    setArrived(true);
  };

  return <main className={styles.experience}><section className={styles.scene}><TeamApproach onFinish={() => setArrived(true)} instant={instant} /><div className={`${styles.sceneCopy} ${arrived ? styles.sceneCopyHidden : ""}`} aria-hidden={arrived}><span>FIELD NOTES / 27</span><strong>THE TEAM<br />IS <em>HERE.</em></strong></div><button className={`${styles.skip} ${arrived ? styles.skipHidden : ""}`} onClick={skipApproach} aria-hidden={arrived} tabIndex={arrived ? -1 : 0}>SKIP APPROACH <ArrowUpRight size={15} /></button><header className={`${styles.settledLabel} ${arrived ? styles.settledLabelVisible : ""}`} aria-hidden={!arrived}><span><i /> BREEZE ’27 / FESTIVAL TEAM BOARD</span><span>SHARDA UNIVERSITY · GREATER NOIDA</span></header></section></main>;
}
