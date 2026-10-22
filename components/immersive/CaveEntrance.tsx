'use client';
import {useEffect, useMemo, useRef, useSyncExternalStore} from 'react';
import {useFrame, useThree} from '@react-three/fiber';
import * as THREE from 'three';
import type {CaveEntranceSession} from './CaveEntranceSession';
import {chooseWallLOD, projectedWallPixels} from './wallSection';
import {renderQuarryPreparation} from './quarryPreparation';

export default function CaveEntrance({session, quality, needed}: {session: CaveEntranceSession; quality: number; needed: boolean}) {
  const state = useSyncExternalStore(session.subscribe, session.snapshot, session.snapshot);
  const {gl, scene, camera} = useThree();
  useEffect(() => { if (needed) session.requireCave(); }, [needed, session, state.mode]);
  const entranceReady = session.entranceReady, materialRevision = session.materialRevision;
  const clone = useMemo(() => {
    if (!state.assetReady || !entranceReady || materialRevision < 1) return null;
    return session.cloneEntrance();
  }, [session, state.assetReady, entranceReady, materialRevision]);
  const parts = useMemo(() => clone ? session.entranceParts.map(part => ({...part, level: 2,
    point: new THREE.Vector3().fromArray(part.center), meshes: part.nodes.map(name => clone.getObjectByName(name) as THREE.Mesh)})) : [], [clone, session]);
  const size = useRef(new THREE.Vector2()), warmed = useRef(0);
  useEffect(() => { if (!clone) return; session.retainConsumer(); return () => session.releaseConsumer(); }, [clone, session]);
  useEffect(() => { warmed.current = 0; }, [state.busy, state.revision]);
  useFrame(() => {
    if (!clone || session.runtime.suspended || gl.getContext().isContextLost()) return;
    if (session.state.busy) {
      const level = Math.min(2, warmed.current++);
      parts.forEach(part => part.meshes.forEach((mesh, i) => { mesh.visible = i === level; mesh.frustumCulled = false; }));
      if (warmed.current <= 3) renderQuarryPreparation(gl, scene, camera, clone);
      return;
    }
    if (!(camera instanceof THREE.PerspectiveCamera)) return;
    gl.getDrawingBufferSize(size.current);
    for (const part of parts) {
      const pixels = projectedWallPixels(part.point, part.radius, camera, size.current.y);
      const next = chooseWallLOD(pixels, quality, part.level);
      if (next !== part.level) session.record('cave-lod-change', {part: part.id, from: part.level, to: next, pixels, quality});
      part.level = next;
      part.meshes.forEach((mesh, i) => { mesh.visible = i === next; mesh.frustumCulled = true; });
      session.lodSelections['Cave_' + part.id] = next;
    }
  });
  return clone ? <group name="Private_Natural_Cave_Entrance"><primitive object={clone} dispose={null}/></group> : null;
}
