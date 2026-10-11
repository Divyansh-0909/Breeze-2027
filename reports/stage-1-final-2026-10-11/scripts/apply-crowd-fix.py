from pathlib import Path
p=Path('components/landing-page/stage3d/Crowd.tsx');s=p.read_text().replace('import { mergeGeometries }','import { disposeUnpublishedPoses } from "./poseResources";\nimport { mergeGeometries }')
a=s.index('  const geoms: THREE.BufferGeometry[] = [];');b=s.index('\ntype Person',a)
s=s[:a]+'''  const geoms: THREE.BufferGeometry[] = [];
  let merged: THREE.BufferGeometry | null = null;
  try {
    const v = new THREE.Vector3();
    root.traverse((o) => {
      const sm = o as THREE.SkinnedMesh;
      if (!sm.isSkinnedMesh) return;
      sm.skeleton.update();
      const src = sm.geometry, pos = src.attributes.position as THREE.BufferAttribute;
      const baked = new Float32Array(pos.count * 3);
      for (let i = 0; i < pos.count; i++) {
        v.fromBufferAttribute(pos, i); sm.applyBoneTransform(i, v); v.applyMatrix4(sm.matrixWorld);
        baked.set([v.x, v.y, v.z], i * 3);
      }
      const geometry = new THREE.BufferGeometry(); geoms.push(geometry);
      geometry.setAttribute("position", new THREE.BufferAttribute(baked, 3));
      if (src.index) geometry.setIndex(src.index.clone());
    });
    merged = mergeGeometries(geoms, false);
    if (!merged) throw new Error("Crowd pose could not be merged");
    merged.computeVertexNormals(); merged.computeBoundingBox();
    const bb = merged.boundingBox!, height = bb.max.y - bb.min.y;
    if (!Number.isFinite(height) || height <= 0) throw new Error("Invalid crowd pose height");
    merged.translate(-(bb.min.x + bb.max.x) / 2, -bb.min.y, -(bb.min.z + bb.max.z) / 2);
    merged.scale(1 / height, 1 / height, 1 / height);
    return merged;
  } catch (error) { merged?.dispose(); throw error; }
  finally { geoms.forEach(geometry => geometry.dispose()); mixer.stopAllAction(); mixer.uncacheRoot(root); }
}
'''+s[b:]
s=s.replace('let warmBaked: THREE.BufferGeometry[] | null = null;','''let warmBaked: THREE.BufferGeometry[] | null = null;
function publishPoses(out: THREE.BufferGeometry[]) {
  if (!warmBaked) warmBaked = out;
  else if (warmBaked !== out) disposeUnpublishedPoses(out, warmBaked);
  return warmBaked;
}
function bakeAll(man: GLTF, woman: GLTF) {
  const out: THREE.BufferGeometry[] = [];
  try { for (const gltf of [man, woman]) for (const time of POSE_TIMES) out.push(bakePose(gltf.scene, gltf.animations, time)); return publishPoses(out); }
  catch (error) { disposeUnpublishedPoses(out, warmBaked); throw error; }
}''')
s=s.replace('''    for (const [gltf, t] of jobs) {
      // spaced out so the page hosting the warm-up never feels it
      await new Promise((r) => setTimeout(r, 150));
      out.push(bakePose(gltf.scene, gltf.animations, t));
    }
    warmBaked = out;''','''    try {
      for (const [gltf, t] of jobs) {
        await new Promise((r) => setTimeout(r, 150));
        out.push(bakePose(gltf.scene, gltf.animations, t));
      }
      publishPoses(out);
    } finally { disposeUnpublishedPoses(out, warmBaked); }''')
a=s.index('      (immediate\n        ? [');b=s.index('\n        : null),',a)
s=s[:a]+'''      (immediate
        ? bakeAll(manGltf, womanGltf)'''+s[b:]
s=s.replace('  const [chunked, setChunked] = useState<THREE.BufferGeometry[]>([]);','  const [chunked, setChunked] = useState<THREE.BufferGeometry[]>([]);\n  const [bakeError, setBakeError] = useState<Error | null>(null);')
a=s.index('    void (async () => {');b=s.index('  }, [immediate, syncVariants',a)
s=s[:a]+'''    void (async () => {
      try {
        for (const [gltf, t] of jobs) {
          await new Promise((resolve) => setTimeout(resolve, bakeDelayMs));
          if (!alive) return;
          const start = performance.now();
          out.push(bakePose(gltf.scene, gltf.animations, t));
          onBake?.(performance.now() - start);
        }
        if (alive) setChunked(publishPoses(out));
      } catch (error) { if (alive) setBakeError(error instanceof Error ? error : new Error(String(error))); }
      finally { disposeUnpublishedPoses(out, warmBaked); }
    })();
    return () => { alive = false; disposeUnpublishedPoses(out, warmBaked); };
'''+s[b:]
s=s.replace('      warmBaked = variants;','      publishPoses(variants);')
s=s.replace('  return (\n    <group>','  if (bakeError) throw bakeError;\n  return (\n    <group>')
p.write_text(s)
