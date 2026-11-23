/**
 * Gully soundscape (Web Audio), built the way open-world games build theirs (see
 * docs/runtime/M2O-SOUND-DESIGN.md and reports/Open world game sound design.md):
 *
 * - no constant noise beds. The night is carried by placed emitters (street-lamp mains buzz, a shop
 *   radio, the stage) and scattered one-shots with random timing, choice, position and cooldowns
 *   (distant horns, a brief two-wheeler passing the lane mouth);
 * - every emitter is heard through distance: HRTF placement, a low-pass that closes with distance
 *   (air absorption), more reverb the further away it is, and culling beyond its reach. The stage is
 *   occluded from the lane by the gate and houses and opens up in the plaza;
 * - two synthetic reverbs, a narrow lane (short flutter echoes off walls about 5 m apart) and the open
 *   plaza (longer tail and facade echoes), cross-faded by where the listener stands;
 * - footsteps triggered by distance walked, heel-to-toe, alternating feet, randomised in pitch
 *   (about 5 %) and level (about 3 dB), with grit on some steps. Sprinting is heavier and quicker
 *   with a clothing swish; puddles splash.
 *
 * The screen and the radio play the looping Aftermovie's own sound; everything else is synthesised.
 * Browsers only allow audio after a user gesture, so the context starts on the first pointer or key
 * press. The on/off choice is remembered.
 */

type Vec3 = readonly [number, number, number];

const storageKey = "breeze:sound";
const masterLevel = 1.4;
// Three.js coordinates. The lane floor is at y = 6 (eye at about 7.6); the plaza starts near z = -14.
// Rev15Z street lamps (L02 and L05 are dead; L03 and L06 flicker).
const lamps: { position: Vec3; flicker: boolean }[] = [
  { position: [-1.17, 11.86, 25], flicker: false }, { position: [-1.17, 11.86, 15.5], flicker: true },
  { position: [1.17, 11.86, 15.5], flicker: false }, { position: [1.17, 12.08, 5.5], flicker: true },
];
const radio: Vec3 = [3.3, 8.6, 16];
const stage: Vec3 = [0, 11, -44.8];
const aftermovieSeat: Vec3 = [0, 9.85, -35.5];
// Puddles and edge pools (x, z, half width x, half depth z), extracted from the master.
const puddles: readonly (readonly [number, number, number, number])[] = [[-3.16, 26.51, 0.43, 3.35], [3.18, 26.07, 0.44, 3.46], [-3.15, 20.06, 0.42, 3.32], [3.15, 19.84, 0.45, 3.23], [-3.17, 13.68, 0.38, 2.98], [3.15, 13.56, 0.39, 2.98], [-12.66, -26.62, 0.51, 1.91], [-12.67, -30.97, 0.5, 2.03], [-12.67, -37.62, 0.46, 1.73], [12.64, -27.15, 0.47, 1.87], [12.65, -32.0, 0.51, 2.05], [12.66, -38.59, 0.47, 2.06], [-10.94, -15.01, 2.14, 0.41], [10.71, -15.02, 2.05, 0.41], [-12.54, -44.46, 0.42, 1.41], [12.51, -44.74, 0.46, 1.38], [-2.5, 25.96, 0.57, 0.74], [2.48, 13.41, 0.56, 0.64], [10.73, -18.4, 0.68, 0.9], [11.92, -27.37, 0.69, 0.9]];

/**
 * Metres per footfall at a given speed: about 1.25 m at the 2.4 m/s walk (1.9 steps a second) and
 * 1.45 m at the 4.2 m/s sprint (2.9 steps a second).
 */
export const strideAt = (speed: number) => 1.25 + 0.2 * Math.min(1, Math.max(0, (speed - 2.4) / 1.8));

export const isWet = (x: number, z: number) =>
  puddles.some(([px, pz, hx, hz]) => Math.abs(x - px) <= hx && Math.abs(z - pz) <= hz);

export function soundPreference() {
  try { return window.localStorage.getItem(storageKey) !== "off"; } catch { return true; }
}

