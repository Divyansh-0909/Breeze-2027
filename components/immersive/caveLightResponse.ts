import type {MeshStandardMaterial} from 'three';

/** Local analytical opening/overburden approximation, not a GI bake. The
 * approved scene lights stay unchanged. Only cave surfaces screen the outdoor
 * direct/ambient contribution; no fixtures, new lights, textures or fake AO. */
export function installCaveLightResponse(material: MeshStandardMaterial, strength: {value:number}) {
  material.onBeforeCompile = shader => {
    shader.uniforms.caveSpillStrength = strength;
    shader.vertexShader = shader.vertexShader.replace('#include <common>', '#include <common>\nvarying float vCaveDepth;');
    shader.vertexShader = shader.vertexShader.replace('#include <project_vertex>', `#include <project_vertex>
      float caveStation = clamp(-(modelMatrix * vec4(transformed, 1.0)).z, 0.0, 42.0);
      vCaveDepth = min(caveStation, 42.0 - caveStation);`);
    shader.fragmentShader = shader.fragmentShader.replace('#include <common>', '#include <common>\nvarying float vCaveDepth;\nuniform float caveSpillStrength;');
    shader.fragmentShader = shader.fragmentShader.replace('#include <lights_fragment_end>', `#include <lights_fragment_end>
      float caveDirect = mix(1.0, 0.10 + 0.90 * exp(-vCaveDepth / 6.5), caveSpillStrength);
      float caveIndirect = mix(1.0, 0.55 + 0.45 * exp(-vCaveDepth / 11.0), caveSpillStrength);
      reflectedLight.directDiffuse *= caveDirect;
      reflectedLight.directSpecular *= caveDirect;
      reflectedLight.indirectDiffuse *= caveIndirect;
      reflectedLight.indirectSpecular *= caveIndirect;`);
  };
  material.customProgramCacheKey = () => 'gullyverse-local-cave-opening-response-v1';
  material.needsUpdate = true;
}
