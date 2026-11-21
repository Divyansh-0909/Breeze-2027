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

export const cypherContact = {
  sourceSHA256: config.sourceSHA256,
  spawn: lookAtPose(point(centreU, depth + 4.85, config.floor + world.eyeHeight), target),
  focus: lookAtPose(point(centreU, depth + focusDistance, centreY), target),
  topLeft: point(left, depth, top),
  bottomRight: point(right, depth, bottom),
  near(pose: { x: number; z: number }) {
    const visitor = local(pose);
    const distance = visitor.depth - depth;
    return distance >= 1 && distance <= 5.2 && Math.abs(visitor.u - centreU) <= 2.75;
  },
  windowFov(aspect: number) {
    const height = Math.max((top - bottom) / 0.43, (right - left) / (0.84 * aspect));
    return 2 * Math.atan(height / (2 * focusDistance)) * 180 / Math.PI;
  },
};