export const previewLayers = {
  "footsteps-walk": "Footsteps, walking",
  "footsteps-sprint": "Footsteps, sprinting (Shift)",
  "footsteps-wet": "Footsteps through a puddle",
  "lane-horns": "Distant horns",
  "two-wheeler": "Two-wheeler passing the lane mouth",
  "lamp-buzz": "Street lamp buzz (L01, L04), standing under it",
  "lamp-flicker": "Flickering lamp crackle (L03, L06), standing under it",
  "shop-radio": "Shop radio playing the Aftermovie's sound, walking past the shop",
  "stage-from-lane": "The screen's Aftermovie heard from the lane (occluded)",
  "stage-in-plaza": "The screen's Aftermovie in the plaza",
  "aftermovie-watching": "Watching the Aftermovie (focused)",
} as const;
export type PreviewLayer = keyof typeof previewLayers;

/** A placed source heard through distance: low-pass, reverb send and culling follow the listener. */
type Emitter = {
  position: Vec3; filter: BiquadFilterNode; level: GainNode; send: GainNode;
  near: number; far: number; reach: number; wet: readonly [number, number]; occluded?: boolean;
};

const rand = (low: number, high: number) => low + Math.random() * (high - low);
const smooth = (edge0: number, edge1: number, x: number) => {
  const t = Math.min(1, Math.max(0, (x - edge0) / (edge1 - edge0))); return t * t * (3 - 2 * t);
};

/**
 * A synthetic stereo room response: decaying noise that darkens as it decays, plus discrete early
 * reflections [seconds, left, right]. Normalised to unit energy per channel.
 */
function impulse(ctx: BaseAudioContext, rt60: number, predelay: number, reflections: readonly (readonly [number, number, number])[]) {
  const rate = ctx.sampleRate, length = Math.round(rate * (predelay + rt60 * 1.1));
  const buffer = ctx.createBuffer(2, length, rate);
  for (let c = 0; c < 2; c++) {
    const data = buffer.getChannelData(c);
    let y = 0;
    for (let i = Math.round(predelay * rate); i < length; i++) {
      const t = i / rate - predelay, x = (Math.random() * 2 - 1) * Math.exp(-6.9 * t / rt60);
      y += (0.85 - 0.7 * Math.min(1, t / rt60)) * (x - y); // high frequencies die first
      data[i] = y;
    }
    let energy = 0;
    for (const v of data) energy += v * v;
    const tail = 0.6 / Math.sqrt(energy || 1);
    for (let i = 0; i < length; i++) data[i] *= tail;
    for (const [time, left, right] of reflections) {
      const at = Math.round(time * rate), gain = c === 0 ? left : right;
      for (let k = 0; k < 48 && at + k < length; k++) data[at + k] += gain * (Math.random() * 2 - 1) * Math.exp(-k / 10);
    }
    energy = 0;
    for (const v of data) energy += v * v;
    const norm = 1 / Math.sqrt(energy || 1);
    for (let i = 0; i < length; i++) data[i] *= norm;
  }
  return buffer;
}

export class GullyAudio {
  private ctx: BaseAudioContext | null = null;
  private master!: GainNode;
  private lane!: GainNode;
  private plaza!: GainNode;
  private duck!: GainNode;
  private reverb!: GainNode;
  private laneWet!: GainNode;
  private plazaWet!: GainNode;
  private noise!: AudioBuffer;
  private emitters: Emitter[] = [];
  private flickers: GainNode[] = [];
  private foot = 1;
  private plazaMix = 0;
  private placed = -1;
  private next = { horn: 0, wheeler: 0 };
  private film: HTMLVideoElement | null = null;
  private filmSource: HTMLVideoElement | null = null;
  private filmDirect!: GainNode;
  private disposed = false;
  private listeners: (() => void)[] = [];
  enabled = soundPreference();

  /** Arms the first-gesture start. Returns a cleanup function. */
  arm() {
    const start = () => { void this.start(); };
    for (const type of ["pointerdown", "keydown", "touchend"] as const) {
      window.addEventListener(type, start, { capture: true });
      this.listeners.push(() => window.removeEventListener(type, start, { capture: true }));
    }
    const visibility = () => {
      if (!this.ctx) return;
      const live = this.ctx as AudioContext;
      if (document.hidden) void live.suspend(); else if (this.enabled) void live.resume();
    };
    document.addEventListener("visibilitychange", visibility);
    this.listeners.push(() => document.removeEventListener("visibilitychange", visibility));
  }

