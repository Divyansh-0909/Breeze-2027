import { Box3, Mesh, MeshStandardMaterial, TextureLoader, Vector3, type Object3D, type Texture } from "three";
import source from "@/public/models/gullyverse/locked-rev15z-team/manifest.json";
import { lookAtPose, world } from "../immersive/world";
import walkSpace from "./cypher-walk-space.json";

const assetPath = "/models/gullyverse/locked-rev15z-team/";
export const teamSlides = source.slides;
const first = teamSlides[0];
const centre = first.centre as [number, number, number];
const maxWidth = Math.max(...teamSlides.map(slide => slide.widthM));
const distance = 5.726;
const viewingPosition = [centre[0] - distance, 7.2 + world.eyeHeight, centre[2]] as const;
export const teamFocus = lookAtPose(viewingPosition, [centre[0], centre[1] - 0.75, centre[2]]);

export function teamView(aspect: number, position: readonly number[]) {
  const aim = lookAtPose(position, centre);
  const metres = Math.hypot(centre[0] - position[0], centre[2] - position[2]);
  const frameHeight = Math.max(first.heightM / 0.66, maxWidth / (0.90 * aspect));
  const initialLens = frameHeight / (2 * Math.max(metres, 1));
  const pitch = aim.pitch - Math.atan(0.22 * initialLens);
  // With downward pitch the upper mural corners sit closer to the camera.
  const sine = Math.sin(pitch);
  const nearestEdge = metres * Math.cos(pitch) + (centre[1] - position[1]) * sine -
    first.heightM / 2 * Math.abs(sine);
  const halfLens = Math.max(initialLens, maxWidth / (2 * 0.92 * aspect * Math.max(nearestEdge, 1)));
  return {
    pitch,
    fov: 2 * Math.atan(halfLens) * 180 / Math.PI,
  };
}

export function teamIndex(value: string | undefined) {
  if (!value || !/^\d+$/.test(value)) return 0;
  const index = Number(value);
  return index < teamSlides.length ? index : 0;
}

export function nextTeam(index: number, direction: -1 | 1) {
  return (index + direction + teamSlides.length) % teamSlides.length;
}

export type TeamDisplay = { index: number; status: "ready" | "loading" | "error" };
export const defaultTeam: TeamDisplay = { index: 0, status: "ready" };

export function mountTeamCarousel(plaza: Object3D) {
  const matches: Mesh[] = [];
  plaza.traverse(object => {
    if (object instanceof Mesh && object.visible && object.userData.artKind === "mural-composition" &&
        object.userData.carouselSlide === 0) matches.push(object);
  });
  const [mesh] = matches;
  if (matches.length !== 1 || !(mesh.material instanceof MeshStandardMaterial) || !mesh.material.map ||
      source.sourceSHA256 !== walkSpace.sourceSHA256) return null;

  const original = mesh.material;
  const originalMap = original.map;
  const position = mesh.position.z;
  const scale = mesh.scale.z;
  mesh.updateWorldMatrix(true, false);
  const bounds = new Box3().setFromObject(mesh, true);
  const anchor = bounds.getCenter(new Vector3());
  // Both plaza export tiers use the same wall-aligned quad. The fallback export
  // keeps absolute coordinates in the vertices instead of centring its node.
  if (anchor.distanceTo(new Vector3(...centre)) > 0.002 || Math.abs(bounds.max.z - bounds.min.z - first.widthM) > 0.002 ||
      Math.abs(bounds.max.y - bounds.min.y - first.heightM) > 0.002 || Math.abs(bounds.max.x - bounds.min.x) > 0.002 ||
      mesh.quaternion.angleTo(mesh.quaternion.clone().identity()) > 0.0001 || scale === 0) return null;
  const pivot = mesh.worldToLocal(anchor).z;
  const loader = new TextureLoader();
  const alternate = original.clone();
  alternate.onBeforeCompile = original.onBeforeCompile;
  alternate.customProgramCacheKey = original.customProgramCacheKey;
  let current = 0;
  let replacement: Texture | null = null;
  let disposed = false;

  function display(index: number, texture: Texture | null) {
    const width = teamSlides[index].widthM / first.widthM;
    mesh.scale.z = scale * width;
    mesh.position.z = position + pivot * scale * (1 - width);
    if (texture) {
      alternate.map = texture;
      mesh.material = alternate;
    } else {
      mesh.material = original;
      alternate.map = null;
    }
    replacement?.dispose();
    replacement = texture;
    current = index;
  }

  return {
    get index() { return current; },
    async show(index: number, signal: AbortSignal) {
      if (disposed || current === index) return;
      const file = teamSlides[index].file;
      if (!file) {
        display(index, null);
        return;
      }
      const response = await fetch(assetPath + file, { signal });
      if (!response.ok) throw Error("Could not load the mural.");
      const blob = await response.blob();
      signal.throwIfAborted();
      const url = URL.createObjectURL(blob);
      try {
        const texture = await loader.loadAsync(url);
        if (disposed || signal.aborted) {
          texture.dispose();
          return;
        }
        texture.colorSpace = originalMap.colorSpace;
        texture.flipY = originalMap.flipY;
        texture.anisotropy = originalMap.anisotropy;
        display(index, texture);
      } finally {
        URL.revokeObjectURL(url);
      }
    },
    dispose() {
      disposed = true;
      display(0, null);
      alternate.dispose();
    },
  };
}
