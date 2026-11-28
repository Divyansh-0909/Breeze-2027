import * as THREE from "three";
import type { CypherEvent } from "../../lib/events/cypher-catalog";
import contactConfig from "./contact-space.json";
import frontage from "@/public/models/gullyverse/locked-rev15z-clean-v2/contact.json";
import { contactSpace } from "./native-space";
import { accommodationGeometry } from "./cypher-accommodation";
import { loadPosterImage, placeholderPosters, posterCard, weatherPoster } from "./event-wall-art";
import { booth, contactSitters, enquiryBoard, stoolSeat, windowHole } from "./contact-booth";
import { eventsLettering, pastGigs, signSheet, sprayEvents } from "./wall-art";
import {
  FLOOR, SODIUM, TUBE, TUNGSTEN, atlasBox, quad, strut, toRegion, vec,
  type DressingSink, type V, type ZoneHooks,
} from "./courtyard-dressing";
import type { Region } from "./dressing-textures";

/**
 * Phase 3 zone dressing (docs/runtime/PHASE3-ZONES-PLAN.md): entrance gate, events wall, organising-committee mural
 * lamp, accommodation and contact booth. Every part joins the courtyard's merged families through the sink
 * (steel, emissive lenses, props, decals, glow sprites, pools); the only new draw is the events poster atlas. States
 * (how many events, accommodation open or closed) are decided once per visit, so everything stays static.
 *
 * Positions come from the Phase 3 surveys (merged-off scene; numbers in the plan's "Surveyed geometry").
 */
export type ZoneState = { events: readonly CypherEvent[]; stayOpen: boolean };

/** What the scene's click handler needs from the events wall: the event (or "list") under each poster quad. */
export type PosterTarget = string | "list" | null;

const label = (o: THREE.Object3D) => String(o.userData.runtimeOriginalSource ?? o.userData.sourceObjectName ?? o.name);
/** Baked parts the zones replace (kept as separate objects by the chunk layout so they can be hidden). The team wall's
 * black-painted brick is a decal over the building's plaster: hidden, so the mural sits on the building's own colour. */
export const replacedByZones = /EVENTS clearly labelled placeholder|PILOT \/ poster outside horizontal retain|PILOT \/ poster washer fixing|COMING above SOON graffiti|Full-width message surface inside window|Team wall black-painted brick finish|CONTACT US colourful wall graffiti|EVENTS destination heading/;
export const isReplacedByZones = (mesh: THREE.Object3D) => replacedByZones.test(label(mesh));

/** Recolours a decal quad's vertex tone (the atlas ink is chalk; this tints it, e.g. toward rusty tan). */
const tint = (g: THREE.BufferGeometry, colour: THREE.Color, k: number) => {
  const c = g.getAttribute("color") as THREE.BufferAttribute;
  for (let i = 0; i < c.count; i++) c.setXYZ(i, colour.r * k, colour.g * k, colour.b * k);
  return g;
};
const CHALK = new THREE.Color("#e4dccb"), RUST_INK = new THREE.Color("#5a3420");
/** Mirrors a region horizontally (an arrow that points the other way). */
const mirror = (r: Region): Region => [r[2], r[1], r[0], r[3]];

/** A roll-down shutter: horizontal corrugations (zigzag, 75 mm pitch) in a plane facing `normal`, bottom bar and rails. */
function shutter(out: THREE.BufferGeometry[], centre: THREE.Vector3, normal: THREE.Vector3, width: number, height: number) {
  const ridges = Math.max(2, Math.round(height / 0.075));
  const g = new THREE.PlaneGeometry(width, height, 1, ridges * 2);
  const position = g.getAttribute("position") as THREE.BufferAttribute;
  for (let i = 0; i < position.count; i++) {
    const row = Math.round((position.getY(i) + height / 2) / (height / (ridges * 2)));
    position.setZ(i, row % 2 ? 0.034 : 0);
  }
  g.computeVertexNormals();
  const turn = new THREE.Quaternion().setFromUnitVectors(new THREE.Vector3(0, 0, 1), normal.clone().normalize());
  g.applyQuaternion(turn); g.translate(centre.x, centre.y, centre.z);
  out.push(g);
  const side = new THREE.Vector3(1, 0, 0).applyQuaternion(turn);
  const bottom = centre.clone().addScaledVector(new THREE.Vector3(0, 1, 0), -height / 2 + 0.02).addScaledVector(normal, 0.03);
  out.push(strut(bottom.clone().addScaledVector(side, -width / 2), bottom.clone().addScaledVector(side, width / 2), 0.022));
  for (const s of [-1, 1]) {
    const rail = centre.clone().addScaledVector(side, s * (width / 2 + 0.025)).addScaledVector(normal, 0.015);
    out.push(strut(rail.clone().add(new THREE.Vector3(0, -height / 2, 0)), rail.clone().add(new THREE.Vector3(0, height / 2, 0)), 0.02));
  }
}
/** A flat contact-shadow quad on the plaza floor (the courtyard's blob family). */
function blobQuad(x: number, z: number, r: number) {
  const g = new THREE.PlaneGeometry(r * 2, r * 2); g.rotateX(-Math.PI / 2); g.translate(x, FLOOR + 0.006, z);
  return g;
}
/**
 * Collapses (to degenerate triangles) every triangle of `root`'s meshes on materials matching `material` whose three
 * corners lie inside `box` (world space). Used for a post baked into a larger shell mesh. Idempotent per geometry.
 */