  setEnabled(on: boolean) {
    this.enabled = on;
    try { window.localStorage.setItem(storageKey, on ? "on" : "off"); } catch { /* private mode */ }
    if (!this.ctx) { if (on) void this.start(); return; }
    this.master.gain.setTargetAtTime(on ? masterLevel : 0, this.ctx.currentTime, 0.15);
    if (on) void (this.ctx as AudioContext).resume();
  }

  private async start() {
    if (this.ctx || this.disposed) return;
    const Context = window.AudioContext ?? (window as unknown as { webkitAudioContext?: typeof AudioContext }).webkitAudioContext;
    if (!Context) return;
    const ctx = new Context();
    this.listeners.splice(0).forEach(off => off()); // gestures no longer needed; re-arm visibility below
    const visibility = () => { if (document.hidden) void ctx.suspend(); else if (this.enabled) void ctx.resume(); };
    document.addEventListener("visibilitychange", visibility);
    this.listeners.push(() => document.removeEventListener("visibilitychange", visibility));
    this.graph(ctx);
    lamps.forEach(lamp => this.lampBuzz(lamp.position, lamp.flicker));
    this.connectFilm();
    // The first one-shots wait a while, so arriving is quiet.
    const now = ctx.currentTime;
    this.next = { horn: now + rand(6, 14), wheeler: now + rand(10, 25) };
    if (this.enabled) void ctx.resume();
  }

  /** Master chain, zone buses, the two room reverbs and the shared noise buffer. */
  private graph(ctx: BaseAudioContext) {
    this.ctx = ctx;
    this.master = ctx.createGain(); this.master.gain.value = this.enabled ? masterLevel : 0;
    this.duck = ctx.createGain(); this.duck.connect(this.master);
    const limiter = ctx.createDynamicsCompressor(); limiter.threshold.value = -12; limiter.ratio.value = 6;
    this.master.connect(limiter).connect(ctx.destination);
    this.lane = ctx.createGain(); this.lane.connect(this.duck);
    this.plaza = ctx.createGain(); this.plaza.gain.value = 0; this.plaza.connect(this.duck);
    this.filmDirect = ctx.createGain(); this.filmDirect.gain.value = 0; this.filmDirect.connect(this.master);
    const length = ctx.sampleRate * 3;
    this.noise = ctx.createBuffer(1, length, ctx.sampleRate);
    const data = this.noise.getChannelData(0);
    for (let i = 0; i < length; i++) data[i] = Math.random() * 2 - 1;
    // Lane: walls about 5 m apart give quick flutter echoes; plaza: a longer tail with facade echoes.
    this.reverb = ctx.createGain();
    const lane = ctx.createConvolver(), plaza = ctx.createConvolver();
    lane.buffer = impulse(ctx, 0.75, 0.004, [[0.014, 0.5, 0.2], [0.017, 0.2, 0.5], [0.029, 0.35, 0.15], [0.033, 0.15, 0.35], [0.046, 0.2, 0.1], [0.051, 0.1, 0.2]]);
    plaza.buffer = impulse(ctx, 1.5, 0.02, [[0.13, 0.3, 0.12], [0.21, 0.08, 0.22]]);
    this.laneWet = ctx.createGain(); this.plazaWet = ctx.createGain(); this.plazaWet.gain.value = 0;
    this.reverb.connect(lane).connect(this.laneWet).connect(this.duck);
    this.reverb.connect(plaza).connect(this.plazaWet).connect(this.duck);
  }

