import { connections, constrain, insideThreshold, locations, spawnPose, type LocationId, type Pose, type RequestSource } from "./navigation";

export type Phase = "boot" | "landing" | "entrance" | "local" | "departure" | "covered" | "arrival" | "context-lost" | "recovering" | "error";
export type Snapshot = { phase: Phase; scene: LocationId; destination: LocationId; serial: number; map: boolean; error: string | null; quality: number; movie: boolean; reduced: boolean };
export type Input = { forward: number; strafe: number; lookX: number; lookY: number };
const smooth = (t: number) => t * t * (3 - 2 * t);
const mix = (a: number, b: number, t: number) => a + (b - a) * t;
function blendPose(out: Pose, a: Pose, b: Pose, t: number) {
  out.x = mix(a.x, b.x, t); out.y = mix(a.y, b.y, t); out.z = mix(a.z, b.z, t);
  // shortest-angle interpolation keeps a turned visitor's handoff smooth.
  const angle = Math.atan2(Math.sin(b.yaw - a.yaw), Math.cos(b.yaw - a.yaw));
  out.yaw = a.yaw + angle * t; out.pitch = mix(a.pitch, b.pitch, t);
}

/** Discrete UI state only. Pose, input, velocity, and frame clocks never notify React. */
export class ImmersiveRuntime {
  private state: Snapshot;
  private listeners = new Set<() => void>();
  pose: Pose;
  input: Input = { forward: 0, strafe: 0, lookX: 0, lookY: 0 };
  get reduced() { return this.state.reduced; }
  set reduced(value: boolean) { if (this.state.reduced !== value) this.publish({ reduced: value }); }
  suspended = false;
  opacity = 1;
  /** Shader preparation releases real draws; animation/control clocks remain live while covered. */
  preparedSerial = -1;
  movieActions: { play: () => void; stop: () => void; sound: () => void; status: () => { phase: string; currentTime: number; paused: boolean; muted: boolean } } | null = null;
  private elapsed = 0;
  private source: RequestSource = "url";
  private from: Pose;
  private to: Pose;
  private vx = 0;
  private vz = 0;
  private departureVx = 0;
  private departureVz = 0;
  private ready = false;
  private focusFrom: Pose | null = null;
  private focusTime = 0;
  private onArrival?: (id: LocationId, source: RequestSource) => void;
  private recovery: { phase: Phase; elapsed: number; opacity: number } | null = null;
  private pendingNavigation: { id: LocationId; source: RequestSource } | null = null;

