import {
  Mesh, NearestFilter, NoColorSpace, ShaderMaterial, TextureLoader,
  type Object3D,
} from "three";

export async function mountSponsorDisplay(scene: Object3D, url: string, signal: AbortSignal) {
  const faces: Mesh[] = [];
  scene.traverse(object => {
    if (object instanceof Mesh && object.userData.ledScreen === true) faces.push(object);
  });
  if (faces.length !== 1 || !faces[0].geometry.getAttribute("uv")) {
    throw new Error("The source sponsor display is missing its face or UVs.");
  }

  const face = faces[0];
  const atlas = await new TextureLoader().loadAsync(url);
  if (signal.aborted) {
    atlas.dispose();
    throw signal.reason;
  }
  atlas.colorSpace = NoColorSpace;
  atlas.flipY = false;
  atlas.minFilter = atlas.magFilter = NearestFilter;
  atlas.generateMipmaps = false;
  if (atlas.image.width !== 2048 || atlas.image.height !== 384) {
    atlas.dispose();
    throw new Error("The sponsor display strip has an unexpected size.");
  }
  const original = face.material;
  const material = new ShaderMaterial({
    name: "Rev15Z sponsor LED",
    uniforms: { strip: { value: atlas }, offset: { value: 0 } },
    vertexShader: `
      varying vec2 panelUV;
      void main() {
        panelUV = uv;
        gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
      }
    `,
    fragmentShader: `
      varying vec2 panelUV;
      uniform sampler2D strip;
      uniform float offset;
      void main() {
        vec2 grid = clamp(panelUV, 0.0, 0.999999) * vec2(384.0, 64.0);
        float column = mod(floor(grid.x) + floor(offset), 10676.0);
        float row = floor(column / 2048.0) * 64.0 + floor(grid.y);
        vec2 pixel = vec2(mod(column, 2048.0) + 0.5, row + 0.5) / vec2(2048.0, 384.0);
        float ink = texture2D(strip, pixel).r;
        float dotMask = 1.0 - smoothstep(0.29, 0.43, length(fract(grid) - 0.5));
        // Phase 3: dimmed to 30% so the LED reads as a strip under the streetlamp, not the brightest thing in the lane.
        gl_FragColor = vec4(vec3(1.0, 0.035, 0.002) * ((ink * 2.4 + 0.006) * dotMask), 1.0);
        #include <tonemapping_fragment>
        #include <colorspace_fragment>
      }
    `,
  });
  face.material = material;
  return {
    advance(seconds: number) {
      material.uniforms.offset.value = (material.uniforms.offset.value + 30 * seconds) % 10676;
    },
    dispose() {
      face.material = original;
      material.dispose();
      atlas.dispose();
    },
  };
}
