"use client";
import React, { useEffect, useMemo, useRef, useState } from "react";
import { useFrame } from "@react-three/fiber";
import * as THREE from "three";
import { GATE, NIGHT } from "./palette";
import {
  lighten,
  makeBeamTexture,
  makePillarTexture,
  makePlinthTexture,
  sampleBottomColor,
} from "./textures";

/**
 * Real artwork for a board if it has been dropped into `public/gate/`,
 * otherwise the procedural print stays. Keeping the fallback means the scene
 * never renders a blank face while art is still being produced, and the app
 * doesn't hard-fail on a missing file.
 */
function useBoardArt(
  url: string,
  fallback: THREE.Texture,
  faceAspect: number
): THREE.Texture {
  const [art, setArt] = useState<THREE.Texture | null>(null);

  useEffect(() => {
    let alive = true;
    // HEAD first so a missing board doesn't spew 404s into the console
    fetch(url, { method: "HEAD" })
      .then((res) => {
        if (!res.ok || !alive) return;
        new THREE.TextureLoader().load(url, (t) => {
          if (!alive) {
            t.dispose();
            return;
          }
          t.colorSpace = THREE.SRGBColorSpace;
          t.anisotropy = 8;

          // cover-fit: centre-crop the overhanging axis rather than stretch,
          // so artwork whose ratio doesn't exactly match its board still
          // reads undistorted
          const img = t.image as { width: number; height: number };
          const ia = img.width / img.height;
          if (ia > faceAspect) {
            t.repeat.set(faceAspect / ia, 1);
          } else {
            t.repeat.set(1, ia / faceAspect);
          }
          t.offset.set((1 - t.repeat.x) / 2, (1 - t.repeat.y) / 2);
          t.needsUpdate = true;
          setArt(t);
        });
      })
      .catch(() => {
        /* no artwork yet — the procedural board stands in */
      });
    return () => {
      alive = false;
    };
  }, [url, faceAspect]);

  return art ?? fallback;
}

/**
 * The arch from the reference photos: two thick printed pillar boards standing
 * on low plinths, carrying one beam that spans the full facade. Structure is
 * boxes; the artwork lives on planes a few millimetres proud of each front
 * face so the print reads as vinyl on board rather than painted geometry.
 *
 * The printed faces use their own artwork as an emissive map, ramped by
 * `powerRef`. Real event signage this size is internally lit or floodlit hard
 * enough to read from across the field — relying on the floods alone left the
 * beam branding sitting in shadow.
 */