  /**
   * Renders one layer on its own, offline, from a listening spot in the gully, through the same code the
   * site plays (used by the sound preview page). `track` is the Aftermovie's bytes for the screen layers.
   */
  static async renderLayer(layer: PreviewLayer, seconds: number, track?: ArrayBuffer): Promise<AudioBuffer> {
    const rate = 44100, ctx = new OfflineAudioContext(2, Math.round(rate * seconds), rate);
    const audio = new GullyAudio();
    audio.enabled = true;
    audio.graph(ctx);
    let listener: Vec3 = [0, 7.6, 20], forward: Vec3 = [0, 0, -1];
    if (layer.startsWith("footsteps")) {
      const sprint = layer === "footsteps-sprint", speed = sprint ? 4.2 : 2.4;
      for (let t = 0.4; t < seconds - 0.4; t += strideAt(speed) / speed) {
        audio.footstep(layer === "footsteps-wet", sprint ? 1 : 0.45, t, sprint);
      }
    } else if (layer === "lane-horns") for (let t = 0.4; t < seconds - 1; t += 2.6) audio.horn(t);
    else if (layer === "two-wheeler") { listener = [0, 7.6, 24]; audio.twoWheeler(0.3, 2.8); }
    else if (layer === "lamp-buzz") { listener = [-0.4, 7.6, 25.6]; audio.lampBuzz(lamps[0].position, false); }
    else if (layer === "lamp-flicker") {
      listener = [-0.4, 7.6, 16.1]; audio.lampBuzz(lamps[1].position, true);
      for (let t = 0; t < seconds; t += 1 / 30) audio.crackle(t);
    } else if (track) {
      const source = ctx.createBufferSource();
      source.buffer = await ctx.decodeAudioData(track.slice(0)); source.start(0, 40);
      if (layer === "shop-radio") { listener = [1.2, 7.6, 18]; audio.radioFrom(source); }
      else if (layer === "aftermovie-watching") { listener = aftermovieSeat; source.connect(audio.filmDirect); audio.watching(0, true); }
      else { audio.stageFrom(source); listener = layer === "stage-in-plaza" ? [0, 7.6, -28] : [0, 7.6, 14]; }
    }
    audio.place(listener, forward, 0, true);
    return ctx.startRendering();
  }

  private filter(type: BiquadFilterType, frequency: number, q = 0.7, gain = 0) {
    const f = this.ctx!.createBiquadFilter(); f.type = type; f.frequency.value = frequency; f.Q.value = q; f.gain.value = gain; return f;
  }

  private panner(position: Vec3, ref: number, rolloff: number) {
    const p = this.ctx!.createPanner();
    p.panningModel = "HRTF"; p.distanceModel = "inverse";
    p.refDistance = ref; p.rolloffFactor = rolloff; p.maxDistance = 150;
    p.positionX.value = position[0]; p.positionY.value = position[1]; p.positionZ.value = position[2];
    return p;
  }

  /** A placed source: input -> distance low-pass -> level -> HRTF panner -> bus, with a reverb send. */
  private emitter(position: Vec3, bus: AudioNode, options: { near: number; far: number; reach: number; wet: readonly [number, number]; ref: number; rolloff: number; occluded?: boolean }) {
    const ctx = this.ctx!;
    const filter = this.filter("lowpass", options.near), level = ctx.createGain(), send = ctx.createGain();
    const panner = this.panner(position, options.ref, options.rolloff);
    filter.connect(level).connect(panner).connect(bus);
    panner.connect(send).connect(this.reverb);
    const emitter: Emitter = { position, filter, level, send, ...options };
    this.emitters.push(emitter);
    return filter;
  }

  /** A one-shot through its own panner, a fixed distance filter and a reverb send. */
  private shot(position: Vec3, bus: AudioNode, wet: number, ref = 4, rolloff = 1) {
    const ctx = this.ctx!, panner = this.panner(position, ref, rolloff), send = ctx.createGain();
    send.gain.value = wet; panner.connect(bus); panner.connect(send).connect(this.reverb);
    return panner;
  }

  /** 100 Hz mains buzz from a lamp head; flickering lamps crackle. */
  private lampBuzz(position: Vec3, flicker: boolean) {
    const ctx = this.ctx!;
    const hum = ctx.createOscillator(); hum.type = "sawtooth"; hum.frequency.value = 100;
    const shape = this.filter("bandpass", 300, 1.2), gain = ctx.createGain();
    gain.gain.value = flicker ? 0.1 : 0.07;
    hum.connect(shape).connect(gain).connect(this.emitter(position, this.lane, { near: 2400, far: 500, reach: 16, wet: [0.02, 0.1], ref: 1.2, rolloff: 1.8 }));
    hum.start();
    if (flicker) this.flickers.push(gain);
  }

  /**
   * The plaza screen's looping Aftermovie is the music source: its sound plays from the screen's PA and,
   * band-passed, from the shop radio, in sync with the picture. While the visitor watches it (focused),
   * it also plays directly and everything else ducks. Media elements can feed Web Audio only after a user
   * gesture, so it connects when the audio starts and then unmutes the video.
   */
  attachFilm(video: HTMLVideoElement) {
    this.film = video;
    this.connectFilm();
  }

