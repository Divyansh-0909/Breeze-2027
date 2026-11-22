import type { Object3D } from "three";
import { lookAtPose } from "../immersive/world";
import { fitWallView } from "./cypher-wall-view";

// The transparent graffiti plane in the locked Rev15Z plaza.
const centre = [-12.015, 9.12, -14.009] as const;
const widthM = 2.3;
const heightM = 1.533333;
const source = "REV15Z / COMING above SOON graffiti";

export const accommodationApproach = lookAtPose([-9, 8.85, -17.1], centre);
export const accommodationFocus = lookAtPose([centre[0], centre[1], -17], centre);

export function accommodationView(width: number, height: number, eye: readonly number[]) {
  return fitWallView(width, height, eye, centre, widthM, heightM);
}

export function isAccommodationArtwork(object: Object3D) {
  return object.userData.runtimeOriginalSource === source;
}