export default function Gate({
  powerRef,
}: {
  powerRef: React.MutableRefObject<number>;
}): React.ReactElement {
  const {
    pillarX,
    pillarW,
    pillarH,
    pillarD,
    plinthH,
    plinthW,
    plinthD,
    beamH,
    halfW,
    pillarTopY,
    faceZ,
  } = GATE;

  const beamProc = useMemo(() => makeBeamTexture(), []);
  const leftProc = useMemo(() => makePillarTexture("left"), []);
  const rightProc = useMemo(() => makePillarTexture("right"), []);

  // supplied artwork wins over the procedural print when present
  const beamTex = useBoardArt("/gate/beam.webp", beamProc, (halfW * 2) / beamH);
  const leftTex = useBoardArt("/gate/board-left.webp", leftProc, pillarW / pillarH);
  const rightTex = useBoardArt("/gate/board-right.webp", rightProc, pillarW / pillarH);

  // the plinths carry the poster's colour down to the ground instead of
  // cutting it off with a white shelf. Both take the *left* board's foot tint
  // rather than sampling their own: the two posters end on different colours,
  // and a mismatched pair of bases reads as two structures rather than one
  // arch. Re-derived when the artwork swaps in for the procedural print.
  //
  // Lifted well toward a warm cream afterwards — the posters both end on a
  // near-black footer band, and taking that literally left the arch standing
  // on two dark blocks that vanished into the ground at night.
  const baseTint = useMemo(
    () => lighten(sampleBottomColor(leftTex, NIGHT.boardEdge), 0.62, NIGHT.baseCream),
    [leftTex]
  );

  // shared material for the unprinted returns (sides/top/back of every board)
  const shell = useMemo(
    () =>
      new THREE.MeshStandardMaterial({
        color: NIGHT.boardEdge,
        roughness: 0.82,
        metalness: 0.02,
      }),
    []
  );

  const printed = (tex: THREE.Texture) =>
    new THREE.MeshStandardMaterial({
      map: tex,
      emissiveMap: tex,
      emissive: new THREE.Color("#ffffff"),
      emissiveIntensity: 0,
      roughness: 0.72,
      metalness: 0.0,
    });

  const beamMat = useMemo(() => printed(beamTex), [beamTex]);
  const leftMat = useMemo(() => printed(leftTex), [leftTex]);
  const rightMat = useMemo(() => printed(rightTex), [rightTex]);

  const leftPlinthMat = useMemo(
    () => printed(makePlinthTexture(baseTint)),
    [baseTint]
  );
  const rightPlinthMat = useMemo(
    () => printed(makePlinthTexture(baseTint)),
    [baseTint]
  );

  // the plinth's own returns (sides, top, back) take the same tint, so the
  // base reads as one solid block rather than a coloured card on a pale box
  const plinthShell = (color: string) =>
    new THREE.MeshStandardMaterial({ color, roughness: 0.86, metalness: 0.02 });
  const leftPlinthShell = useMemo(() => plinthShell(baseTint), [baseTint]);
  const rightPlinthShell = useMemo(() => plinthShell(baseTint), [baseTint]);

  // the beam carries the headline branding, so it gets the strongest lift
  const lit = useRef<[THREE.MeshStandardMaterial, number][]>([]);
  lit.current = [
    [beamMat, 0.26],
    [leftMat, 0.17],
    [rightMat, 0.17],
    [leftPlinthMat, 0.14],
    [rightPlinthMat, 0.14],
  ];

  useFrame(() => {
    const p = powerRef.current;
    for (const [m, peak] of lit.current) m.emissiveIntensity = p * peak;
  });

  const beamY = pillarTopY + beamH / 2;

  return (
    <group>
      {/* ---- structure ---- */}
      {[
        { x: -pillarX, base: leftPlinthShell },
        { x: pillarX, base: rightPlinthShell },
      ].map(({ x, base }) => (
        <group key={x}>
          {/* plinth */}
          <mesh position={[x, plinthH / 2, 0]} material={base} castShadow receiveShadow>
            <boxGeometry args={[plinthW, plinthH, plinthD]} />
          </mesh>
          {/* pillar board */}
          <mesh
            position={[x, plinthH + pillarH / 2, 0]}
            material={shell}
            castShadow
            receiveShadow
          >
            <boxGeometry args={[pillarW, pillarH, pillarD]} />
          </mesh>
        </group>
      ))}

      {/* beam spanning the whole facade */}
      <mesh position={[0, beamY, 0]} material={shell} castShadow receiveShadow>
        <boxGeometry args={[halfW * 2, beamH, pillarD]} />
      </mesh>

      {/* ---- printed faces (front, +z) ---- */}
      <mesh position={[0, beamY, faceZ]} material={beamMat}>
        <planeGeometry args={[halfW * 2, beamH]} />
      </mesh>

      <mesh
        position={[-pillarX, plinthH + pillarH / 2, faceZ]}
        material={leftMat}
      >
        <planeGeometry args={[pillarW, pillarH]} />
      </mesh>
      <mesh
        position={[pillarX, plinthH + pillarH / 2, faceZ]}
        material={rightMat}
      >
        <planeGeometry args={[pillarW, pillarH]} />
      </mesh>

      {[
        { x: -pillarX, mat: leftPlinthMat },
        { x: pillarX, mat: rightPlinthMat },
      ].map(({ x, mat }) => (
        <mesh
          key={x}
          position={[x, plinthH / 2, plinthD / 2 + 0.006]}
          material={mat}
        >
          <planeGeometry args={[plinthW, plinthH]} />
        </mesh>
      ))}

      {/* inner reveals of the opening catch a little bounce, which is what
          makes the arch read as having real thickness */}
      {[-1, 1].map((s) => (
        <mesh
          key={s}
          position={[s * (GATE.openingW / 2), (plinthH + pillarH) / 2, 0]}
          rotation-y={s * -Math.PI / 2}
          material={shell}
        >
          <planeGeometry args={[pillarD, plinthH + pillarH]} />
        </mesh>
      ))}
      <mesh position={[0, pillarTopY - 0.002, 0]} rotation-x={Math.PI / 2} material={shell}>
        <planeGeometry args={[GATE.openingW, pillarD]} />
      </mesh>
    </group>
  );
}
