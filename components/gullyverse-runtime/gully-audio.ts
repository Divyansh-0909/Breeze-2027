/**
 * Gully soundscape (Web Audio). Everything except the music is synthesised in the browser, so it ships
 * no audio files and carries no third-party licences:
 *
 * - footsteps on asphalt, or splashes inside the authored Rev15Z puddles and edge pools;
 * - a night-city bed in the lane (traffic rumble, occasional distant horns);
 * - the plaza crowd (a murmur) and the stage (the festival's own FireFire.mp3, low-passed and placed
 *   at the screen), cross-faded by zone;
 * - positional 100 Hz mains buzz at the street lamps (crackling on the two flickering ones) and a tinny
 *   shop radio (the same track, band-passed) in an open shop.
 *
 * Browsers only allow audio after a user gesture, so the context starts on the first pointer or key
 * press. The on/off choice is remembered.
 */

type Vec3 = readonly [number, number, number];
const storageKey = "breeze:sound";
const music = "/music/FireFire.mp3";
// Three.js coordinates of the Rev15Z street lamps (L02 and L05 are dead; L03 and L06 flicker).
const lamps: { position: Vec3; flicker: boolean }[] = [
  { position: [-1.17, 11.86, 25], flicker: false }, { position: [-1.17, 11.86, 15.5], flicker: true },
  { position: [1.17, 11.86, 15.5], flicker: false }, { position: [1.17, 12.08, 5.5], flicker: true },
];
const radio: Vec3 = [3.3, 8.6, 16];
const stage: Vec3 = [0, 11, -44.8];
// Puddles and edge pools (x, z, half width x, half depth z), extracted from the master.
const puddles: readonly (readonly [number, number, number, number])[] = [[-3.16, 26.51, 0.43, 3.35], [3.18, 26.07, 0.44, 3.46], [-3.15, 20.06, 0.42, 3.32], [3.15, 19.84, 0.45, 3.23], [-3.17, 13.68, 0.38, 2.98], [3.15, 13.56, 0.39, 2.98], [-12.66, -26.62, 0.51, 1.91], [-12.67, -30.97, 0.5, 2.03], [-12.67, -37.62, 0.46, 1.73], [12.64, -27.15, 0.47, 1.87], [12.65, -32.0, 0.51, 2.05], [12.66, -38.59, 0.47, 2.06], [-10.94, -15.01, 2.14, 0.41], [10.71, -15.02, 2.05, 0.41], [-12.54, -44.46, 0.42, 1.41], [12.51, -44.74, 0.46, 1.38], [-2.5, 25.96, 0.57, 0.74], [2.48, 13.41, 0.56, 0.64], [10.73, -18.4, 0.68, 0.9], [11.92, -27.37, 0.69, 0.9]];

export const isWet = (x: number, z: number) =>
  puddles.some(([px, pz, hx, hz]) => Math.abs(x - px) <= hx && Math.abs(z - pz) <= hz);

export function soundPreference() {
  try { return window.localStorage.getItem(storageKey) !== "off"; } catch { return true; }
}