  private connectFilm() {
    const ctx = this.ctx, video = this.film;
    if (!ctx || !video || this.filmSource === video || !("createMediaElementSource" in ctx)) return;
    this.filmSource = video;
    this.filmInput((ctx as AudioContext).createMediaElementSource(video));
    video.muted = false;
    void video.play().catch(() => { /* paused while hidden */ });
  }

  private filmInput(source: AudioNode) {
    this.stageFrom(source);
    this.radioFrom(source);
    source.connect(this.filmDirect);
  }

  private stageFrom(input: AudioNode) {
    const ctx = this.ctx!;
    const gain = ctx.createGain(); gain.gain.value = 0.6;
    // PA speakers: no deep sub, a little 1 kHz and 2.5 kHz presence, rolled-off top.
    input.connect(this.filter("highpass", 55)).connect(this.filter("peaking", 1000, 1, 2))
      .connect(this.filter("peaking", 2500, 1.2, 2)).connect(this.filter("highshelf", 7000, 0.7, -5)).connect(gain)
      .connect(this.emitter(stage, this.duck, { near: 9000, far: 220, reach: 110, wet: [0.15, 0.7], ref: 9, rolloff: 1.1, occluded: true }));
  }

  private radioFrom(input: AudioNode) {
    const ctx = this.ctx!;
    const gain = ctx.createGain(); gain.gain.value = 0.12;
    input.connect(this.filter("highpass", 500)).connect(this.filter("lowpass", 2600)).connect(this.filter("peaking", 1200, 2, 4))
      .connect(gain).connect(this.emitter(radio, this.lane, { near: 3000, far: 600, reach: 28, wet: [0.1, 0.4], ref: 1.2, rolloff: 1.6 }));
  }

  private crackle(time: number) {
    for (const gain of this.flickers) if (Math.random() < 0.06) {
      gain.gain.setTargetAtTime(Math.random() < 0.5 ? 0.01 : 0.13, time, 0.02);
    }
  }

  /** A distant car or truck horn, from beyond either end of the lane. */
  private horn(time: number) {
    const ctx = this.ctx!;
    const side = Math.random() < 0.5 ? 1 : -1;
    const at: Vec3 = [rand(-25, 25), 7, side > 0 ? rand(45, 70) : rand(-65, -55)];
    const gain = ctx.createGain(), low = this.filter("lowpass", 1100);
    const length = rand(0.2, 0.6), level = rand(0.05, 0.08), double = Math.random() < 0.35;
    gain.gain.setValueAtTime(0, time);
    for (const [start, end] of double ? [[0, length * 0.45], [length * 0.6, length]] : [[0, length]]) {
      gain.gain.setValueAtTime(0, time + start);
      gain.gain.linearRampToValueAtTime(level, time + start + 0.025);
      gain.gain.setValueAtTime(level, time + end);
      gain.gain.linearRampToValueAtTime(0, time + end + 0.06);
    }
    for (const f of [rand(400, 470), rand(500, 580)]) {
      const o = ctx.createOscillator(); o.type = "sawtooth"; o.frequency.value = f;
      o.connect(low); o.start(time); o.stop(time + length + 0.1);
    }
    low.connect(gain).connect(this.shot(at, this.lane, 0.8, 6));
  }

  /** A scooter or motorbike crossing the lane mouth, with Doppler and throttle wobble. */
  private twoWheeler(time: number, duration = rand(2.4, 3.2)) {
    const ctx = this.ctx!, dir = Math.random() < 0.5 ? 1 : -1, f0 = rand(46, 62), end = time + duration;
    const panner = this.shot([-dir * 22, 6.8, 36], this.lane, 0.5, 5);
    (panner as PannerNode).positionX.setValueAtTime(-dir * 22, time);
    (panner as PannerNode).positionX.linearRampToValueAtTime(dir * 22, end);
    const low = this.filter("lowpass", 900, 1.5), gain = ctx.createGain();
    gain.gain.setValueAtTime(0, time); gain.gain.linearRampToValueAtTime(0.014, time + 0.5);
    gain.gain.setValueAtTime(0.014, end - 0.5); gain.gain.linearRampToValueAtTime(0, end);
    const wobble = ctx.createOscillator(), depth = ctx.createGain();
    wobble.frequency.value = rand(2, 4); depth.gain.value = f0 * 0.04; wobble.connect(depth);
    for (const [type, ratio, level] of [["sawtooth", 1, 1], ["square", 0.5, 0.5], ["sawtooth", 2.01, 0.25]] as const) {
      const o = ctx.createOscillator(), g = ctx.createGain(); o.type = type; g.gain.value = level;
      o.frequency.setValueAtTime(f0 * ratio * 1.05, time);
      o.frequency.linearRampToValueAtTime(f0 * ratio, time + duration / 2);
      o.frequency.linearRampToValueAtTime(f0 * ratio * 0.94, end);
      depth.connect(o.frequency);
      o.connect(g).connect(low); o.start(time); o.stop(end + 0.05);
    }
    wobble.start(time); wobble.stop(end + 0.05);
    low.connect(gain).connect(panner);
  }

