import * as THREE from "three";

/**
 * Camera finishing pass (docs/runtime/REALISM-RESCUE-PLAN.md). The scene renders linear (no tone mapping) into a
 * half-float target, then one full-screen triangle tone-maps it once with the renderer's own operator (AgX) and adds
 * what a night camera adds: a soft halation around highlights (light bleeding into the air), a 1.5 px chroma offset
 * toward the frame edges, fine low-light grain and a light vignette. One extra draw call. On phones the target has
 * no MSAA and the halation uses half the taps.
 *
 * The scene's programs must be compiled for the target (their tone-mapping define differs from the screen's):
 * `ReadinessGate` binds `target` around compileAsync.
 */
export class FinishingPass {
  readonly target: THREE.WebGLRenderTarget;
  private readonly quad: THREE.Mesh;
  private readonly scene = new THREE.Scene();
  private readonly camera = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1);
  private readonly material: THREE.ShaderMaterial;
  private readonly size = new THREE.Vector2();
  private time = 0;

  constructor(gl: THREE.WebGLRenderer, phone: boolean) {
    gl.getDrawingBufferSize(this.size);
    this.target = new THREE.WebGLRenderTarget(this.size.x, this.size.y, {
      type: THREE.HalfFloatType, samples: phone ? 2 : 4, depthBuffer: true, colorSpace: THREE.LinearSRGBColorSpace,
    });
    this.material = new THREE.ShaderMaterial({
      name: "Breeze finishing pass",
      uniforms: { frame: { value: this.target.texture }, texel: { value: new THREE.Vector2(1 / this.size.x, 1 / this.size.y) }, time: { value: 0 } },
      // Phones: lighter grain (a small screen shows it as static on the floor).
      defines: { TAPS: phone ? 4 : 8, GRAIN: phone ? "0.022" : "0.036" },
      vertexShader: `varying vec2 vUv;
void main() { vUv = position.xy * 0.5 + 0.5; gl_Position = vec4(position.xy, 0.0, 1.0); }`,
      fragmentShader: `uniform sampler2D frame;
uniform vec2 texel;
uniform float time;
varying vec2 vUv;
float hash(vec2 p) { return fract(sin(dot(p, vec2(12.9898, 78.233))) * 43758.5453); }
void main() {
  vec2 fromCentre = vUv - 0.5;
  float edge = dot(fromCentre, fromCentre);
  // 1.5 px of lateral chroma toward the edges (an old lens), none at the centre.
  vec2 shift = fromCentre * edge * 4.0 * 1.5 * texel;
  vec3 colour = vec3(texture2D(frame, vUv + shift).r, texture2D(frame, vUv).g, texture2D(frame, vUv - shift).b);
  // Halation: highlights above 0.72 (lamp lenses, lit windows, the LED screen) bleed warm into the air around them.
  vec3 glow = vec3(0.0);
  // Three rings, each rotated half a tap, so a single bright dot spreads as a soft disc rather than a star.
  for (int i = 0; i < TAPS; i++) {
    float a = float(i) * 6.2831853 / float(TAPS);
    vec2 d = vec2(cos(a), sin(a)) * texel, e = vec2(cos(a + 3.14159 / float(TAPS)), sin(a + 3.14159 / float(TAPS))) * texel;
    glow += max(texture2D(frame, vUv + d * 4.0).rgb - 0.72, 0.0)
      + 0.7 * max(texture2D(frame, vUv + e * 9.0).rgb - 0.72, 0.0)
      + 0.45 * max(texture2D(frame, vUv + d * 16.0).rgb - 0.72, 0.0);
  }
  colour += glow / float(TAPS) * vec3(0.12, 0.09, 0.07);
  gl_FragColor = vec4(colour, 1.0);
  #include <tonemapping_fragment>
  #include <colorspace_fragment>
  // After tone mapping: grain strongest in the shadows (+-1.8%), light vignette (14% at the corners).
  float l = dot(gl_FragColor.rgb, vec3(0.2126, 0.7152, 0.0722));
  float grain = (hash(vUv * vec2(1733.0, 977.0) + fract(time * 13.7)) - 0.5) * GRAIN * (1.0 - smoothstep(0.1, 0.6, l));
  gl_FragColor.rgb = max(gl_FragColor.rgb + grain, 0.0) * (1.0 - 0.14 * smoothstep(0.08, 0.5, edge));
}`,
      depthTest: false, depthWrite: false,
    });
    const triangle = new THREE.BufferGeometry();
    triangle.setAttribute("position", new THREE.Float32BufferAttribute([-1, -1, 0, 3, -1, 0, -1, 3, 0], 3));
    this.quad = new THREE.Mesh(triangle, this.material);
    this.quad.frustumCulled = false;
    this.scene.add(this.quad);
  }

  /** Renders the scene through the pass. Draw-call counters cover both renders (scene + 1). */
  render(gl: THREE.WebGLRenderer, scene: THREE.Scene, camera: THREE.Camera, delta: number) {
    gl.getDrawingBufferSize(this.size);
    if (this.size.x !== this.target.width || this.size.y !== this.target.height) {
      this.target.setSize(this.size.x, this.size.y);
      this.material.uniforms.texel.value.set(1 / this.size.x, 1 / this.size.y);
    }
    this.time += delta;
    this.material.uniforms.time.value = this.time;
    const autoReset = gl.info.autoReset;
    gl.info.reset(); gl.info.autoReset = false;
    try {
      gl.setRenderTarget(this.target);
      gl.render(scene, camera);
      gl.setRenderTarget(null);
      gl.render(this.scene, this.camera);
    } finally { gl.info.autoReset = autoReset; }
  }

  /** Compiles the pass's own program alongside the scene's (no first-frame compile). */
  compile(gl: THREE.WebGLRenderer) { gl.compile(this.scene, this.camera); }

  dispose() {
    this.target.dispose(); this.material.dispose(); this.quad.geometry.dispose();
  }
}
