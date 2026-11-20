import React, { useEffect, useRef, useState } from "react";
import { createRoot } from "react-dom/client";
import { Canvas, useFrame, useThree } from "@react-three/fiber";
import * as THREE from "three";
import { GLTFLoader } from "three/examples/jsm/loaders/GLTFLoader.js";
import { RGBELoader } from "three/examples/jsm/loaders/RGBELoader.js";
import { KTX2Loader } from "three/examples/jsm/loaders/KTX2Loader.js";
import { MeshoptDecoder } from "three/examples/jsm/libs/meshopt_decoder.module.js";
import { decalProbes } from "./decal-probes";
import { mountContactForm } from "./contact-form.js";

declare global {
  interface Window {
    __lockedPilot: any;
  }
}
const read = async (url: string) => {
  const r = await fetch(url);
  if (!r.ok) throw Error(`Could not load ${url}: ${r.status}`);
  return r.json();
};
const point = (p: number[]) => new THREE.Vector3(p[0], p[2], -p[1]);
const cache = new Map<string, { users: number; promise: Promise<any> }>();
function dispose(asset: any) {
  const geometries = new Set<THREE.BufferGeometry>(),
    materials = new Set<THREE.Material>(),
    textures = new Set<THREE.Texture>();
  asset.scene.traverse((o: any) => {
    if (o.geometry) geometries.add(o.geometry);
    for (const m of o.material
      ? Array.isArray(o.material)
        ? o.material
        : [o.material]
      : []) {
      materials.add(m);
      for (const v of Object.values(m))
        if (v instanceof THREE.Texture) textures.add(v);
    }
  });
  geometries.forEach((x) => x.dispose());
  materials.forEach((x) => x.dispose());
  textures.forEach((x) => x.dispose());
  asset.ktx.dispose();
}
function acquire(url: string, renderer: THREE.WebGLRenderer, bake: any) {
  let entry = cache.get(url);
  if (!entry) {
    const ktx = new KTX2Loader()
        .setTranscoderPath("transcoders/")
        .detectSupport(renderer),
      loader = new GLTFLoader()
        .setKTX2Loader(ktx)
        .setMeshoptDecoder(MeshoptDecoder);
    const promise = (async () => {
      let loaded: any = null;
      let irradiance: THREE.Texture | null = null;
      try {
        const gltf = await loader.loadAsync(url);
        loaded = gltf;
        const light = bake.ktxURI
          ? await ktx.loadAsync(bake.ktxURI)
          : await new RGBELoader().loadAsync("lightmap.hdr");
        irradiance = light;
        light.flipY = false;
        // Linear HDR is averaged before RGBM mip packing.
        light.generateMipmaps = !bake.ktxURI;
        light.minFilter = THREE.LinearMipmapLinearFilter;
        light.magFilter = THREE.LinearFilter;
        light.colorSpace = THREE.NoColorSpace;
        const bindings: any[] = [];
        gltf.scene.traverse((o: any) => {
          if (!o.isMesh) return;
          const list = Array.isArray(o.material) ? o.material : [o.material];
          for (const material of list) {
            for (const value of Object.values(material)) if (value instanceof THREE.Texture) value.anisotropy = Math.min(8, renderer.capabilities.getMaxAnisotropy());
            if (material.userData.runtimeDecal) {
              o.castShadow = false; material.transparent = true; material.depthWrite = false; material.alphaTest = 1 / 255;
              material.polygonOffset = true; material.polygonOffsetFactor = -1; material.polygonOffsetUnits = -1;
            }
          }
          for (const m of list) {
            const channel = Number(m.userData.runtimeLightmapChannel);
            if (
              !Number.isInteger(channel) ||
              !o.geometry.getAttribute(channel === 0 ? "uv" : `uv${channel}`)
            )
              throw Error(`Missing lightmap UV channel on ${o.name}`);
            const lm = light.clone();
            lm.channel = channel;
            lm.needsUpdate = true;
            m.lightMap = lm;
            m.lightMapIntensity = Math.PI;
            if (bake.ktxURI)
              m.onBeforeCompile = (shader: any) => {
                const from =
                    "vec3 lightMapIrradiance = lightMapTexel.rgb * lightMapIntensity;",
                  to = `vec3 lightMapIrradiance = lightMapTexel.rgb * lightMapTexel.a * ${Number(bake.range).toFixed(1)} * lightMapIntensity;`;
                if (!THREE.ShaderChunk.lights_fragment_maps.includes(from))
                  throw Error("Three lightmap shader contract changed");
                shader.fragmentShader = shader.fragmentShader.replace(
                  "#include <lights_fragment_maps>",
                  THREE.ShaderChunk.lights_fragment_maps.replace(from, to),
                );
              };
            m.customProgramCacheKey = () =>
              `breeze-${bake.ktxURI ? "rgbm-" + bake.range : "hdr"}-v1`;
            m.needsUpdate = true;
            bindings.push({
              node: o.name,
              material: m.name,
              channel,
              rgbmRange: bake.range,
            });
          }
        });
        return { scene: gltf.scene, ktx, bindings, light };
      } catch (e) {
        if (loaded) dispose({ scene: loaded.scene, ktx });
        else ktx.dispose();
        irradiance?.dispose();
        throw e;
      }
    })();
    entry = { users: 0, promise };
    cache.set(url, entry);
    promise.catch(() => {
      if (cache.get(url) === entry) cache.delete(url);
    });
  }
  entry.users++;
  let released = false;
  return {
    promise: entry.promise,
    release() {
      if (released) return;
      released = true;
      entry!.users--;
      if (entry!.users === 0) {
        const owned = entry!;
        cache.delete(url);
        owned.promise.then(
          (a) => {
            dispose(a);
            a.light.dispose();
          },
          () => {},
        );
      }
    },
  };
}
const samples: number[] = [];
let info: any = {
  ready: false,
  scope:
    "PRIVATE representative chunk; not a full visitor journey or physical-device benchmark",
};
function stats(renderer: THREE.WebGLRenderer, scene: THREE.Scene) {
  const geometries = new Set<any>(),
    textures = new Map<string, any>(),
    materials = new Set<any>();
  let triangles = 0;
  scene.traverse((o: any) => {
    if (!o.isMesh) return;
    geometries.add(o.geometry);
    triangles +=
      (o.geometry.index?.count ?? o.geometry.attributes.position.count) / 3;
    for (const m of Array.isArray(o.material) ? o.material : [o.material]) {
      materials.add(m);
      for (const v of Object.values(m))
        if (v instanceof THREE.Texture)
          textures.set(v.source.uuid + ":" + v.colorSpace, v);
    }
  });
  let geometryBytes = 0,
    gpuTextureBytesProxy = 0;
  const arrays = new Set<any>();
  geometries.forEach((g) => {
    for (const a of Object.values(g.attributes) as any[]) {
      const data = a.isInterleavedBufferAttribute ? a.data.array : a.array;
      if (data) arrays.add(data);
    }
    if (g.index?.array) arrays.add(g.index.array);
  });
  arrays.forEach((a) => (geometryBytes += a.byteLength));
  textures.forEach((t) => {
    gpuTextureBytesProxy += t.isCompressedTexture
      ? t.mipmaps.reduce((n: number, m: any) => n + m.data.byteLength, 0)
      : ((t.image?.width ?? 0) * (t.image?.height ?? 0) * 4 * 4) / 3;
  });
  const sorted = samples.slice(20).sort((a, b) => a - b),
    pct = (q: number) =>
      sorted.length ? sorted[Math.floor((sorted.length - 1) * q)] : null;
  const gl = renderer.getContext(),
    ext = gl.getExtension("WEBGL_debug_renderer_info");
  return {
    ...info,
    canvasCount: document.querySelectorAll("canvas").length,
    triangles,
    materials: materials.size,
    geometries: geometries.size,
    textures: textures.size,
    geometryBytes,
    gpuTextureBytesProxy,
    drawCalls: renderer.info.render.calls,
    textureFormats: [...new Set([...textures.values()].map((t) => t.format))],
    frameSamples: sorted.length,
    frameMs: { p50: pct(0.5), p95: pct(0.95), p99: pct(0.99) },
    renderer: gl.getParameter(ext?.UNMASKED_RENDERER_WEBGL ?? gl.RENDERER),
    glError: gl.getError(),
  };
}
function View({
  mode,
  manifest,
  contact,
  onReady,
  onError,
  view,
}: {
  mode: string;
  manifest: any;
  contact: any;
  onReady: () => void;
  onError: (s: string) => void;
  view: string;
}) {
  const { gl, scene, camera, size } = useThree();
  const [asset, setAsset] = useState<any>(null);
  const start = useRef(performance.now());
  useEffect(() => {
    let alive = true;
    setAsset(null);
    info = {
      ready: false,
      mode,
      scope:
        "PRIVATE source-derived representative chunk; not full-world integration",
    };
    samples.length = 0;
    start.current = performance.now();
    const optimized = mode !== "png";
    const bake = {
      ...manifest.bake,
      ktxURI: optimized ? "lightmap.ktx2" : null,
    };
    const lease = acquire(
      optimized
        ? mode === "mobile"
          ? "contact-frontage.mobile.glb"
          : "contact-frontage.optimized.glb"
        : "contact-frontage.png.glb",
      gl,
      bake,
    );
    lease.promise.then(
      (a) => {
        if (alive) {
          setAsset(a);
          info = {
            ...info,
            bindings: a.bindings,
            loadMs: performance.now() - start.current,
          };
        }
      },
      (e) => {
        if (alive) onError(String(e));
      },
    );
    return () => {
      alive = false;
      lease.release();
    };
  }, [mode, manifest, gl]);
  useEffect(() => {
    gl.toneMapping = THREE.AgXToneMapping;
    gl.toneMappingExposure = Math.pow(2, 0.25);
    scene.background = new THREE.Color("#010303");
    const centre = new THREE.Vector3(...contact.frameCentre);
    centre.z = 8.95;
    const n = new THREE.Vector3(...contact.normal),
      t = new THREE.Vector3(...contact.tangent);
    const position = centre
      .clone()
      .addScaledVector(n, view === "front" ? 6.7 : 6.9);
    if (view !== "front")
      position.addScaledVector(t, 0.8).add(new THREE.Vector3(0, 0, 0.35));
    camera.position.copy(point(position.toArray()));
    camera.lookAt(point(centre.toArray()));
    if (camera instanceof THREE.PerspectiveCamera) {
      camera.fov = 35.6;
      camera.updateProjectionMatrix();
    }
  }, [contact, view, camera, gl, scene]);
  useEffect(() => {
    if (!asset) return;
    let alive = true;
    const begin = performance.now();
    void gl.compileAsync(scene, camera).then(
      () => {
        if (alive) {
          info = {
            ...info,
            ready: true,
            compileMs: performance.now() - begin,
            loadAndCompileMs: performance.now() - start.current,
          };
          onReady();
        }
      },
      (e) => onError(String(e)),
    );
    return () => {
      alive = false;
    };
  }, [asset, gl, scene, camera]);
  useFrame((_, dt) => {
    if (info.ready && samples.length < 360) samples.push(dt * 1000);
    const host = document.getElementById("form-host");
    if (!host || innerWidth < 700 || view !== "front") return;
    const n = new THREE.Vector3(...contact.normal),
      t = new THREE.Vector3(...contact.tangent),
      P = (u: number, z: number) =>
        point(
          t
            .clone()
            .multiplyScalar(u)
            .addScaledVector(n, contact.messageDepth)
            .add(new THREE.Vector3(0, 0, z))
            .toArray(),
        ).project(camera);
    const a = P(contact.messageBoundsU[0], contact.messageBoundsZ[1]),
      b = P(contact.messageBoundsU[1], contact.messageBoundsZ[0]);
    Object.assign(host.style, {
      left: `${((a.x + 1) * size.width) / 2}px`,
      top: `${((1 - a.y) * size.height) / 2}px`,
      width: `${((b.x - a.x) * size.width) / 2}px`,
      height: `${((a.y - b.y) * size.height) / 2}px`,
    });
  });
  useEffect(() => {
    window.__lockedPilot = {
      stats: () => stats(gl, scene),
      ready: () => info.ready,
      decalProbes: () => decalProbes(scene, camera, size.width, size.height),
      cache: () => ({
        entries: cache.size,
        users: [...cache.values()].reduce((n, e) => n + e.users, 0),
        gpu: gl.info.memory,
      }),
      debug: (kind: string) => {
        scene.traverse((o: any) => {
          if (!o.isMesh) return;
          if (kind === "hide-decals" || kind === "show-decals") {
            const list=Array.isArray(o.material)?o.material:[o.material];
            if(list.some((m:any)=>m.userData.runtimeDecal))o.visible=kind === "show-decals";
          }
          for (const m of Array.isArray(o.material)
            ? o.material
            : [o.material]) {
            if (kind === "flip" && m.lightMap) {
              m.lightMap.flipY = !m.lightMap.flipY;
              m.lightMap.needsUpdate = true;
            }
            if (kind === "color") {
              m.lightMapIntensity = 0;
              m.normalMap = null;
              m.roughness = 1;
              m.metalness = 0;
              m.needsUpdate = true;
            }
            if (kind === "light") {
              m.map = null;
              m.normalMap = null;
              m.color.setRGB(1, 1, 1);
              m.emissive.setRGB(0, 0, 0);
              m.metalness = 0;
              m.roughness = 1;
              m.needsUpdate = true;
            }
          }
        });
        if (kind === "color")
          scene.add(new THREE.AmbientLight(0xffffff, Math.PI));
      },
    };
  }, [gl, scene, camera, size.width, size.height]);
  return asset ? <primitive object={asset.scene} /> : null;
}
function App() {
  const [config, setConfig] = useState<any>(null),
    [mode, setMode] = useState("png"),
    [view, setView] = useState("front"),
    [formOpen, setFormOpen] = useState(true),
    [ready, setReady] = useState(false),
    [error, setError] = useState(""),
    [serial, setSerial] = useState(0);
  const [width, setWidth] = useState(innerWidth);
  const host = useRef<HTMLDivElement>(null);
  useEffect(() => {
    void Promise.all([read("manifest.json"), read("contact.json")]).then(
      ([manifest, contact]) => setConfig({ manifest, contact }),
      (e) => setError(String(e)),
    );
    const resize = () => setWidth(innerWidth);
    addEventListener("resize", resize);
    return () => removeEventListener("resize", resize);
  }, []);
  useEffect(() => {
    if (!host.current) return;
    const form = mountContactForm(host.current, {
      submit: async () => {
        throw Error("Private preview only. Your message was not sent.");
      },
      onClose: () => setFormOpen(false),
    });
    return () => form.dispose();
  }, [config]);
  const change = (next: string) => {
    setReady(false);
    setError("");
    setMode(next);
    setSerial((x) => x + 1);
  };
  return (
    <>
      <header>
        <strong>Locked world — baked runtime pilot</strong>
        <small>
          Actual Contact house geometry · source artwork preserved · one canvas
          <br />
          Representative M1 export. Full-world journey integration is pending.
        </small>
        <nav>
          {!formOpen && (
            <button onClick={() => setFormOpen(true)}>Show form</button>
          )}
          <button onClick={() => change("png")}>PNG baseline</button>
          <button onClick={() => change(width < 700 ? "mobile" : "compressed")}>
            KTX2 + Meshopt
          </button>
          <button
            onClick={() => setView(view === "front" ? "context" : "front")}
          >
            Change view
          </button>
        </nav>
      </header>
      {config && (
        <div
          className="canvas-holder"
          style={{ height: width < 700 ? 320 : "100vh" }}
        >
          <Canvas
            dpr={1}
            gl={{ antialias: true, powerPreference: "high-performance" }}
            camera={{ fov: 35.6, near: 0.05, far: 100 }}
          >
            <View
              key={serial}
              mode={mode}
              manifest={config.manifest}
              contact={config.contact}
              view={view}
              onReady={() => setReady(true)}
              onError={setError}
            />
          </Canvas>
        </div>
      )}
      <div
        id="form-host"
        ref={host}
        hidden={!ready || view !== "front" || !formOpen}
      />
      {(!ready || error) && (
        <div className="loading" role="status">
          {error || "Loading and preparing baked materials…"}
          {error && (
            <button onClick={() => change("png")}>Retry PNG fallback</button>
          )}
        </div>
      )}
      <footer>
        Private engineering preview · baked night lighting · no messages sent ·
        desktop/device performance unverified
      </footer>
    </>
  );
}
createRoot(document.getElementById("root")!).render(<App />);