  /** A short burst of the shared noise through a filter, for footstep layers. */
  private burst(t: number, out: AudioNode, level: number, type: BiquadFilterType, frequency: number, q: number, decay: number, attack = 0.004) {
    const ctx = this.ctx!, source = ctx.createBufferSource(), gain = ctx.createGain();
    source.buffer = this.noise; source.playbackRate.value = rand(0.9, 1.1);
    gain.gain.setValueAtTime(0, t); gain.gain.linearRampToValueAtTime(level, t + attack);
    gain.gain.exponentialRampToValueAtTime(0.0003, t + attack + decay);
    source.connect(this.filter(type, frequency, q)).connect(gain).connect(out);
    source.start(t, Math.random() * 2.5, attack + decay + 0.02);
  }

  /**
   * One footfall. `strength` 0-1 follows speed. Heel then toe (a slower roll when walking), on
   * alternating feet, with per-step pitch and level variation, grit on some steps, a clothing swish
   * when sprinting and a splash in puddles.
   */
  footstep(wet: boolean, strength: number, at?: number, sprint = false) {
    const ctx = this.ctx;
    if (!ctx || !this.enabled || (at === undefined && ctx.state !== "running")) return;
    const t = at ?? ctx.currentTime + 0.005;
    this.foot = -this.foot;
    const out = ctx.createStereoPanner(), send = ctx.createGain();
    out.pan.value = 0.1 * this.foot; send.gain.value = 0.3;
    out.connect(this.duck); out.connect(send).connect(this.reverb);
    const pitch = rand(0.95, 1.05), level = (sprint ? 0.11 : 0.1) * Math.min(1, 0.45 + strength * 0.55) * 10 ** (rand(-3, 3) / 20);
    const roll = sprint ? rand(0.015, 0.03) : rand(0.06, 0.09);
    // Heel thump.
    const thump = ctx.createOscillator(), thumpGain = ctx.createGain(), thumpEnd = sprint ? 0.1 : 0.075;
    thump.frequency.setValueAtTime((sprint ? 115 : 92) * pitch, t); thump.frequency.exponentialRampToValueAtTime(45, t + thumpEnd);
    thumpGain.gain.setValueAtTime(level * (sprint ? 1.1 : 0.8), t); thumpGain.gain.exponentialRampToValueAtTime(0.0005, t + thumpEnd);
    thump.connect(thumpGain).connect(out); thump.start(t); thump.stop(t + thumpEnd + 0.01);
    if (wet) {
      this.burst(t, out, level * 0.7, "bandpass", rand(1500, 2400) * pitch, 1.3, 0.14);
      this.burst(t + roll, out, level * 0.5, "bandpass", 700 * pitch, 1.2, 0.18);
      const band = this.filter("bandpass", 1800, 3), dropGain = ctx.createGain(), drops = ctx.createBufferSource();
      drops.buffer = this.noise;
      band.frequency.setValueAtTime(1800, t + 0.02); band.frequency.exponentialRampToValueAtTime(4200, t + 0.22);
      dropGain.gain.setValueAtTime(level * 0.55, t + 0.02); dropGain.gain.exponentialRampToValueAtTime(0.0005, t + 0.26);
      drops.connect(band).connect(dropGain).connect(out); drops.start(t + 0.02, Math.random() * 2, 0.26);
    } else {
      // Heel scuff, then the toe a moment later.
      this.burst(t, out, level, "lowpass", (sprint ? 1500 : 950) * pitch, 0.8, sprint ? 0.06 : 0.05);
      this.burst(t + roll, out, level * (sprint ? 0.8 : 0.55), "bandpass", (sprint ? 2200 : 1500) * pitch, 0.9, 0.04);
    }
    // Grit underfoot on some steps.
    if (Math.random() < 0.35) for (let k = 0; k < 2 + Math.floor(Math.random() * 3); k++) {
      this.burst(t + rand(0.01, 0.08), out, level * rand(0.12, 0.25), "highpass", rand(3500, 6000), 0.7, 0.006, 0.001);
    }
    // Clothing swish with each sprinting stride.
    if (sprint) this.burst(t - 0.06, out, level * 0.28, "bandpass", rand(1300, 1900), 0.8, 0.12, 0.06);
  }