function trimTriangles(root: THREE.Object3D, material: RegExp, box: THREE.Box3) {
  let total = 0;
  const v = [new THREE.Vector3(), new THREE.Vector3(), new THREE.Vector3()];
  root.traverse(object => {
    const mesh = object as THREE.Mesh;
    if (!mesh.isMesh || (mesh as unknown as THREE.BatchedMesh).isBatchedMesh || Array.isArray(mesh.material) || !material.test(mesh.material.name)) return;
    const geometry = mesh.geometry, key = `trim ${box.min.toArray()} ${box.max.toArray()}`;
    if (geometry.userData.breezeTrim === key) return;
    const position = geometry.getAttribute("position") as THREE.BufferAttribute, index = geometry.index;
    const count = index ? index.count : position.count;
    let trimmed = 0;
    for (let k = 0; k + 2 < count; k += 3) {
      const ids = [0, 1, 2].map(j => index ? index.getX(k + j) : k + j);
      ids.forEach((id, j) => v[j].fromBufferAttribute(position, id).applyMatrix4(mesh.matrixWorld));
      if (!v.every(p => box.containsPoint(p))) continue;
      if (index) { index.setX(k + 1, ids[0]); index.setX(k + 2, ids[0]); }
      else for (const j of [1, 2]) position.setXYZ(ids[j], position.getX(ids[0]), position.getY(ids[0]), position.getZ(ids[0]));
      trimmed++;
    }
    if (trimmed) { (index ?? position).needsUpdate = true; geometry.userData.breezeTrim = key; total += trimmed; }
  });
  return total;
}
/** A chamfered plate (bevel 15 mm) facing `normal`, so its edges catch light. */
function plate(out: THREE.BufferGeometry[], centre: THREE.Vector3, normal: THREE.Vector3, width: number, height: number, depth: number) {
  const shape = new THREE.Shape();
  shape.moveTo(-width / 2, -height / 2); shape.lineTo(width / 2, -height / 2); shape.lineTo(width / 2, height / 2); shape.lineTo(-width / 2, height / 2);
  const g = new THREE.ExtrudeGeometry(shape, { depth: depth * 0.4, bevelEnabled: true, bevelThickness: depth * 0.3, bevelSize: 0.015, bevelSegments: 1 });
  g.deleteAttribute("uv");
  g.applyQuaternion(new THREE.Quaternion().setFromUnitVectors(new THREE.Vector3(0, 0, 1), normal.clone().normalize()));
  g.translate(centre.x, centre.y, centre.z);
  out.push(g);
}
/** A domed rivet head (18 mm). */
function rivet(out: THREE.BufferGeometry[], at: THREE.Vector3, normal: THREE.Vector3) {
  const g = new THREE.SphereGeometry(0.018, 6, 3, 0, Math.PI * 2, 0, Math.PI / 2);
  g.deleteAttribute("uv");
  g.applyQuaternion(new THREE.Quaternion().setFromUnitVectors(new THREE.Vector3(0, 1, 0), normal.clone().normalize()));
  g.translate(at.x, at.y, at.z);
  out.push(g);
}
/** A steel box oriented with its +z face along `normal` (position + normal only: the steel family). */
function steelBox(out: THREE.BufferGeometry[], size: V, at: THREE.Vector3, normal: THREE.Vector3) {
  const g = new THREE.BoxGeometry(size[0], size[1], size[2]);
  g.deleteAttribute("uv");
  g.applyQuaternion(new THREE.Quaternion().setFromUnitVectors(new THREE.Vector3(0, 0, 1), normal.clone().normalize()));
  g.translate(at.x, at.y, at.z);
  out.push(g);
}
/** A decal quad with a semicircular cut (radius `r`) at the middle of its bottom edge (the grille's speaking cut). */
function notchedQuad(centre: THREE.Vector3, normal: THREE.Vector3, width: number, height: number, region: Region, brightness: number, r: number) {
  const w = width / 2, h = height / 2, shape = new THREE.Shape();
  shape.moveTo(-w, -h); shape.lineTo(-r, -h);
  shape.absarc(0, -h, r, Math.PI, 0, true);
  shape.lineTo(w, -h); shape.lineTo(w, h); shape.lineTo(-w, h); shape.closePath();
  const g = new THREE.ShapeGeometry(shape, 16);
  const pos = g.getAttribute("position") as THREE.BufferAttribute, uvs: number[] = [];
  for (let i = 0; i < pos.count; i++) {
    const u = (pos.getX(i) + w) / width, v = (pos.getY(i) + h) / height;
    uvs.push(region[0] + u * (region[2] - region[0]), region[1] + v * (region[3] - region[1]));
  }
  g.setAttribute("uv", new THREE.Float32BufferAttribute(uvs, 2));
  g.applyQuaternion(new THREE.Quaternion().setFromUnitVectors(new THREE.Vector3(0, 0, 1), normal.clone().normalize()));
  g.translate(centre.x, centre.y, centre.z);
  const n = g.getAttribute("position").count;
  g.setAttribute("color", new THREE.Float32BufferAttribute(new Array(n * 3).fill(brightness), 3));
  return g.toNonIndexed();
}
/** Merges textured quads into one geometry (position, normal, uv only). */
function mapGeometry(parts: THREE.BufferGeometry[]) {
  const positions: number[] = [], normals: number[] = [], uvs: number[] = [];
  for (const g of parts) {
    positions.push(...g.getAttribute("position").array); normals.push(...g.getAttribute("normal").array); uvs.push(...g.getAttribute("uv").array);
    g.dispose();
  }
  const merged = new THREE.BufferGeometry();
  merged.setAttribute("position", new THREE.Float32BufferAttribute(positions, 3));
  merged.setAttribute("normal", new THREE.Float32BufferAttribute(normals, 3));
  merged.setAttribute("uv", new THREE.Float32BufferAttribute(uvs, 2));
  merged.computeBoundingSphere();
  return merged;
}
/** The rolled drum housing over a shutter. */
function drum(out: THREE.BufferGeometry[], centre: THREE.Vector3, normal: THREE.Vector3, width: number, size: number) {
  const g = new THREE.BoxGeometry(width, size, size);
  g.applyQuaternion(new THREE.Quaternion().setFromUnitVectors(new THREE.Vector3(0, 0, 1), normal.clone().normalize()));
  const at = centre.clone().addScaledVector(normal, size / 2);
  g.translate(at.x, at.y, at.z);
  out.push(g);
}
/** A lit prop box (props atlas) oriented with its +z face along `normal`, with vertex tone. */
function propBox(out: THREE.BufferGeometry[], faces: Region[], size: V, at: THREE.Vector3, normal: THREE.Vector3, tone: number) {
  const g = atlasBox(size[0], size[1], size[2], faces);
  g.applyQuaternion(new THREE.Quaternion().setFromUnitVectors(new THREE.Vector3(0, 0, 1), normal.clone().normalize()));
  g.translate(at.x, at.y, at.z);
  g.setAttribute("color", new THREE.Float32BufferAttribute(new Array(g.getAttribute("position").count * 3).fill(tone), 3));
  out.push(g);
}