export class GullyAudio {
  private ctx: AudioContext | null = null;
  private master!: GainNode;
  private lane!: GainNode;
  private plaza!: GainNode;
  private duck!: GainNode;
  private noise!: AudioBuffer;
  private flickers: GainNode[] = [];
  private nextHorn = 0;
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
      if (document.hidden) void this.ctx.suspend(); else if (this.enabled) void this.ctx.resume();
    };
    document.addEventListener("visibilitychange", visibility);
    this.listeners.push(() => document.removeEventListener("visibilitychange", visibility));
  }

  setEnabled(on: boolean) {
    this.enabled = on;
    try { window.localStorage.setItem(storageKey, on ? "on" : "off"); } catch { /* private mode */ }
    if (!this.ctx) { if (on) void this.start(); return; }
    this.master.gain.setTargetAtTime(on ? 0.9 : 0, this.ctx.currentTime, 0.15);
    if (on) void this.ctx.resume();
  }

  private async start() {
    if (this.ctx || this.disposed) return;
    const Context = window.AudioContext ?? (window as unknown as { webkitAudioContext?: typeof AudioContext }).webkitAudioContext;
    if (!Context) return;
    const ctx = this.ctx = new Context();
    this.listeners.splice(0).forEach(off => off()); // gestures no longer needed; re-arm visibility below
    const visibility = () => { if (document.hidden) void ctx.suspend(); else if (this.enabled) void ctx.resume(); };
    document.addEventListener("visibilitychange", visibility);
    this.listeners.push(() => document.removeEventListener("visibilitychange", visibility));

    this.master = ctx.createGain(); this.master.gain.value = this.enabled ? 0.9 : 0;
    this.duck = ctx.createGain(); this.duck.connect(this.master);
    const limiter = ctx.createDynamicsCompressor(); limiter.threshold.value = -12; limiter.ratio.value = 6;
    this.master.connect(limiter).connect(ctx.destination);
    this.lane = ctx.createGain(); this.lane.connect(this.duck);
    this.plaza = ctx.createGain(); this.plaza.gain.value = 0; this.plaza.connect(this.duck);

    const length = ctx.sampleRate * 3;
    this.noise = ctx.createBuffer(1, length, ctx.sampleRate);
    const data = this.noise.getChannelData(0);
    for (let i = 0; i < length; i++) data[i] = Math.random() * 2 - 1;

    this.cityBed();
    this.crowdBed();
    lamps.forEach(lamp => this.lampBuzz(lamp.position, lamp.flicker));
    void this.music();
    if (this.enabled) void ctx.resume();
  }

  private loopNoise(): AudioBufferSourceNode {
    const source = this.ctx!.createBufferSource();
    source.buffer = this.noise; source.loop = true;
    source.loopStart = Math.random(); source.start(0, Math.random() * 2);
    return source;
  }

  private filter(type: BiquadFilterType, frequency: number, q = 0.7) {
    const f = this.ctx!.createBiquadFilter(); f.type = type; f.frequency.value = frequency; f.Q.value = q; return f;
  }

  private panner(position: Vec3, ref: number, rolloff: number) {
    const p = this.ctx!.createPanner();
    p.panningModel = "HRTF"; p.distanceModel = "inverse";
    p.refDistance = ref; p.rolloffFactor = rolloff; p.maxDistance = 120;
    p.positionX.value = position[0]; p.positionY.value = position[1]; p.positionZ.value = position[2];
    return p;
  }

  /** Distant traffic rumble with a slowly breathing city hiss. */
  private cityBed() {
    const ctx = this.ctx!;
    const rumble = this.loopNoise(), low = this.filter("lowpass", 160), rumbleGain = ctx.createGain();
    rumbleGain.gain.value = 0.11;
    rumble.connect(low).connect(rumbleGain).connect(this.lane);
    const hiss = this.loopNoise(), band = this.filter("bandpass", 650, 0.6), hissGain = ctx.createGain();
    hissGain.gain.value = 0.018;
    const lfo = ctx.createOscillator(), depth = ctx.createGain();
    lfo.frequency.value = 0.07; depth.gain.value = 0.01; lfo.connect(depth).connect(hissGain.gain); lfo.start();
    hiss.connect(band).connect(hissGain).connect(this.lane);
  }

  /** A low crowd murmur: several speech-band noise voices with syllable-rate swells. */
  private crowdBed() {
    const ctx = this.ctx!;
    for (let i = 0; i < 6; i++) {
      const voice = this.loopNoise(), band = this.filter("bandpass", 420 + i * 230, 2.2), gain = ctx.createGain();
      gain.gain.value = 0.012;
      const syllables = ctx.createOscillator(), depth = ctx.createGain();
      syllables.frequency.value = 2.5 + Math.random() * 3; depth.gain.value = 0.01;
      syllables.connect(depth).connect(gain.gain); syllables.start();
      voice.connect(band).connect(gain).connect(this.plaza);
    }
  }

  /** 100 Hz mains buzz from a lamp head; flickering lamps crackle. */
  private lampBuzz(position: Vec3, flicker: boolean) {
    const ctx = this.ctx!;
    const hum = ctx.createOscillator(); hum.type = "sawtooth"; hum.frequency.value = 100;
    const shape = this.filter("bandpass", 300, 1.2), gain = ctx.createGain();
    gain.gain.value = flicker ? 0.05 : 0.03;
    hum.connect(shape).connect(gain).connect(this.panner(position, 1.2, 1.8)).connect(this.lane);
    hum.start();
    if (flicker) this.flickers.push(gain);
  }

  /** The festival track as muffled stage music at the screen and a tinny radio in an open shop. */
  private async music() {
    const ctx = this.ctx!;
    try {
      const response = await fetch(music);
      const buffer = await ctx.decodeAudioData(await response.arrayBuffer());
      if (this.disposed) return;
      const stageSource = ctx.createBufferSource(); stageSource.buffer = buffer; stageSource.loop = true;
      const stageGain = ctx.createGain(); stageGain.gain.value = 0.55;
      stageSource.connect(this.filter("lowpass", 260)).connect(stageGain).connect(this.panner(stage, 9, 1.1)).connect(this.plaza);
      stageSource.start(0, 12);
      const radioSource = ctx.createBufferSource(); radioSource.buffer = buffer; radioSource.loop = true;
      const radioGain = ctx.createGain(); radioGain.gain.value = 0.05;
      radioSource.connect(this.filter("highpass", 500)).connect(this.filter("lowpass", 2600))
        .connect(radioGain).connect(this.panner(radio, 1.2, 1.6)).connect(this.lane);
      radioSource.start(0, 70);
    } catch { /* music is optional */ }
  }

  private horn(time: number) {
    const ctx = this.ctx!;
    const gain = ctx.createGain(), low = this.filter("lowpass", 1400), pan = ctx.createStereoPanner();
    pan.pan.value = Math.random() * 1.6 - 0.8;
    const length = 0.25 + Math.random() * 0.4;
    gain.gain.setValueAtTime(0, time);
    gain.gain.linearRampToValueAtTime(0.014, time + 0.03);
    gain.gain.setValueAtTime(0.014, time + length);
    gain.gain.linearRampToValueAtTime(0, time + length + 0.08);
    for (const f of [410 + Math.random() * 60, 520 + Math.random() * 60]) {
      const o = ctx.createOscillator(); o.type = "sawtooth"; o.frequency.value = f;
      o.connect(low); o.start(time); o.stop(time + length + 0.1);
    }
    low.connect(gain).connect(pan).connect(this.lane);
  }

  /** One footstep. `strength` 0-1 follows walking speed. */
  footstep(wet: boolean, strength: number) {
    const ctx = this.ctx;
    if (!ctx || !this.enabled || ctx.state !== "running") return;
    const t = ctx.currentTime + 0.005, level = (0.09 + Math.random() * 0.03) * Math.min(1, 0.4 + strength * 0.6);
    const scuff = ctx.createBufferSource(); scuff.buffer = this.noise;
    scuff.playbackRate.value = 0.8 + Math.random() * 0.4;
    const tone = this.filter(wet ? "bandpass" : "lowpass", wet ? 1700 + Math.random() * 900 : 700 + Math.random() * 400, wet ? 1.4 : 0.8);
    const gain = ctx.createGain();
    const decay = wet ? 0.16 : 0.07;
    gain.gain.setValueAtTime(0, t);
    gain.gain.linearRampToValueAtTime(level * (wet ? 0.8 : 1), t + 0.006);
    gain.gain.exponentialRampToValueAtTime(0.0005, t + decay);
    scuff.connect(tone).connect(gain).connect(this.duck);
    scuff.start(t, Math.random() * 2, decay + 0.02);
    // Heel thump.
    const thump = ctx.createOscillator(), thumpGain = ctx.createGain();
    thump.frequency.setValueAtTime(95 + Math.random() * 20, t); thump.frequency.exponentialRampToValueAtTime(45, t + 0.06);
    thumpGain.gain.setValueAtTime(level * 0.9, t); thumpGain.gain.exponentialRampToValueAtTime(0.0005, t + 0.07);
    thump.connect(thumpGain).connect(this.duck); thump.start(t); thump.stop(t + 0.08);
    if (wet) {
      // Splash: a quick rising band of droplets.
      const drops = ctx.createBufferSource(); drops.buffer = this.noise;
      const band = this.filter("bandpass", 2400, 3), dropGain = ctx.createGain();
      band.frequency.setValueAtTime(1800, t + 0.02); band.frequency.exponentialRampToValueAtTime(4200, t + 0.2);
      dropGain.gain.setValueAtTime(level * 0.5, t + 0.02); dropGain.gain.exponentialRampToValueAtTime(0.0005, t + 0.24);
      drops.connect(band).connect(dropGain).connect(this.duck); drops.start(t + 0.02, Math.random() * 2, 0.25);
    }
  }

  /**
   * Per frame: moves the listener with the camera, cross-fades lane and plaza by depth (Three.js z;
   * the plaza begins near z = -16), crackles the flickering lamps and schedules distant horns.
   */
  update(position: Vec3, forward: Vec3, ducked: boolean) {
    const ctx = this.ctx;
    if (!ctx || ctx.state !== "running") return;
    const l = ctx.listener, now = ctx.currentTime;
    if (l.positionX) {
      l.positionX.setTargetAtTime(position[0], now, 0.03); l.positionY.setTargetAtTime(position[1], now, 0.03);
      l.positionZ.setTargetAtTime(position[2], now, 0.03);
      l.forwardX.setTargetAtTime(forward[0], now, 0.03); l.forwardY.setTargetAtTime(forward[1], now, 0.03);
      l.forwardZ.setTargetAtTime(forward[2], now, 0.03);
      l.upX.value = 0; l.upY.value = 1; l.upZ.value = 0;
    } else {
      l.setPosition(...position); l.setOrientation(...forward, 0, 1, 0);
    }
    const plaza = Math.min(1, Math.max(0, (-position[2] - 12) / 10));
    this.plaza.gain.setTargetAtTime(plaza, now, 0.4);
    this.lane.gain.setTargetAtTime(1 - plaza * 0.75, now, 0.4);
    this.duck.gain.setTargetAtTime(ducked ? 0.25 : 1, now, 0.25);
    for (const gain of this.flickers) if (Math.random() < 0.06) {
      gain.gain.setTargetAtTime(Math.random() < 0.5 ? 0.005 : 0.07, now, 0.02);
    }
    if (now > this.nextHorn) {
      if (this.nextHorn > 0 && plaza < 0.7) this.horn(now + 0.05);
      this.nextHorn = now + 9 + Math.random() * 18;
    }
  }

  dispose() {
    this.disposed = true;
    this.listeners.splice(0).forEach(off => off());
    void this.ctx?.close();
    this.ctx = null;
  }
}
