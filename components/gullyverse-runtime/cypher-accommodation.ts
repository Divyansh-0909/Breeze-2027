import { Box3, Mesh, MeshStandardMaterial, ShaderChunk, Vector4, type Object3D } from "three";
import { lookAtPose } from "../immersive/world";
import { fitWallView } from "./cypher-wall-view";

// The graffiti sits on the left house wall facing the plaza, mirroring the Contact window on the right
// house (scripts/gullyverse/scene_overrides.py). Three.js coordinates; the wall faces +x, slightly toward the gate.
const centre = [-16.884, 8.97, -17.546] as const;
const facing = [0.947, 0, 0.3214] as const;
/** Graffiti half extents (2.30 x 1.53 m) and the lamp hood's top edge, for framing checks. */
export const accommodationGeometry = {
  centre, facing, halfWidth: 1.15, halfHeight: 0.7667,
  lampTop: [centre[0] + facing[0] * 0.45, 10.23, centre[2] + facing[2] * 0.45] as const,
};
const source = "REV15Z / COMING above SOON graffiti";
const plasterOverlay = "REV15Z / Normal house plaster finish";
const housePlaster = "Runtime / REV15Z / REV15N / Existing Events house shell / m.012";

// Walk-up spawn and level focused view at about the Contact window's distances (4.6 and 5.3 m). The
// floor in front of the wall starts just inside the plaza, so both sit a little toward the plaza
// rather than straight out (which would be in the gate approach); the view is about 11 degrees oblique.
export const accommodationApproach = lookAtPose([-12.8, 8.85, -16.85], centre);
export const accommodationFocus = lookAtPose([-11.6, 8.95, -16.9], [centre[0], 8.95, centre[2]]);

export function accommodationView(width: number, height: number, eye: readonly number[]) {
  return fitWallView(width, height, eye, centre, 3.65, 2.95);
}

export function isAccommodationArtwork(object: Object3D) {
  return object.userData.runtimeOriginalSource === source;
}

export function revealAccommodationHouseWall(plaza: Object3D, rgbmRange?: number) {
  const overlays: Object3D[] = [];
  plaza.traverse(object => { if (object.userData.runtimeOriginalSource === plasterOverlay) overlays.push(object); });
  const [plaster] = overlays;
  if (!plaster) return;
  plaster.visible = false;
  if (!(plaster instanceof Mesh) || !(plaster.material instanceof MeshStandardMaterial) || !plaster.material.lightMap) return;

  // Transfer the authored lamp bake onto the house plaster. The hidden plane
  // cast a shadow on the house during baking, so hiding the geometry alone leaves a dark patch.
  const channel = plaster.material.lightMap.channel;
  const lightUv = plaster.geometry.getAttribute(channel ? `uv${channel}` : "uv");
  if (!lightUv) return;
  const u = Array.from({ length: lightUv.count }, (_, i) => lightUv.getX(i));
  const v = Array.from({ length: lightUv.count }, (_, i) => lightUv.getY(i));
  const atlas = new Vector4(Math.min(...u), Math.min(...v), Math.max(...u), Math.max(...v));
  const { min, max } = new Box3().setFromObject(plaster, true);
  const wall = new Vector4(min.x, min.y, max.x - min.x, max.y - min.y);
  const decode = rgbmRange === undefined ? "lampTexel.rgb" : `lampTexel.rgb * lampTexel.a * ${rgbmRange.toFixed(1)}`;
  const patched = new Set<MeshStandardMaterial>();
  plaza.traverse(object => {
    if (!(object instanceof Mesh) || !(object.material instanceof MeshStandardMaterial)) return;
    const material = object.material;
    if (material.name !== housePlaster || patched.has(material)) return;
    patched.add(material);
    const compile = material.onBeforeCompile;
    const cacheKey = material.customProgramCacheKey();
    material.onBeforeCompile = (shader, renderer) => {
      compile.call(material, shader, renderer);
      shader.uniforms.accommodationWall = { value: wall };
      shader.uniforms.accommodationLampAtlas = { value: atlas };
      shader.uniforms.accommodationWallZ = { value: min.z };
      shader.vertexShader = "varying vec3 vAccommodationPosition;\n" + shader.vertexShader.replace(
        "#include <project_vertex>",
        "#include <project_vertex>\nvAccommodationPosition = (modelMatrix * vec4(transformed, 1.0)).xyz;",
      );
      shader.fragmentShader = `varying vec3 vAccommodationPosition;
        uniform vec4 accommodationWall;
        uniform vec4 accommodationLampAtlas;
        uniform float accommodationWallZ;
      ` + shader.fragmentShader.replace("#include <lights_fragment_maps>", ShaderChunk.lights_fragment_maps).replace(
        "irradiance += lightMapIrradiance;",
        `
        vec2 localWall = (vAccommodationPosition.xy - accommodationWall.xy) / accommodationWall.zw;
        vec2 edge = clamp(localWall, vec2(0.0), vec2(1.0));
        float distanceFromPatch = length((localWall - edge) * accommodationWall.zw);
        if (abs(vAccommodationPosition.z - accommodationWallZ) < 0.025 && distanceFromPatch < 0.36) {
          vec2 lampUv = mix(accommodationLampAtlas.xy, accommodationLampAtlas.zw, edge);
          vec4 lampTexel = texture2D(lightMap, lampUv);
          float blend = 1.0 - smoothstep(0.0, 0.36, distanceFromPatch);
          lightMapIrradiance = mix(lightMapIrradiance, ${decode} * lightMapIntensity, blend);
        }
        irradiance += lightMapIrradiance;
        `,
      );
    };
    material.customProgramCacheKey = () => cacheKey + "-accommodation-wall";
    material.needsUpdate = true;
  });
}