export function mountZoneDressing(sink: DressingSink, state: ZoneState): ZoneHooks {
  const { plaza, fidelity, lamps, atlas } = sink;
  const zones = atlas.decals.zones, decals = atlas.decals;
  const hidden: THREE.Object3D[] = [];
  plaza.traverse(object => {
    const mesh = object as THREE.Mesh;
    if (!mesh.isMesh) return;
    // The baked EVENTS heading goes too (the shutter's white throw-up replaces it); merged builds keep only its material name.
    const material = Array.isArray(mesh.material) ? null : mesh.material;
    if (isReplacedByZones(object) || (material && /EVENTS destination heading/.test(material.name))) hidden.push(object);
  });
  // Hidden, not removed: the accommodation graffiti stays a click target (three's ray casts ignore visibility).
  hidden.forEach(object => { object.visible = false; });

  // ---------------------------------------------------------------- 1. entrance (lane side of the compound wall)
  {
    const wall = -14.19 + 0.012, n = new THREE.Vector3(0, 0, 1);
    const at = (x: number, y: number) => new THREE.Vector3(x, y, wall);
    sink.laneDecals.push(
      tint(quad(at(-2.75, 8.78), n, 2.5, 2.5 / 4.76, decals.gullyVerse, 1), RUST_INK, 0.55),
      tint(quad(at(-2.9, 8.08), n, 1.5, 1.5 / 4.6, decals.breeze, 1), CHALK, 0.6),
      tint(quad(at(3.0, 9.38), n, 1.2, 1.2 / 4.6, decals.breeze, 1), CHALK, 0.5),
      tint(quad(at(-2.15, 7.58), n, 0.6, 0.3, zones.arrow, 1), CHALK, 0.38),
    );
    // Right wall: a wheat-pasted cluster, overlapping (each a little further out), varied sizes; left: three by the jamb.
    const flyers: [number, number, number, number][] = [[1.72, 8.5, 0.04, 0.5], [2.18, 8.82, -0.05, 0.42], [2.55, 8.35, 0.03, 0.56],
      [3.0, 8.75, -0.02, 0.46], [3.45, 8.4, 0.06, 0.52], [3.78, 8.86, -0.04, 0.4], [2.85, 8.05, 0.02, 0.38]];
    flyers.forEach(([x, y, roll, w], i) => sink.laneDecals.push(quad(at(x, y).setZ(wall + i * 0.0015), n, w, w * 1.08,
      decals.flyers[(i * 5 + 2) % decals.flyers.length], 0.48 + 0.06 * ((i * 7) % 3), roll)));
    sink.laneDecals.push(tint(quad(at(2.3, 7.62), n, 0.56, 0.28, mirror(zones.arrow), 1), CHALK, 0.36), tint(quad(at(3.35, 7.58), n, 0.5, 0.25, mirror(zones.arrow), 1), CHALK, 0.32));
    // The crooked sodium streetlamp: a leaning pole against the left connector house, in front of the navigation board
    // (anything behind the board, which stands 3 m in front of the gate, is hidden from the approach).
    const base = vec([-3.82, 7.0, -9.35]), knee = vec([-3.88, 11.4, -9.38]), top = vec([-3.7, 12.15, -9.45]);
    const elbow = vec([-3.2, 12.0, -9.7]);
    sink.steel.push(strut(base, knee, 0.055), strut(knee, top, 0.045), strut(top, elbow, 0.04),
      strut(knee.clone().add(new THREE.Vector3(0, 0.25, 0)), elbow, 0.02)); // the arm and its brace, bent out over the lane
    lamps.push({ kind: "sodium", housing: [-3.2, 11.98, -9.7], facing: [0.82, 0, -0.57], pool: [-3.0, 11.6, -10.0], radius: 9,
      colour: SODIUM, intensity: 1.3, label: "entrance streetlamp", active: eye => eye.z > -15, glow: [0.8, 0.8],
      // A tight cone down and across the lane onto the gate (penumbra 0.65), not an even sphere of light.
      cone: { direction: new THREE.Vector3(0.45, -0.82, -0.35).normalize(), angle: 0.62, penumbra: 0.65 } });
    // Cool screen spill falling out through the doorway onto the lane.
    lamps.push({ kind: "practical", housing: [0, 8.8, -16.5], facing: [0, 0, 1], pool: [0, 8.8, -16.5], radius: 6.5,
      colour: new THREE.Color("#9aa4b0"), intensity: 0.32, label: "gate screen spill", glow: [0.001, 0.001], active: eye => eye.z > -15 });
  }

  // ---------------------------------------------------------------- 2. events wall (plane x −15.85, facing +x)
  // The events house's shell carries a slim post at x −14.84, z −31.19 that stands straight in front of the shutter
  // from the events view; the balcony above it hangs from the wall, so the post is cut out.
  plaza.updateMatrixWorld(true);
  // Its concrete capital and plinth (x −15.1 … −15.3) are separate materials.
  trimTriangles(plaza, /Existing Events house shell|mineral concrete|building base \/ mineral/,
    new THREE.Box3(new THREE.Vector3(-15.42, 6.4, -31.8), new THREE.Vector3(-14.55, 10.62, -30.7)));
  // Its mirror twin stands at the contact booth's left end (x 15.10, z −20.4) with two concrete brackets above.
  trimTriangles(plaza, /Existing Events house shell|mineral concrete|building base \/ mineral/,
    new THREE.Box3(new THREE.Vector3(14.8, 6.4, -20.68), new THREE.Vector3(15.95, 10.45, -20.0)));
  const count = state.events.length;
  let posters: THREE.Mesh | null = null;
  const posterDisposables: { dispose(): void }[] = [];
  const abort = { aborted: false };
  {
    const n = new THREE.Vector3(1, 0, 0), x = -15.85;
    const wall = (z: number, y: number, off = 0.012) => new THREE.Vector3(x + off, y, z);
    // Rolled-down shutter over the centre window (z −32.05 … −30.15); cracked open 0.35 m for 7+ events.
    // Cracked open 0.35 m for 7+ events; otherwise it stops 12 cm short of the floor and warm light shows underneath.
    const crack = count >= 7 ? 0.35 : 0, gap = crack || 0.12, bottom = 7.245 + gap, topY = 9.45;
    // 2.2 m wide (z −29.88 … −32.08): it also covers the green leaf of the old shutter beside the window.
    shutter(sink.steel, wall(-30.98, (bottom + topY) / 2, 0.24), n, 2.2, topY - bottom);
    drum(sink.steel, wall(-30.98, 9.58, 0.0), n, 2.35, 0.4);
    const near = (eye: THREE.Vector3) => eye.x < -4 && eye.z < -22 && eye.z > -40;
    lamps.push({ kind: "practical", housing: [-14.75, 10.02, -31.1], facing: [1, 0, 0], pool: [-14.55, 9.95, -31.1], radius: 6.5,
      colour: TUBE, intensity: 0.75, label: "events tube", glow: [1.55, 0.42], active: near,
      // Down and back onto the wall it hangs from (the posters and the shutter).
      cone: { direction: new THREE.Vector3(-0.25, -0.97, 0).normalize(), angle: 1.25, penumbra: 0.55 } });
    if (!crack) { // a thin warm sliver under the closed shutter (any closed state: 0-6 events)
      // A sharp amber line along the whole gap (the tube lens strip is even along its length; 2.5x, over-bright before tone
      // mapping) and a low cone grazing out across the wet floor.
      sink.glow.push(tint(quad(wall(-30.98, 7.225, 0.27), n, 2.12, 0.035, atlas.emissive.tubeLens, 1), new THREE.Color("#ff9d3b"), 2.5));
      lamps.push({ kind: "practical", housing: [-15.58, 7.26, -30.98], facing: [1, 0, 0], pool: [-15.55, 7.3, -30.98], radius: 2.4,
        colour: new THREE.Color("#ff9d3b"), intensity: 1.35, label: "events sliver", glow: [2.0, 0.1], active: near,
        cone: { direction: new THREE.Vector3(0.7, -0.7, 0).normalize(), angle: 0.75, penumbra: 0.65 } });
    }
    // The lit interior seen through the gap under the shutter.
    // Just behind the shutter (0.24 m proud): the window frame stands 0.16 m out, so anything deeper hides behind its sill.
    sink.glow.push(quad(wall(-30.98, 7.245 + gap / 2, 0.2), n, 2.1, gap, atlas.emissive.windows[0], crack ? 0.7 : 1.1));
    if (crack) {
      lamps.push({ kind: "practical", housing: [-15.7, 7.42, -31.1], facing: [1, 0, 0], pool: [-15.4, 7.5, -31.1], radius: 3.5,
        colour: TUNGSTEN, intensity: 0.9, label: "events interior", glow: [1.9, 0.3], active: near });
    }
    // Weathered crates by the two doorways.
    const crate: Region[] = Array(6).fill(atlas.props.crate);
    for (const [z, k] of [[-27.35, 0], [-34.85, 1]] as const) {
      propBox(sink.props, crate, [0.55, 0.3, 0.38], new THREE.Vector3(-15.5, FLOOR + 0.15, z), new THREE.Vector3(1, 0, 0.12 * (k ? -1 : 1)), 0.8);
      propBox(sink.props, crate, [0.55, 0.3, 0.38], new THREE.Vector3(-15.48, FLOOR + 0.45, z + (k ? 0.05 : -0.05)), new THREE.Vector3(1, 0, -0.2), 0.8);
      if (!k) propBox(sink.props, crate, [0.55, 0.3, 0.38], new THREE.Vector3(-15.45, FLOOR + 0.15, z - 0.6), new THREE.Vector3(1, 0, 0.3), 0.75);
      sink.blobs.push(blobQuad(-15.45, z - (k ? 0 : 0.3), 0.6));
    }

    // Posters (user request, 28 Nov; reference 06-events-wall): two crowded wheat-paste clusters either side of the
    // shutter, posters overlapping and off the grid. The live events sit on top; older gig posters crowd in under them
    // (repeats included, as pasting crews do). One atlas: 4 × 4 poster cells (0.743:1), then a strip with the shutter's
    // white EVENTS throw-up; the strip's clear bottom-left corner is the shutter's click proxy (7+ events).
    const shown = count === 1 ? state.events.slice(0, 1) : state.events.slice(0, 6);
    const big = fidelity.budget.textureSize >= 1024, cw = big ? 380 : 190, ch = big ? 512 : 256;
    const W = cw * 4, H = ch * 5;
    const canvas = document.createElement("canvas"); canvas.width = W; canvas.height = H;
    const ink = canvas.getContext("2d");
    const texture = new THREE.CanvasTexture(canvas);
    texture.colorSpace = THREE.SRGBColorSpace; texture.anisotropy = 4;
    const rect = (px: number, py: number, pw: number, ph: number): Region => [px / W, 1 - (py + ph) / H, (px + pw) / W, 1 - py / H];
    const cell = (i: number) => rect((i % 4) * cw, Math.floor(i / 4) * ch, cw, ch);
    const paint = (i: number, source: HTMLCanvasElement | HTMLImageElement, old: boolean) => {
      if (!ink) return;
      const cx = (i % 4) * cw, cy = Math.floor(i / 4) * ch;
      ink.clearRect(cx, cy, cw, ch);
      ink.drawImage(weatherPoster(source, cw, ch, 101 + i * 37), cx, cy);
      if (old) { // sun-yellowed and grimier than the live ones
        ink.save(); ink.globalCompositeOperation = "source-atop";
        ink.fillStyle = "rgba(92,66,30,0.26)"; ink.fillRect(cx, cy, cw, ch);
        ink.restore();
      }
      texture.needsUpdate = true;
    };
    void loadPosterImage(eventsLettering, abort).then(art => {
      if (art && ink && !abort.aborted) { sprayEvents(ink, 0, ch * 4, W, ch, art); texture.needsUpdate = true; }
    });
    // Cluster slots [dz, dy, width, roll] around each cluster's centre, bottom layer first: two half-covered scraps,
    // then a loose 3 × 3 (neighbours overlap 5–15 cm). Heights are width × 1.346 (the cell's aspect).
    const slots: [number, number, number, number][] = [[0.62, 0.36, 0.3, 0.12], [-0.64, -0.28, 0.3, -0.1], [0.1, 0.86, 0.32, -0.06],
      [-0.44, 0.5, 0.54, -0.07], [0.0, 0.6, 0.5, 0.04], [0.42, 0.48, 0.56, 0.08],
      [-0.4, -0.04, 0.56, 0.05], [0.03, 0.02, 0.6, -0.03], [0.45, -0.08, 0.5, -0.08],
      [-0.45, -0.56, 0.52, -0.04], [-0.02, -0.5, 0.56, 0.07], [0.4, -0.6, 0.5, 0.03]];
    const layers = [0, 1, 2, 8, 3, 11, 5, 9, 6, 4, 10, 7]; // paste order (later = on top); the event slots go last
    const eventSlots = [7, 4, 10]; // centre, top middle, bottom middle; alternating left and right clusters
    const clusters: [number, number, number][] = [[-28.86, 8.5, 1], [-33.1, 8.5, -1]];
    const parts: THREE.BufferGeometry[] = [], targets: PosterTarget[] = [];
    const placed = new Map<string, number>(); // "cluster:slot" → event index
    shown.forEach((_, i) => placed.set(`${i % 2}:${eventSlots[Math.floor(i / 2)]}`, i));
    let filler = shown.length;
    clusters.forEach(([zc, yc, s], c) => {
      const order = [...layers.filter(k => !placed.has(`${c}:${k}`)), ...layers.filter(k => placed.has(`${c}:${k}`))];
      order.forEach((k, layer) => {
        const [dz, dy, w0, roll0] = slots[k];
        const ev = placed.get(`${c}:${k}`);
        const hero = ev !== undefined && count === 1;
        const w = hero ? 0.8 : w0, roll = roll0 * s + (c ? 0.01 : 0);
        const at = wall(zc - dz * s, yc + dy * (c ? 0.97 : 1), 0.014 + layer * 0.0025);
        let index: number;
        if (ev !== undefined) { index = ev; targets.push(shown[ev].id); }
        else { index = shown.length + ((filler++ - shown.length) % (16 - shown.length)); targets.push(null); }
        parts.push(quad(at, n, w, w * 1.346, cell(index), 1, roll));
      });
    });
    // The live posters: a type-only card first, then the event's image (or a placeholder photo) under the same title.
    shown.forEach((event, i) => {
      const date = event.event_date ? new Date(event.event_date).toLocaleDateString("en-IN", { day: "numeric", month: "short" }) : "Date TBA";
      const line = `${date} · ${event.event_venue ?? "BREEZE 2027"} · BREEZE '27`;
      paint(i, posterCard(null, event.event_name, line), false);
      const own = event.image_url && /^(?:https:\/\/|\/(?![/\\]))/i.test(event.image_url) ? event.image_url : null;
      void loadPosterImage(own ?? placeholderPosters[(i * 5 + 2) % placeholderPosters.length], abort).then(async photo => {
        const picture = photo ?? (own ? await loadPosterImage(placeholderPosters[(i * 5 + 2) % placeholderPosters.length], abort) : null);
        if (!abort.aborted && picture) paint(i, posterCard(picture, event.event_name, line, i % 2 ? "#c4883e" : "#6e4127"), false);
      });
    });
    // The older posters under them: past BREEZE gigs on the placeholder photos.
    for (let i = shown.length; i < 16; i++) {
      const title = pastGigs[(i * 3) % pastGigs.length], line = `PAST · BREEZE '26 · ${["CYPHER PLAZA", "GULLY STAGE", "BLOCK B"][i % 3]}`;
      paint(i, posterCard(null, title, line, i % 3 ? "#6e4127" : "#c4883e"), true);
      void loadPosterImage(placeholderPosters[(i * 7 + 3) % placeholderPosters.length], abort).then(photo => {
        if (!abort.aborted && photo) paint(i, posterCard(photo, title, line, i % 3 ? "#6e4127" : "#c4883e"), true);
      });
    }
    // The white EVENTS throw-up on the shutter, following its corrugation (rows of the shutter's ridge step).
    {
      const shutterH = topY - bottom, ridges = Math.max(2, Math.round(shutterH / 0.075)), step = shutterH / (ridges * 2);
      const k0 = Math.round((8.05 - bottom) / step), rows = Math.max(2, Math.round(0.9 / step));
      const gw = 2.1, gh = rows * step, yMid = bottom + (k0 + rows / 2) * step;
      const g = new THREE.PlaneGeometry(gw, gh, 1, rows);
      const pos = g.getAttribute("position") as THREE.BufferAttribute;
      for (let i = 0; i < pos.count; i++) {
        const row = Math.round((pos.getY(i) + gh / 2) / step);
        pos.setZ(i, ((k0 + row) % 2 ? 0.034 : 0) + 0.004);
      }
      g.computeVertexNormals();
      toRegion(g, rect(0, ch * 4, W, ch));
      g.applyQuaternion(new THREE.Quaternion().setFromUnitVectors(new THREE.Vector3(0, 0, 1), n));
      const centre = wall(-30.98, yMid, 0.24);
      g.translate(centre.x, centre.y, centre.z);
      parts.push(g.toNonIndexed()); g.dispose();
      targets.push(null);
    }
    if (crack) { parts.push(quad(wall(-30.98, 8.3, 0.3), n, 2.2, 2.2, rect(4, H - 12, 8, 8), 1)); targets.push("list"); }
    const merged = new THREE.BufferGeometry();
    const positions: number[] = [], normals: number[] = [], uvs: number[] = [];
    const faceTargets: PosterTarget[] = []; // per two triangles (the click handler's faceIndex / 2)
    parts.forEach((g, i) => { for (let t = 0; t < g.getAttribute("position").count / 6; t++) faceTargets.push(targets[i]); });
    for (const g of parts) {
      positions.push(...g.getAttribute("position").array); normals.push(...g.getAttribute("normal").array); uvs.push(...g.getAttribute("uv").array);
      g.dispose();
    }
    merged.setAttribute("position", new THREE.Float32BufferAttribute(positions, 3));
    merged.setAttribute("normal", new THREE.Float32BufferAttribute(normals, 3));
    merged.setAttribute("uv", new THREE.Float32BufferAttribute(uvs, 2));
    merged.computeBoundingSphere();
    const material = new THREE.MeshStandardMaterial({ map: texture, roughness: 0.92, metalness: 0, alphaTest: 0.5, envMapIntensity: 0.6 });
    material.onBeforeCompile = shader => fidelity.patchProp(shader, null, 0.04);
    material.customProgramCacheKey = () => fidelity.propKey(null, 0.04) + "-map-posters";
    posters = new THREE.Mesh(merged, material);
    posters.name = "Event posters";
    posters.userData.posterTargets = faceTargets;
    posterDisposables.push(merged, material, texture);
  }

  // ---------------------------------------------------------------- 3. mural: one dim caged work lamp above it
  // A near-neutral warm white (not sodium orange), so it lights the mural without tinting its colours.
  lamps.push({ kind: "sodium", housing: [15.1, 11.3, -31.45], facing: [-1, 0, 0], pool: [14.6, 11.0, -31.45], radius: 6,
    colour: new THREE.Color("#ffe6c8"), intensity: 1.3, label: "mural work lamp", active: eye => eye.x > 4 && eye.z < -24 && eye.z > -40 });

  // Wall signs and counter art (wall-art.ts): one alpha-tested mesh over both house walls (accommodation boards and
  // curtain, the contact counter's lanyards and stickers). Parts pushed here as quads; built after the contact booth.
  const sheet = signSheet(fidelity.budget.textureSize >= 1024);
  const signParts: THREE.BufferGeometry[] = [];

  // ---------------------------------------------------------------- 4. accommodation (left house wall)
  // User request, 28 Nov (two references): the wall as the "safe house" front (an open doorway with a half-drawn
  // collapsible gate, stairs going up under a bare bulb, a barred window glowing through a curtain, cables from the tube
  // lamp), without the board over the door; on the wall between door and window, three stacked enamel boards:
  // ACCOMMODATION / HOSTEL & STAY PASSES / CHECK-IN DESK →.
  {
    const { centre, facing } = accommodationGeometry;
    const f = vec([facing[0], facing[1], facing[2]]).normalize(), r = new THREE.Vector3(f.z, 0, -f.x); // viewer's right
    const at = (s: number, y: number, d: number) => vec([centre[0], y, centre[2]]).addScaledVector(r, s).addScaledVector(f, d);
    const near = (eye: THREE.Vector3) => eye.x < -6 && eye.z > -24 && eye.z < -12;
    const win = 2.225; // the right window: r +1.6 … +2.85, y 8.0 … 9.4, 0.30 m deep
    // The baked shaded wall lamp over the boards gets a soft cool pool.
    const lamp = at(0, 10.0, 0.3);
    lamps.push({ kind: "practical", housing: lamp.toArray() as V, facing: [f.x, 0, f.z], pool: lamp.toArray() as V, radius: 3.4,
      colour: TUBE, intensity: 0.85, label: "stay wall lamp", glow: [1.45, 0.38], active: near,
      cone: { direction: f.clone().multiplyScalar(0.1).add(new THREE.Vector3(0, -1, 0)).normalize(), angle: 1.15, penumbra: 0.65 } });
    // The three boards: riveted enamel plates standing 3 cm off the wall (a steel backing plate gives the edge and shadow).
    const boards: [number, number, number, number, number][] = [[0.02, 9.3, 1.56, 0.39, 0.012], [0.0, 8.8, 1.74, 0.435, -0.008], [0.05, 8.32, 1.38, 0.345, 0.014]];
    boards.forEach(([s, y, w, h, roll], i) => {
      signParts.push(quad(at(s, y, 0.052), f, w, h, sheet.boards[i], 1, roll));
      plate(sink.steel, at(s, y, 0.026), f, w - 0.06, h - 0.06, 0.022); // standoff, inset so the board's slight roll hides it
    });
    // Cables: two sagging runs from the lamp (over the door, toward the window awning) and a drop down beside the door.
    const sag = (a: THREE.Vector3, b: THREE.Vector3, dip: number, segments = 8) => {
      for (let k = 0; k < segments; k++) {
        const t0 = k / segments, t1 = (k + 1) / segments;
        const pt = (t: number) => a.clone().lerp(b, t).add(new THREE.Vector3(0, -dip * 4 * t * (1 - t), 0));
        sink.steel.push(strut(pt(t0), pt(t1), 0.007));
      }
    };
    sag(at(-0.35, 10.08, 0.04), at(-2.9, 9.95, 0.04), 0.28);
    sag(at(-0.3, 10.06, 0.05), at(-2.6, 9.62, 0.05), 0.2);
    sag(at(0.35, 10.07, 0.04), at(1.5, 9.78, 0.04), 0.16);
    sink.steel.push(strut(at(-2.62, 9.62, 0.05), at(-2.66, 8.2, 0.05), 0.008));
    // The doorway (s −2.42 … −1.38, d −0.32 recess): its timber leaf is hidden (above); behind it a stairwell box with five
    // steps climbing into the house and a bare bulb.
    {
      // The timber-green material is one mesh across the whole scene, so the leaf is cut away in the shader: a box around
      // the leaf only (s −2.6 … −1.1, d −0.45 … −0.22; the contact window's hole stays on the same material).
      const u0 = centre[0] * r.x - centre[2] * -r.z, dd0 = centre[0] * f.x - centre[2] * -f.z;
      const doorHole = [r.x, -r.z, f.x, -f.z, u0 - 2.6, u0 - 1.1, FLOOR + 0.02, 9.39, dd0 - 0.45, dd0 - 0.22];
      plaza.traverse(object => {
        const mesh = object as THREE.Mesh;
        if (!mesh.isMesh) return;
        for (const m of Array.isArray(mesh.material) ? mesh.material : [mesh.material]) {
          if (/muted timber gre/.test(m.name) && !m.userData.breezeHole) { m.userData.breezeHole = [windowHole, doorHole]; m.needsUpdate = true; }
        }
      });
    }
    const d0 = -0.34, d1 = -1.4, sL = -2.45, sR = -1.2, sw = sR - sL, sMid = (sL + sR) / 2, yTop = 9.36;
    steelBox(sink.steel, [sw + 0.06, yTop - FLOOR, 0.03], at(sMid, (yTop + FLOOR) / 2, d1), f);
    for (const s of [sL - 0.02, sR + 0.02]) steelBox(sink.steel, [0.03, yTop - FLOOR, d0 - d1], at(s, (yTop + FLOOR) / 2, (d0 + d1) / 2), f);
    steelBox(sink.steel, [sw + 0.06, 0.03, d0 - d1], at(sMid, yTop, (d0 + d1) / 2), f);
    for (let i = 0; i < 5; i++) {
      const front = -0.48 - i * 0.19, rise = 0.17;
      steelBox(sink.steel, [sw, rise * (i + 1), front - d1], at(sMid, FLOOR + 0.1 + (rise * (i + 1)) / 2, (front + d1) / 2), f);
    }
    const stairBulb = at(sMid + 0.12, yTop - 0.2, -0.72);
    lamps.push({ kind: "bulb", housing: stairBulb.toArray() as V, facing: [f.x, 0, f.z], pool: at(sMid, 8.3, -0.6).toArray() as V,
      radius: 2.8, colour: new THREE.Color("#ffb45c"), intensity: 1.9, cord: yTop - 0.02, label: "stay stair bulb", active: near,
      cone: { direction: f.clone().multiplyScalar(0.35).add(new THREE.Vector3(0, -1, 0)).normalize(), angle: 1.1, penumbra: 0.7 } });
    // The collapsible gate in the reveal: half drawn across from the left when open, fully drawn when closed.
    {
      const gd = -0.12, yb = FLOOR + 0.12, yt = yTop - 0.04, reach = state.stayOpen ? sL + sw * 0.5 : sR - 0.02;
      sink.steel.push(strut(at(sL, yt, gd), at(sR, yt, gd), 0.012), strut(at(sL, yb, gd), at(sR, yb, gd), 0.01));
      const bars = Math.max(3, Math.round((reach - sL) / 0.075));
      for (let b = 0; b <= bars; b++) {
        const s = sL + 0.02 + ((reach - sL - 0.02) * b) / bars;
        sink.steel.push(strut(at(s, yb, gd), at(s, yt, gd), 0.009));
        if (b < bars) {
          const s2 = sL + 0.02 + ((reach - sL - 0.02) * (b + 1)) / bars;
          for (const [ya, yb2] of [[yb + 0.05, (yb + yt) / 2], [(yb + yt) / 2, yt - 0.05]]) {
            sink.steel.push(strut(at(s, ya, gd + 0.01), at(s2, yb2, gd + 0.01), 0.004), strut(at(s2, ya, gd + 0.01), at(s, yb2, gd + 0.01), 0.004));
          }
        }
      }
    }
    if (!state.stayOpen) {
      shutter(sink.steel, at(win, 8.7, 0.03), f, 1.32, 1.46);
      drum(sink.steel, at(win, 9.5, 0.0), f, 1.42, 0.2);
      sink.glow.push(quad(at(win, 7.965, 0.075), f, 1.25, 0.024, atlas.emissive.sodiumLens, 0.7));
      const sliver = at(win, 8.05, 0.3);
      lamps.push({ kind: "practical", housing: sliver.toArray() as V, facing: [f.x, 0, f.z], pool: sliver.toArray() as V, radius: 2.2,
        colour: TUNGSTEN, intensity: 0.4, label: "stay sliver", glow: [1.1, 0.04], active: near });
    } else {
      // The window glows through a sheer curtain behind its baked bars (a room lit by a bulb behind the curtain).
      plate(sink.steel, at(win, 8.7, -0.3), f, 1.3, 1.4, 0.02);
      signParts.push(quad(at(win, 8.7, -0.283), f, 1.22, 1.38, sheet.curtain, 1));
      const room = at(win + 0.25, 9.1, -0.1);
      lamps.push({ kind: "practical", housing: room.toArray() as V, facing: [f.x, 0, f.z], pool: at(win, 8.4, 0.4).toArray() as V,
        radius: 3.2, colour: new THREE.Color("#ffb45c"), intensity: 1.2, label: "stay window", active: near,
        cone: { direction: f.clone().multiplyScalar(0.7).add(new THREE.Vector3(0, -0.6, 0)).normalize(), angle: 1.0, penumbra: 0.75 } });
    }
  }

  // ---------------------------------------------------------------- 5. contact booth: a railway-style enquiry counter
  // (contact-booth.ts). The window is cut open in the shader; behind it a booth box, the clerk (crowd placement), a hanging
  // bulb; in the window a see-through grille with a semicircular speaking cut; over it the bilingual enamel board.
  let board: THREE.Mesh | null = null;
  const boardDisposables: { dispose(): void }[] = [];
  {
    const { point } = contactSpace(contactConfig);
    const p = (u: number, d: number, y: number) => vec(point(u, d, y));
    const out = p(0, 1, 0).sub(p(0, 0, 0)).normalize(), side = p(1, 0, 0).sub(p(0, 0, 0)).normalize();
    const { left, right, bottom, top, mid } = booth;
    const width = right - left, height = top - bottom, near = (eye: THREE.Vector3) => eye.x > 6 && eye.z > -26 && eye.z < -12;
    // Cut the opening: every plaza material discards inside the hole (fidelity.ts). By name it would miss the facade, whose
    // material is merged under a collapsed name in the normal build; the hole is a small box inside the window reveal.
    plaza.traverse(object => {
      const mesh = object as THREE.Mesh;
      if (!mesh.isMesh) return;
      for (const m of Array.isArray(mesh.material) ? mesh.material : [mesh.material]) {
        if (!m.userData.breezeHole) { m.userData.breezeHole = windowHole; m.needsUpdate = true; }
      }
    });
    // A ledge baked into the facade juts 0.4 m out over the left of the window and would hide the board: cut away.
    const ledge = new THREE.Box3();
    for (const u of [-14.9, -12.4]) for (const d of [-21.99, -20.9]) for (const y of [9.38, 9.97]) ledge.expandByPoint(p(u, d, y));
    trimTriangles(plaza, /./, ledge);
    // The concrete brackets of the post removed earlier reach out over the board too (they run deeper into the wall).
    const brackets = new THREE.Box3();
    for (const u of [-14.95, -12.3]) for (const d of [-22.4, -20.8]) for (const y of [9.3, 10.15]) brackets.expandByPoint(p(u, d, y));
    trimTriangles(plaza, /mineral concrete/, brackets);
    // The booth box: back wall, two sides, ceiling, and the counter top inside the window (steel family, painted plate).
    const depth = booth.grille - booth.back, cy = bottom + height / 2, cd = (booth.grille + booth.back) / 2;
    steelBox(sink.steel, [width + 0.1, height + 0.3, 0.03], p(mid, booth.back, cy), out);
    for (const u of [left - 0.02, right + 0.02]) steelBox(sink.steel, [0.03, height + 0.3, depth], p(u, cd, cy), out);
    steelBox(sink.steel, [width + 0.1, 0.03, depth], p(mid, cd, top + 0.04), out);
    steelBox(sink.steel, [width, 0.05, 0.55], p(mid, booth.grille - 0.3, bottom - 0.01), out);
    // Notices on the back wall and a ledger on the counter.
    sink.decals.push(quad(p(mid - 1.2, booth.back + 0.02, cy + 0.1), out, 0.3, 0.4, decals.flyers[2], 0.35, 0.03),
      quad(p(mid + 1.3, booth.back + 0.02, cy + 0.15), out, 0.26, 0.34, decals.flyers[5], 0.3, -0.04),
      quad(p(mid + 0.55, booth.grille - 0.2, bottom + 0.016), new THREE.Vector3(0, 1, 0), 0.42, 0.28, zones.register, 0.3));
    // A bulb over the clerk.
    const bulb = p(mid + 0.5, booth.clerk + 0.1, top - 0.12);
    lamps.push({ kind: "bulb", housing: bulb.toArray() as V, facing: [out.x, 0, out.z], pool: p(mid, booth.clerk + 0.25, cy).toArray() as V,
      radius: 3.2, colour: TUNGSTEN, intensity: 2.0, cord: top + 0.02, label: "contact bulb", active: near,
      cone: { direction: out.clone().multiplyScalar(0.45).add(new THREE.Vector3(0, -1, 0)).normalize(), angle: 1.0, penumbra: 0.65 } });
    // The counter (user request, 28 Nov; the reference desk): on the clerk's counter behind the grille a desk lamp, an
    // open laptop turned to the window, two small speakers; on the outer ledge (top y 8.13, front face d −21.47) a stack of
    // ledgers and loose papers, lanyards with ID cards hanging over its edge, and stickers on its face and the wall below.
    {
      const deskY = bottom + 0.015, up = new THREE.Vector3(0, 1, 0), ledgeY = 8.13, ledgeFront = -21.466;
      const yawed = (a: number) => out.clone().multiplyScalar(Math.cos(a)).addScaledVector(side, Math.sin(a)).normalize();
      // Desk lamp (the clerk's left, our right): base, two-part arm, a conical shade tipped toward the counter.
      const base = p(mid + 1.3, -22.32, deskY + 0.01);
      steelBox(sink.steel, [0.15, 0.02, 0.15], base, out);
      const elbow = p(mid + 1.36, -22.36, deskY + 0.34), head = p(mid + 1.14, -22.22, deskY + 0.43);
      sink.steel.push(strut(base, elbow, 0.009), strut(elbow, head, 0.009));
      const tip = up.clone().addScaledVector(side, 0.45).normalize();
      const shade = new THREE.CylinderGeometry(0.03, 0.08, 0.12, 12, 1, true);
      shade.deleteAttribute("uv");
      shade.applyQuaternion(new THREE.Quaternion().setFromUnitVectors(up, tip));
      shade.translate(head.x, head.y, head.z);
      sink.steel.push(shade);
      const mouth = head.clone().addScaledVector(tip, -0.065);
      sink.glow.push(tint(quad(mouth.clone().addScaledVector(out, 0.02), out, 0.1, 0.028, atlas.emissive.tubeLens, 1, -0.42), new THREE.Color("#ffc27a"), 1.8));
      lamps.push({ kind: "practical", housing: head.toArray() as V, facing: [out.x, 0, out.z], pool: p(mid + 0.95, -22.2, deskY + 0.05).toArray() as V,
        radius: 1.7, colour: new THREE.Color("#ffb45c"), intensity: 1.5, label: "contact desk lamp", glow: [0.5, 0.22], active: near,
        cone: { direction: tip.clone().negate(), angle: 0.85, penumbra: 0.6 } });
      // Laptop (our left of the clerk): base and a lid leaning back 15°, its screen turned out toward the window.
      const lf = yawed(-0.35), lapAt = p(mid - 0.85, -22.18, deskY);
      steelBox(sink.steel, [0.34, 0.018, 0.24], lapAt.clone().add(new THREE.Vector3(0, 0.009, 0)), lf);
      const lidN = lf.clone().multiplyScalar(Math.cos(0.26)).addScaledVector(up, Math.sin(0.26)).normalize();
      const lidAt = lapAt.clone().addScaledVector(lf, -0.12).add(new THREE.Vector3(0, 0.12, 0)).addScaledVector(lf, -0.03);
      steelBox(sink.steel, [0.34, 0.225, 0.012], lidAt, lidN);
      sink.glow.push(tint(quad(lidAt.clone().addScaledVector(lidN, 0.0075), lidN, 0.3, 0.19, atlas.emissive.tubeLens, 1), new THREE.Color("#8fb3cf"), 0.8));
      // Two small speakers either side of the laptop.
      const speaker: Region[] = [atlas.props.speakerSide, atlas.props.speakerSide, atlas.props.speakerSide, atlas.props.speakerSide, atlas.props.speakerFront, atlas.props.speakerSide];
      propBox(sink.props, speaker, [0.11, 0.18, 0.11], p(mid - 1.27, -22.28, deskY + 0.09), yawed(-0.2), 0.7);
      propBox(sink.props, speaker, [0.11, 0.18, 0.11], p(mid - 0.42, -22.3, deskY + 0.09), yawed(0.15), 0.7);
      // Ledgers and loose papers on the outer ledge (our left), the register open on top.
      propBox(sink.props, Array(6).fill(atlas.props.drum), [0.3, 0.07, 0.22], p(mid - 1.6, -21.7, ledgeY + 0.035), yawed(0.12), 0.5);
      propBox(sink.props, Array(6).fill(atlas.props.crate), [0.26, 0.04, 0.2], p(mid - 1.58, -21.7, ledgeY + 0.09), yawed(-0.1), 0.45);
      sink.decals.push(quad(p(mid - 1.58, -21.7, ledgeY + 0.112), up, 0.3, 0.2, zones.register, 0.32, 0.2),
        quad(p(mid - 1.15, -21.66, ledgeY + 0.004), up, 0.2, 0.27, decals.flyers[3], 0.3, -0.3),
        quad(p(mid - 1.0, -21.7, ledgeY + 0.006), up, 0.2, 0.27, decals.flyers[0], 0.28, 0.25));
      // Lanyards draped over the ledge's front edge, cards hanging below it.
      ([[0.28, 0.04], [0.42, -0.05], [0.57, 0.03], [-0.72, -0.04]] as const).forEach(([u, roll], i) =>
        signParts.push(quad(p(mid + u, ledgeFront + 0.004 + i * 0.001, ledgeY - 0.14), out, 0.14, 0.28, sheet.lanyards[i], 1, roll)));
      // Stickers: small ones on the ledge's face, bigger ones on the wall below among the flyers.
      ([[-1.95, 0.07], [-0.95, 0.075], [-0.1, 0.07], [1.05, 0.075], [1.85, 0.07]] as const).forEach(([u, size], i) =>
        signParts.push(quad(p(mid + u, ledgeFront + 0.003, ledgeY - 0.05), out, size, size, sheet.stickers[(i * 3) % 8], 1, (i % 2 ? 1 : -1) * 0.2)));
      ([[-2.05, 7.72, 0.15], [-1.0, 7.92, 0.13], [-0.08, 7.66, 0.16], [0.3, 7.9, 0.12], [1.28, 7.7, 0.15], [1.95, 7.88, 0.13], [2.15, 7.62, 0.12]] as const)
        .forEach(([u, y, size], i) => signParts.push(quad(p(mid + u, frontage.depth + 0.03 + i * 0.001, y), out, size, size, sheet.stickers[(i * 5 + 1) % 8], 1, (i % 3 - 1) * 0.25)));
    }
    // Tall counter stools under the two seated crew (contactSitters): round seat, splayed legs, a footrest ring, a low back.
    for (const sitter of contactSitters()) {
      const [px, , pz] = sitter.position, fwd = new THREE.Vector3(Math.sin(sitter.yaw), 0, Math.cos(sitter.yaw));
      const floorY = contactConfig.floor, seatY = floorY + stoolSeat;
      const c = new THREE.Vector3(px, 0, pz).addScaledVector(fwd, 0.08);
      const seat = new THREE.CylinderGeometry(0.19, 0.17, 0.045, 14);
      seat.deleteAttribute("uv"); seat.translate(c.x, seatY - 0.0225, c.z);
      sink.steel.push(seat);
      const across = new THREE.Vector3(fwd.z, 0, -fwd.x), feet: THREE.Vector3[] = [];
      for (const [a, b] of [[1, 1], [1, -1], [-1, 1], [-1, -1]]) {
        const dir = fwd.clone().multiplyScalar(a).addScaledVector(across, b).normalize();
        const top = c.clone().addScaledVector(dir, 0.12).setY(seatY - 0.04), foot = c.clone().addScaledVector(dir, 0.25).setY(floorY);
        sink.steel.push(strut(top, foot, 0.012));
        feet.push(top.clone().lerp(foot, 0.6));
      }
      for (const [i, j] of [[0, 1], [1, 3], [3, 2], [2, 0]]) sink.steel.push(strut(feet[i], feet[j], 0.009));
      const back = c.clone().addScaledVector(fwd, -0.25);
      for (const s2 of [-0.12, 0.12]) sink.steel.push(strut(back.clone().addScaledVector(across, s2).setY(seatY - 0.01), back.clone().addScaledVector(across, s2).setY(seatY + 0.3), 0.01));
      steelBox(sink.steel, [0.3, 0.13, 0.02], back.clone().setY(seatY + 0.24), fwd);
    }
    // The grille in the window plane (see-through: alpha-tested mesh), square tiles; the middle tile has the speaking cut.
    const tiles = Math.max(1, Math.round(width / height)), tileW = width / tiles;
    for (let k = 0; k < tiles; k++) {
      const centre = p(left + tileW * (k + 0.5), booth.grille, cy);
      sink.decals.push(k === Math.floor(tiles / 2)
        ? notchedQuad(centre, out, tileW, height, zones.grille, 0.55, 0.17)
        : quad(centre, out, tileW, height, zones.grille, 0.55));
    }
    // A steel rim around the speaking cut.
    const cut = p(left + tileW * (Math.floor(tiles / 2) + 0.5), booth.grille + 0.01, bottom);
    for (let k = 0; k < 8; k++) {
      const a0 = (k / 8) * Math.PI, a1 = ((k + 1) / 8) * Math.PI;
      const at = (a: number) => cut.clone().addScaledVector(side, Math.cos(a) * 0.17).add(new THREE.Vector3(0, Math.sin(a) * 0.17, 0));
      sink.steel.push(strut(at(a0), at(a1), 0.012));
    }
    // Torn flyers along the counter base.
    const sill: [number, number, number, number][] = [[-1.75, -0.4, 0.05, 0.4], [-1.38, -0.5, -0.03, 0.34], [-0.45, -0.38, 0.02, 0.44],
      [0.62, -0.47, -0.05, 0.36], [0.95, -0.36, 0.04, 0.3], [1.62, -0.44, -0.02, 0.42]];
    sill.forEach(([k, dy, roll, w], i) => sink.decals.push(quad(p(mid + k, frontage.depth + 0.012 + i * 0.0015, bottom + dy), out, w, w * 1.08,
      decals.flyers[(i * 5 + 1) % decals.flyers.length], 0.12 + 0.03 * (i % 3), roll)));
    // The enamel board over the window (its own mesh: its own texture, and it is the booth's heading for the focused view).
    const texture = enquiryBoard();
    const boardW = width + 0.3, boardH = boardW / 10; // under the balcony slab: 0.48 m
    const geometry = new THREE.PlaneGeometry(boardW, boardH);
    geometry.applyQuaternion(new THREE.Quaternion().setFromUnitVectors(new THREE.Vector3(0, 0, 1), out));
    const centre = p(mid, frontage.depth + 0.05, top + 0.17 + boardH / 2);
    geometry.translate(centre.x, centre.y, centre.z);
    const material = new THREE.MeshStandardMaterial({ map: texture, roughness: 0.72, metalness: 0.15, emissiveMap: texture,
      emissive: new THREE.Color(0xffffff), emissiveIntensity: 0.16 });
    material.onBeforeCompile = shader => fidelity.patchProp(shader, null, 0.05);
    material.customProgramCacheKey = () => fidelity.propKey(null, 0.05) + "-map-board";
    board = new THREE.Mesh(geometry, material);
    board.name = "Contact enquiry board";
    board.userData.contactPart = "contact heading"; // frames the focused contact view (CypherGatePreview.tsx)
    plate(sink.steel, centre.clone().addScaledVector(out, -0.035), out, boardW + 0.08, boardH + 0.08, 0.04);
    boardDisposables.push(geometry, material, texture);
  }



  // Lane-mode culling (entrance budget): from the lane, plaza meshes wholly below the compound wall's coping
  // (y < 9.85) and outside the doorway's sight line (|x| > 2.5) are behind the wall. Hidden only while in the lane.
  const behindWall: THREE.Object3D[] = [];
  const box = new THREE.Box3();
  plaza.updateMatrixWorld(true);
  for (const child of plaza.children) child.traverse(object => {
    if (!(object as THREE.Mesh).isMesh || !object.visible || isReplacedByZones(object)) return;
    box.setFromObject(object);
    if (box.isEmpty() || box.max.y >= 9.85 || box.max.z > -14.0 || (box.max.x > -2.5 && box.min.x < 2.5)) return;
    behindWall.push(object);
  });
  let culled = false;

  if (posters) { plaza.add(posters); behindWall.push(posters); }
  if (board) plaza.add(board);
  // The wall signs and counter art (one alpha-tested mesh; the curtain glows through its emissive map).
  let signs: THREE.Mesh | null = null;
  const signDisposables: { dispose(): void }[] = [sheet.texture, sheet.glow];
  if (signParts.length) {
    const geometry = mapGeometry(signParts);
    const material = new THREE.MeshStandardMaterial({ map: sheet.texture, emissiveMap: sheet.glow, emissive: new THREE.Color(0xffffff),
      emissiveIntensity: 1, roughness: 0.78, metalness: 0.08, alphaTest: 0.5, envMapIntensity: 0.6 });
    material.onBeforeCompile = shader => fidelity.patchProp(shader, null, 0.04);
    material.customProgramCacheKey = () => fidelity.propKey(null, 0.04) + "-map-signs";
    signs = new THREE.Mesh(geometry, material);
    signs.name = "Zone signs";
    plaza.add(signs); behindWall.push(signs);
    signDisposables.push(geometry, material);
  }

  // Wall flyers (gate lane and plaza): the atlas's stick-figure cells are repainted as weathered photo battle posters.
  {
    const sheet = decals.texture.image as HTMLCanvasElement, ink = sheet.getContext("2d");
    decals.flyerCells.forEach(({ rect: [x, y, w, h], title }, i) => {
      void loadPosterImage(placeholderPosters[(i * 7 + 3) % placeholderPosters.length], abort).then(photo => {
        if (abort.aborted || !photo || !ink) return;
        ink.clearRect(x - 2, y - h * 0.05, w + 4, h * 1.05 + 2); // the cell and the old tape strip above it
        ink.drawImage(weatherPoster(posterCard(photo, title, "SAT · 9PM · THE YARD", i % 2 ? "#c4883e" : "#6e4127"), Math.round(w), Math.round(h), 307 + i * 53), x, y);
        decals.texture.needsUpdate = true;
      });
    });
  }
  return {
    update(camera) {
      const lane = camera.position.z > -13.5;
      if (lane === culled) return;
      culled = lane;
      behindWall.forEach(object => { object.visible = !lane; });
    },
    dispose() {
      if (culled) behindWall.forEach(object => { object.visible = true; });
      hidden.forEach(object => { object.visible = true; });
      abort.aborted = true;
      posters?.removeFromParent();
      board?.removeFromParent();
      signs?.removeFromParent();
      signDisposables.forEach(d => d.dispose());
      boardDisposables.forEach(d => d.dispose());
      posterDisposables.forEach(d => d.dispose());
    },
  };
}
