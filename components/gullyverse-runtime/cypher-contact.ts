import { lookAtPose, world } from "../immersive/world";
import { contactSpace } from "./native-space";
import config from "./contact-space.json";
import frontage from "@/public/models/gullyverse/locked-rev15z-clean-v2/contact.json";

const { point, local } = contactSpace(config);
const [left, right] = frontage.messageBoundsU;
const [bottom, top] = frontage.messageBoundsZ;
const depth = frontage.messageDepth;
const centreU = (left + right) / 2;
const centreY = (bottom + top) / 2;
const focusDistance = 5.7;
const target = point(centreU, depth, centreY);
const artTop = frontage.headingCentreZ + 0.35;
const frameCentreY = (artTop + bottom) / 2;
const frameHeight = (aspect: number) => Math.max((artTop - bottom) / 0.68, (right - left) / (0.84 * aspect));
const fovFor = (height: number, distance: number) => 2 * Math.atan(height / (2 * distance)) * 180 / Math.PI;

export const cypherContact = {
  sourceSHA256: config.sourceSHA256,
  spawn: lookAtPose(point(centreU, depth + 4.85, config.floor + world.eyeHeight), target),
  focus: lookAtPose(point(centreU, depth + focusDistance, frameCentreY), point(centreU, depth, frameCentreY)),
  topLeft: point(left, depth, top),
  bottomRight: point(right, depth, bottom),
  headingCentre: point(frontage.headingCentreU, frontage.depth, frontage.headingCentreZ),
  near(pose: { x: number; z: number }) {
    const visitor = local(pose);
    const distance = visitor.depth - depth;
    return distance >= 1 && distance <= 5.2 && Math.abs(visitor.u - centreU) <= 2.75;
  },
  windowFov(aspect: number) {
    return fovFor(frameHeight(aspect), focusDistance);
  },
  windowFits(width: number, height: number) {
    return (top - bottom) * height / frameHeight(width / height) >= 145;
  },
  artworkFov(aspect: number, width: number, height: number, distance: number) {
    return fovFor(Math.max(height / 0.46, width / (0.72 * aspect)), distance);
  },
};