  constructor(initial: LocationId, onArrival?: (id: LocationId, source: RequestSource) => void) {
    this.state = { phase: "boot", scene: initial, destination: initial, serial: 0, map: false, error: null, quality: 0, movie: false, reduced: false };
    this.pose = initial === "hub" ? { x: 0, y: 1.72, z: 8, yaw: 0, pitch: 0 } : spawnPose(initial, true);
    this.from = { ...this.pose }; this.to = spawnPose(initial);
    this.onArrival = onArrival;
  }
  getSnapshot = () => this.state;
  subscribe = (listener: () => void) => { this.listeners.add(listener); return () => { this.listeners.delete(listener); }; };
  private publish(update: Partial<Snapshot>) { this.state = { ...this.state, ...update }; this.listeners.forEach((fn) => fn()); }
  clearInput() { this.input.forward = this.input.strafe = this.input.lookX = this.input.lookY = 0; this.vx = this.vz = 0; }
  setMap(map: boolean) { this.clearInput(); this.publish({ map }); }
  setQuality(quality: number) { if (quality !== this.state.quality) this.publish({ quality }); }
  setMovie(movie: boolean) {
    if (movie === this.state.movie) return;
    this.clearInput(); this.focusFrom = { ...this.pose }; this.focusTime = 0;
    // Return to exactly the visitor's bounded viewing pose when playback exits.
    if (movie) this.from = { ...this.pose };
    this.to = movie ? { x: 0, y: 5.9, z: 17, yaw: 0, pitch: 0 } : { ...this.from };
    this.publish({ movie });
  }
  enter() {
    if (this.state.phase !== "landing") return;
    this.elapsed = 0; this.clearInput(); this.publish({ phase: "entrance" });
  }
  request(id: LocationId, source: RequestSource): boolean {
    if (this.state.phase === "error") return false;
    if (this.recovery) { this.pendingNavigation = { id, source }; return true; }
    if (id === this.state.destination && !["landing", "entrance"].includes(this.state.phase)) return false;
    this.source = source; this.elapsed = 0; this.ready = false;
    this.departureVx = source === "physical" ? this.vx : 0;
    this.departureVz = source === "physical" ? this.vz : 0;
    this.from = { ...this.pose };
    const direction = this.state.scene === "hub" ? -1 : 1;
    this.to = { ...this.pose, z: this.pose.z + direction * 3, yaw: direction === -1 ? 0 : Math.PI, pitch: 0.04 };
    this.clearInput(); this.focusFrom = null;
    this.publish({ destination: id, phase: "departure", serial: this.state.serial + 1, map: false, movie: false });
    return true;
  }
  markReady(serial: number) {
    if (serial !== this.state.serial || this.state.phase === "context-lost" || this.state.phase === "error") return;
    this.ready = true;
    if (this.state.phase === "recovering" && this.recovery) {
      const resume = this.recovery; this.recovery = null;
      this.elapsed = resume.elapsed; this.opacity = resume.opacity;
      this.publish({ phase: resume.phase });
      const pending = this.pendingNavigation; this.pendingNavigation = null;
      if (pending) this.request(pending.id, pending.source);
    }
    if (this.state.phase === "boot") {
      if (this.state.scene === "hub") { this.opacity = 0; this.publish({ phase: "landing" }); }
      else this.beginArrival();
    }
  }
  loseContext() {
    if (this.state.phase === "error" || this.state.phase === "context-lost") return;
    // A second loss during preparation keeps the original interrupted journey.
    this.recovery ??= { phase: this.state.phase, elapsed: this.elapsed, opacity: this.opacity };
    if (this.state.movie) {
      this.movieActions?.stop();
      Object.assign(this.pose, this.from); this.focusFrom = null;
    }
    this.clearInput(); this.ready = false; this.opacity = 1; this.preparedSerial = -1;
    this.publish({ phase: "context-lost", serial: this.state.serial + 1, map: false, movie: false });
  }
  restoreContext() {
    if (this.state.phase === "context-lost") this.publish({ phase: "recovering" });
  }
  fail(message: string) { this.opacity = 1; this.clearInput(); this.publish({ phase: "error", error: message, map: false, movie: false }); }
  private beginArrival() {
    this.elapsed = 0; this.from = { ...this.pose }; this.to = spawnPose(this.state.scene);
    this.publish({ phase: "arrival" });
  }
  tick(delta: number) {
    if (this.suspended || ["error", "context-lost", "recovering"].includes(this.state.phase)) return;
    const dt = Math.min(delta, 0.05); // restoring a background tab cannot teleport the player
    const phase = this.state.phase;
    this.elapsed += dt;
    if (phase === "entrance") {
      if (this.reduced) { this.opacity = 1; Object.assign(this.pose, spawnPose("hub")); }
      else {
        const points = locations.hub.spatial.entrance;
        const u = smooth(Math.min(1, this.elapsed / 7.2)) * (points.length - 1);
        const i = Math.min(points.length - 2, Math.floor(u));
        const t = u - i;
        // Cubic Hermite path: continuous velocity through each authored anchor.
        const p0 = points[Math.max(0, i - 1)], p1 = points[i], p2 = points[i + 1], p3 = points[Math.min(points.length - 1, i + 2)];
        const cubic = (axis: number) => 0.5 * ((2 * p1[axis]) + (-p0[axis] + p2[axis]) * t + (2 * p0[axis] - 5 * p1[axis] + 4 * p2[axis] - p3[axis]) * t * t + (-p0[axis] + 3 * p1[axis] - 3 * p2[axis] + p3[axis]) * t * t * t);
        this.pose.x = cubic(0); this.pose.y = cubic(1); this.pose.z = cubic(2);
        this.pose.pitch = smooth(Math.max(0, (u - 2) / 2)) * 0.04;
      }
      if (this.elapsed >= (this.reduced ? 0.25 : 7.2)) { this.opacity = 0; Object.assign(this.pose, spawnPose("hub")); this.elapsed = 0; this.publish({ phase: "local" }); }
    } else if (phase === "departure") {
      const duration = this.reduced ? 0.18 : this.source === "physical" ? connections[this.state.scene].departure : 0.3;
      const u = Math.min(1, this.elapsed / duration);
      if (!this.reduced) {
        blendPose(this.pose, this.from, this.to, smooth(u));
        // Preserve walking velocity at route commitment. Camera ownership
        // changes without inserting an abrupt stop before guided motion.
        const tangent = u * (1 - u) * (1 - u) * duration;
        this.pose.x += this.departureVx * tangent;
        this.pose.z += this.departureVz * tangent;
      }
      this.opacity = smooth(Math.max(0, (u - 0.35) / 0.65));
      if (u === 1) {
        this.opacity = 1; this.elapsed = 0; this.ready = false;
        Object.assign(this.pose, spawnPose(this.state.destination, true));
        this.publish({ phase: "covered", scene: this.state.destination });
      }
    } else if (phase === "covered") {
      if (this.ready) this.beginArrival();
    } else if (phase === "arrival") {
      const duration = this.reduced ? 0.22 : this.source === "physical" ? connections[this.state.scene].arrival : 0.6;
      const u = Math.min(1, this.elapsed / duration);
      if (!this.reduced) blendPose(this.pose, this.from, this.to, smooth(u));
      else Object.assign(this.pose, this.to);
      this.opacity = 1 - smooth(Math.min(1, u * 1.5));
      if (u === 1) { this.opacity = 0; this.elapsed = 0; this.publish({ phase: "local" }); this.onArrival?.(this.state.scene, this.source); }
    } else if (phase === "local") {
      if (this.focusFrom) {
        this.focusTime += dt;
        const u = Math.min(1, this.focusTime / (this.reduced ? 0.01 : 0.9));
        blendPose(this.pose, this.focusFrom, this.to, smooth(u));
        if (u === 1) { Object.assign(this.pose, this.to); this.focusFrom = null; }
        return;
      }
      if (this.state.map || this.state.movie) return;
      const input = this.input;
      this.pose.yaw -= input.lookX; this.pose.pitch = Math.max(-0.5, Math.min(0.55, this.pose.pitch - input.lookY));
      input.lookX = input.lookY = 0;
      const length = Math.max(1, Math.hypot(input.forward, input.strafe));
      const f = input.forward / length, s = input.strafe / length;
      const speed = 4.2, damping = 1 - Math.exp(-16 * dt);
      this.vx += ((s * Math.cos(this.pose.yaw) - f * Math.sin(this.pose.yaw)) * speed - this.vx) * damping;
      this.vz += ((-f * Math.cos(this.pose.yaw) - s * Math.sin(this.pose.yaw)) * speed - this.vz) * damping;
      this.pose.x += this.vx * dt; this.pose.z += this.vz * dt;
      constrain(this.state.scene, this.pose);
      if (insideThreshold(this.state.scene, this.pose)) this.request(connections[this.state.scene].to, "physical");
    }
  }
}
