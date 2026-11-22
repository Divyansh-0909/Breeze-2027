/** Fit a front-facing display above the controls without pitching the camera. */
export function fitWallView(width: number, height: number, position: readonly number[],
  centre: readonly number[], wallWidth: number, wallHeight: number) {
  const metres = Math.hypot(centre[0] - position[0], centre[2] - position[2]);
  const viewingArea = Math.max(height - 112, height * 0.65);
  const frameHeight = Math.max(wallHeight * height / (0.84 * viewingArea), wallWidth * height / (0.90 * width));
  const halfLens = frameHeight / (2 * Math.max(metres, 1));
  return {
    fov: 2 * Math.atan(halfLens) * 180 / Math.PI,
    offsetY: (height - viewingArea) / 2 + (position[1] - centre[1]) * height / frameHeight,
  };
}
