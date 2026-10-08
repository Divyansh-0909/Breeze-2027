import { boundaryClearance, boundaryCrossings, connections, constrain, constrainInterior, crossedHubDestination, navigationDestination, spawnPose, type LocationId, type Pose, type RequestSource, type TravelId } from "./navigation";
import { filmPose, inspectionCamera, landingPose, tunnelCenter, world } from "./world";
import { composeCamera, mapCamera } from "./aerial";

export type Phase = "boot" | "landing" | "entrance" | "local" | "departure" | "covered" | "arrival" | "context-lost" | "recovering" | "error";
export type Snapshot = { phase: Phase; scene: LocationId; destination: LocationId; serial: number; map: boolean; mapStage: "ascent" | "open" | "descent" | null; destinationMenu: boolean; unavailableDestination: TravelId | null; error: string | null; quality: number; movie: boolean; reduced: boolean; inspection: string | null };
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
  inspectionEnabled = false;
  opacity = 1;
  mapProgress = 0;
  /** Existing content routes leave the immersive shell only after coverage. */
  onCoveredRoute: ((href: string) => void) | null = null;
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
  private mapSaved: Pose | null = null;
  private departureMap: { saved: Pose; progress: number; scene: LocationId } | null = null;
  private boundaryArmed = true;
  private targetEntrance = false;
  private externalRoute: string | null = null;
  private onArrival?: (id: LocationId, source: RequestSource) => void;
  private recovery: { phase: Phase; elapsed: number; opacity: number } | null = null;
  private pendingNavigation: { id: TravelId; source: RequestSource } | null = null;

  constructor(initial: LocationId, onArrival?: (id: LocationId, source: RequestSource) => void) {
    this.state = { phase: "boot", scene: initial, destination: initial, serial: 0, map: false, mapStage: null, destinationMenu: false, unavailableDestination: null, error: null, quality: 0, movie: false, reduced: false, inspection: null };
    this.pose = initial === "hub" ? landingPose() : spawnPose(initial, true);
    this.from = { ...this.pose }; this.to = spawnPose(initial);
    this.onArrival = onArrival;
  }
  getSnapshot = () => this.state;
  subscribe = (listener: () => void) => { this.listeners.add(listener); return () => { this.listeners.delete(listener); }; };
  private publish(update: Partial<Snapshot>) { this.state = { ...this.state, ...update }; this.listeners.forEach((fn) => fn()); }
  clearInput() { this.input.forward = this.input.strafe = this.input.lookX = this.input.lookY = 0; this.vx = this.vz = 0; }
  setMap(map: boolean) {
    if (map) {
      if (this.state.phase !== "local" || this.state.movie || this.state.destinationMenu || this.state.inspection) return;
      if (this.state.mapStage === "open" || this.state.mapStage === "ascent") return;
      this.mapSaved ??= { ...this.pose };
      this.clearInput(); this.publish({ map: true, mapStage: "ascent" });
    } else if (this.state.map && this.state.mapStage !== "descent") {
      this.clearInput(); this.publish({ mapStage: "descent" });
    }
  }
  private resetMap() { this.mapProgress = 0; this.mapSaved = null; }
  dismissDestinationMenu() {
    if (!this.state.destinationMenu) return;
    this.clearInput(); this.boundaryArmed = false; this.publish({ destinationMenu: false });
  }
  dismissUnavailableDestination() { if (this.state.unavailableDestination) this.publish({ unavailableDestination: null }); }
  handleEscape(): boolean {
    if (this.state.destinationMenu) { this.dismissDestinationMenu(); return true; }
    if (this.state.map) { this.setMap(false); return true; }
    if (this.state.movie) { this.movieActions?.stop(); return true; }
    return false;
  }
  setQuality(quality: number) { if (quality !== this.state.quality) this.publish({ quality }); }
  inspect(id: string | null): boolean {
    if (!this.inspectionEnabled || (id !== null && !inspectionCamera(id))) return false;
    this.clearInput(); this.publish({ inspection: id }); return true;
  }
  cameraPose(aspect = 16/9) {
    const base = this.state.inspection ? inspectionCamera(this.state.inspection)! : { ...this.pose, fov: world.camera.fov };
    const camera = composeCamera(base, aspect, this.state.scene, this.state.inspection, this.state.phase);
    const departing = this.state.phase === "departure" ? this.departureMap : null;
    const saved = departing?.saved ?? this.mapSaved;
    if ((!this.state.map && !departing) || !saved) return camera;
    const progress = departing?.progress ?? this.mapProgress;
    const from = composeCamera({ ...saved, fov: world.camera.fov }, aspect, departing?.scene ?? this.state.scene, null, "local");
    const to = mapCamera(aspect), t = smooth(progress);
    blendPose(camera, from, to, t);
    // Altitude leads the lateral move: rise above the same world before
    // centering it, rather than cutting to an unrelated overview camera.
    camera.y = mix(from.y, to.y, smooth(Math.min(1, progress * 1.32)));
    camera.fov = mix(from.fov, to.fov, t);
    return camera;
  }
  preparationPose(): Pose {
    if (this.state.phase === "recovering" || (this.state.phase === "boot" && this.state.scene === "hub")) return this.pose;
    return this.arrivalPose(false);
  }
  private arrivalPose(approaching: boolean): Pose {
    return this.targetEntrance ? landingPose() : spawnPose(this.state.destination, approaching);
  }
  setMovie(movie: boolean) {
    if (movie === this.state.movie) return;
    if (movie && (this.state.map || this.state.destinationMenu || this.state.phase !== "local")) return;
    this.clearInput(); this.focusFrom = { ...this.pose }; this.focusTime = 0;
    // Return to exactly the visitor's bounded viewing pose when playback exits.
    if (movie) this.from = { ...this.pose };
    this.to = movie ? filmPose() : { ...this.from };
    this.publish({ movie });
  }
  enter() {
    if (this.state.phase !== "landing") return;
    this.targetEntrance = false;
    this.elapsed = 0; this.clearInput(); this.publish({ phase: "entrance" });
  }
  request(id: LocationId, source: RequestSource): boolean {
    return this.requestDestination(id, source);
  }
  requestDestination(id: TravelId, source: RequestSource): boolean {
    if (this.state.phase === "error") return false;
    if (this.recovery) { this.pendingNavigation = { id, source }; return true; }
    const option = navigationDestination(id);
    if (!option.available) {
      this.clearInput(); this.boundaryArmed = false; this.publish({ unavailableDestination: id }); return false;
    }
    const localId: LocationId = id === "aftermovie" ? "aftermovie" : id === "hub" || id === "entrance" ? "hub" : this.state.scene;
    const external = !["hub", "entrance", "aftermovie"].includes(id);
    if (external && (!option.href || !this.onCoveredRoute)) return false;
    if (!external && id === this.state.destination && !this.targetEntrance && !this.externalRoute && !["landing", "entrance"].includes(this.state.phase)) return false;
    if (this.state.movie) this.movieActions?.stop();
    this.targetEntrance = id === "entrance";
    this.externalRoute = external ? option.href : null;
    this.source = source; this.elapsed = 0; this.ready = false;
    this.departureVx = source === "physical" ? this.vx : 0;
    this.departureVz = source === "physical" ? this.vz : 0;
    this.from = { ...this.pose };
    // Nearby travel thresholds retain the current view while it fades. The
    // distant arrival pose changes only after the curtain becomes opaque.
    this.to = { ...this.pose };
    this.clearInput(); this.focusFrom = null;
    this.departureMap = this.state.map && this.mapSaved ? { saved: { ...this.mapSaved }, progress: this.mapProgress, scene: this.state.scene } : null;
    this.resetMap(); this.boundaryArmed = true;
    this.publish({ destination: localId, phase: "departure", serial: this.state.serial + 1, map: false, mapStage: null, movie: false, destinationMenu: false, unavailableDestination: null });
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
      if (pending) this.requestDestination(pending.id, pending.source);
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
    this.resetMap(); this.departureMap = null;
    this.publish({ phase: "context-lost", serial: this.state.serial + 1, map: false, mapStage: null, movie: false });
  }
  restoreContext() {
    if (this.state.phase === "context-lost") this.publish({ phase: "recovering" });
  }
  fail(message: string) { this.opacity = 1; this.clearInput(); this.resetMap(); this.departureMap = null; this.publish({ phase: "error", error: message, map: false, mapStage: null, movie: false, destinationMenu: false }); }
  private beginArrival() {
    this.elapsed = 0; this.from = { ...this.pose }; this.to = this.arrivalPose(false);
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
        const points = [world.landing.position, ...world.tunnel.centerline.map(([x,z]) => [x,world.eyeHeight,z]), world.hub.spawn];
        const u = smooth(Math.min(1, this.elapsed / 7.2)) * (points.length - 1);
        const i = Math.min(points.length - 2, Math.floor(u));
        const t = u - i;
        // Cubic Hermite path: continuous velocity through each authored anchor.
        const p0 = points[Math.max(0, i - 1)], p1 = points[i], p2 = points[i + 1], p3 = points[Math.min(points.length - 1, i + 2)];
        const cubic = (axis: number) => 0.5 * ((2 * p1[axis]) + (-p0[axis] + p2[axis]) * t + (2 * p0[axis] - 5 * p1[axis] + 4 * p2[axis] - p3[axis]) * t * t + (-p0[axis] + 3 * p1[axis] - 3 * p2[axis] + p3[axis]) * t * t * t);
        this.pose.z = cubic(2); this.pose.y = world.eyeHeight;
        // Follow the exact excavated centerline rather than a spline cutting
        // across the bent rock walls. Soft heading follows its local tangent.
        this.pose.x = this.pose.z > world.tunnel.startZ ? mix(points[i][0],points[i+1][0],t) : tunnelCenter(this.pose.z);
        const dx = tunnelCenter(Math.min(world.tunnel.startZ,this.pose.z - 0.5)) - this.pose.x;
        const heading = Math.atan2(-dx,0.5);
        this.pose.yaw += Math.atan2(Math.sin(heading-this.pose.yaw),Math.cos(heading-this.pose.yaw)) * (1-Math.exp(-8*dt));
        const exit = smooth(Math.max(0, (u - points.length + 3) / 2));
        this.pose.pitch = mix(world.landing.pitch, world.hub.pitch, exit);
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
        this.departureMap = null;
        if (!this.externalRoute) Object.assign(this.pose, this.arrivalPose(true));
        this.publish({ phase: "covered", scene: this.state.destination });
        if (this.externalRoute) this.onCoveredRoute?.(this.externalRoute);
      }
    } else if (phase === "covered") {
      if (this.ready && !this.externalRoute) this.beginArrival();
    } else if (phase === "arrival") {
      const duration = this.reduced ? 0.22 : this.source === "physical" ? connections[this.state.scene].arrival : 0.6;
      const u = Math.min(1, this.elapsed / duration);
      if (!this.reduced) blendPose(this.pose, this.from, this.to, smooth(u));
      else Object.assign(this.pose, this.to);
      this.opacity = 1 - smooth(Math.min(1, u * 1.5));
      if (u === 1) { this.opacity = 0; this.elapsed = 0; this.publish({ phase: this.targetEntrance ? "landing" : "local" }); this.onArrival?.(this.state.scene, this.source); }
    } else if (phase === "local") {
      if (this.state.inspection) return;
      if (this.state.map) {
        const direction = this.state.mapStage === "descent" ? -1 : this.state.mapStage === "ascent" ? 1 : 0;
        this.mapProgress = Math.max(0, Math.min(1, this.mapProgress + direction * dt / (this.reduced ? 0.18 : direction > 0 ? 1.4 : 1.1)));
        if (direction > 0 && this.mapProgress === 1) this.publish({ mapStage: "open" });
        if (direction < 0 && this.mapProgress === 0) {
          if (this.mapSaved) Object.assign(this.pose,this.mapSaved);
          this.resetMap(); this.publish({ map: false, mapStage: null });
        }
        return;
      }
      if (this.focusFrom) {
        this.focusTime += dt;
        const u = Math.min(1, this.focusTime / (this.reduced ? 0.01 : 0.9));
        blendPose(this.pose, this.focusFrom, this.to, smooth(u));
        if (u === 1) { Object.assign(this.pose, this.to); this.focusFrom = null; }
        return;
      }
      if (this.state.movie || this.state.destinationMenu) return;
      if (!this.boundaryArmed && boundaryClearance(this.state.scene,this.pose) > 0.65) {
        this.boundaryArmed = true;
        if (this.state.unavailableDestination) this.publish({ unavailableDestination: null });
      }
      const input = this.input;
      this.pose.yaw -= input.lookX; this.pose.pitch = Math.max(-0.5, Math.min(0.55, this.pose.pitch - input.lookY));
      input.lookX = input.lookY = 0;
      const length = Math.max(1, Math.hypot(input.forward, input.strafe));
      const f = input.forward / length, s = input.strafe / length;
      const speed = 4.2, damping = 1 - Math.exp(-16 * dt);
      this.vx += ((s * Math.cos(this.pose.yaw) - f * Math.sin(this.pose.yaw)) * speed - this.vx) * damping;
      this.vz += ((-f * Math.cos(this.pose.yaw) - s * Math.sin(this.pose.yaw)) * speed - this.vz) * damping;
      const before = { x: this.pose.x, z: this.pose.z };
      this.pose.x += this.vx * dt; this.pose.z += this.vz * dt;
      constrainInterior(this.state.scene,this.pose);
      const crossings = boundaryCrossings(this.state.scene,before,this.pose);
      constrain(this.state.scene, this.pose);
      if (!this.boundaryArmed || crossings.length === 0) return;
      if (this.state.scene === "aftermovie") {
        this.boundaryArmed = false; this.clearInput(); this.publish({ destinationMenu: true });
      } else {
        const destination = crossedHubDestination(crossings);
        if (destination) this.requestDestination(destination,"physical");
      }
    }
  }
}