  /**
   * Moves the listener and steers the mix: lane and plaza (reverbs included) cross-fade over the gate
   * (Three.js z from -4 to -16), emitters follow distance, the stage opens up as the plaza is entered.
   */
  private place(position: Vec3, forward: Vec3, now: number, immediate = false) {
    const ctx = this.ctx!, l = ctx.listener, set = (param: AudioParam, value: number, time = 0.05) => {
      if (immediate) param.setValueAtTime(value, now); else param.setTargetAtTime(value, now, time);
    };
    if (l.positionX) {
      set(l.positionX, position[0], 0.03); set(l.positionY, position[1], 0.03); set(l.positionZ, position[2], 0.03);
      set(l.forwardX, forward[0], 0.03); set(l.forwardY, forward[1], 0.03); set(l.forwardZ, forward[2], 0.03);
      l.upX.value = 0; l.upY.value = 1; l.upZ.value = 0;
    } else {
      l.setPosition(...position); l.setOrientation(...forward, 0, 1, 0);
    }
    // The mix and emitter curves change slowly: about 15 updates a second is plenty.
    if (!immediate && now - this.placed < 0.066) return;
    this.placed = now;
    const plaza = this.plazaMix = smooth(4, 16, -position[2]);
    set(this.plaza.gain, plaza, 0.4); set(this.lane.gain, 1 - plaza * 0.75, 0.4);
    set(this.laneWet.gain, 1 - plaza, 0.4); set(this.plazaWet.gain, plaza, 0.4);
    for (const e of this.emitters) {
      const d = Math.hypot(position[0] - e.position[0], position[1] - e.position[1], position[2] - e.position[2]);
      const open = e.occluded ? 0.3 + 0.7 * plaza : 1;
      set(e.filter.frequency, (e.far + (e.near - e.far) * Math.exp(-d / (e.reach * 0.35))) * open, 0.1);
      set(e.level.gain, (1 - smooth(e.reach * 0.8, e.reach, d)) * (e.occluded ? 0.5 + 0.5 * plaza : 1), 0.1);
      set(e.send.gain, e.wet[0] + (e.wet[1] - e.wet[0]) * Math.min(1, d / e.reach), 0.1);
    }
  }

  /** Watching the film: it plays directly, and the gully (its own screen sound included) ducks. */
  private watching(now: number, on: boolean) {
    this.duck.gain.setTargetAtTime(on ? 0.12 : 1, now, 0.25);
    this.filmDirect.gain.setTargetAtTime(on ? 0.7 : 0, now, 0.25);
  }

  /** Per frame: listener, mix, lamp crackle and the scattered one-shots. */
  update(position: Vec3, forward: Vec3, ducked: boolean) { // ducked: the visitor is watching the Aftermovie
    const ctx = this.ctx;
    if (!ctx || ctx.state !== "running") return;
    const now = ctx.currentTime;
    this.place(position, forward, now);
    this.watching(now, ducked);
    this.crackle(now);
    const inLane = this.plazaMix < 0.6, next = this.next;
    if (now > next.horn) { if (inLane || Math.random() < 0.4) this.horn(now + 0.05); next.horn = now + rand(9, 27); }
    if (now > next.wheeler) { if (inLane) this.twoWheeler(now + 0.05); next.wheeler = now + rand(25, 55); }
  }

  dispose() {
    this.disposed = true;
    this.listeners.splice(0).forEach(off => off());
    void (this.ctx as AudioContext | null)?.close();
    this.ctx = null;
  }
}
