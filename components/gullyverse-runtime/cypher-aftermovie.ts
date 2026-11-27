import { DoubleSide, Mesh, MeshBasicMaterial, type Object3D, type VideoTexture } from "three";
import { isRetiredVideoTexture, retainVideoTexture } from "../landing-page/stage3d/videoTextureOwnership";
import { lookAtPose } from "../immersive/world";
import { fitWallView } from "./cypher-wall-view";

const centre = [0, 11.59, -45.72] as const;
const screenWidth = 14.56, screenHeight = 5.98;
const position = [0, 9.85, -35.5] as const;
export const aftermovieFocus = lookAtPose(position, [centre[0], position[1], centre[2]]);
const panelSources = new Set(["left", "center", "right"].map(part => "REV15Z / Existing Aftermovie / " + part));

export function aftermovieView(width: number, height: number, eye: readonly number[]) {
  return fitWallView(width, height, eye, centre, screenWidth, screenHeight);
}

export function isAftermoviePanel(object: Object3D) {
  return object instanceof Mesh && panelSources.has(object.userData.runtimeOriginalSource);
}

export function findAftermoviePanels(scene: Object3D) {
  const panels: Mesh[] = [];
  scene.traverse(object => {
    if (object instanceof Mesh && isAftermoviePanel(object)) panels.push(object);
  });
  return new Set(panels.map(panel => panel.userData.runtimeOriginalSource)).size === panelSources.size &&
    panels.length === panelSources.size ? panels : null;
}

/**
 * The LED wall (docs/runtime/PHASE2-COURTYARD-SCREEN-PLAN.md): tone-mapped with the scene (AgX tames hot primaries
 * instead of the old untoned magenta blow-out), the film at 75% with a soft shoulder so white frames cannot wash
 * the dark courtyard, a slight black lift (LED panels are never pure black), and a 4 cm pixel grid with faint
 * scanlines laid out in world space (the three panels have different UV crops). The grid fades before it could
 * alias (fwidth), so phones and distant views see a clean picture. Fogged like the rest of the plaza.
 */
function ledMaterial(video: VideoTexture) {
  const material = new MeshBasicMaterial({ map: video, side: DoubleSide, toneMapped: true, fog: true });
  material.onBeforeCompile = shader => {
    shader.vertexShader = shader.vertexShader
      .replace("#include <common>", "#include <common>\nvarying vec3 vLedWorld;")
      .replace("#include <project_vertex>", "#include <project_vertex>\nvLedWorld = (modelMatrix * vec4(transformed, 1.0)).xyz;");
    shader.fragmentShader = shader.fragmentShader
      .replace("#include <common>", "#include <common>\nvarying vec3 vLedWorld;")
      .replace("#include <map_fragment>", `#include <map_fragment>
{
  vec3 led = diffuseColor.rgb * 0.75;
  led /= 1.0 + 0.35 * max(led.r, max(led.g, led.b));
  vec2 cell = vec2(vLedWorld.x, vLedWorld.y) / 0.04;
  vec2 fw = fwidth(cell);
  float gridOn = 1.0 - smoothstep(0.22, 0.48, max(fw.x, fw.y));
  vec2 f = abs(fract(cell) - 0.5);
  float pixel = smoothstep(0.5, 0.34, max(f.x, f.y));
  float scan = 0.95 + 0.05 * sin(cell.y * 6.2831853);
  led *= mix(1.0, mix(0.58, 1.0, pixel) * scan, gridOn);
  diffuseColor.rgb = led + 0.004;
}`);
  };
  material.customProgramCacheKey = () => "breeze-led-v1";
  return material;
}

export function bindAftermovie(panels: Mesh[], video: VideoTexture) {
  // The 3D scene commits after the page. A film that ended or failed in that
  // gap is already retired; the panels keep their still instead of crashing.
  if (isRetiredVideoTexture(video)) return () => {};
  const original = panels.map(panel => panel.material);
  const release = retainVideoTexture(video);
  // The still already uses the film's authored UV crop on each panel.
  video.flipY = false;
  const screen = ledMaterial(video);
  panels.forEach(panel => { panel.material = screen; });
  return () => {
    panels.forEach((panel, index) => { panel.material = original[index]; });
    screen.dispose();
    release();
  };
}
