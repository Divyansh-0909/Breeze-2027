import { DoubleSide, Mesh, MeshBasicMaterial, type Object3D, type VideoTexture } from "three";
import { retainVideoTexture } from "../landing-page/stage3d/videoTextureOwnership";
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

export function bindAftermovie(panels: Mesh[], video: VideoTexture) {
  const original = panels.map(panel => panel.material);
  const release = retainVideoTexture(video);
  // The still already uses the film's authored UV crop on each panel.
  video.flipY = false;
  const screen = new MeshBasicMaterial({ map: video, side: DoubleSide, toneMapped: false });
  panels.forEach(panel => { panel.material = screen; });
  return () => {
    panels.forEach((panel, index) => { panel.material = original[index]; });
    screen.dispose();
    release();
  };
}
