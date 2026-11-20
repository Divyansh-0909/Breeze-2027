import * as THREE from 'three';

// glTF cannot express the source Blender MixRGB and Vector Math nodes.
// Reconstruct their exact recorded values instead of showing raw untinted maps.
export function restoreWallMaterials(context, specifications) {
  const byName = new Map(specifications.map(spec => [spec.name, spec]));
  const restored = new Set();
  const textures = new Set();
  const records = [];
  context.traverse(object => {
    if (!object.isMesh) return;
    for (const material of Array.isArray(object.material) ? object.material : [object.material]) {
      if (!material || restored.has(material)) continue;
      restored.add(material);
      const spec = byName.get(material.name);
      if (!spec || !material.map) continue;
      if (spec.blend !== 'MIX') throw new Error('Unsupported source wall blend: ' + spec.blend);
      for (const key of ['map', 'normalMap', 'roughnessMap', 'metalnessMap']) {
        if (!material[key]) continue;
        const texture = material[key].clone();
        texture.wrapS = texture.wrapT = THREE.RepeatWrapping;
        texture.repeat.set(spec.uvScale, spec.uvScale);
        texture.needsUpdate = true;
        material[key] = texture;
        textures.add(texture);
      }
      material.color.setRGB(1, 1, 1);
      material.userData.sourceWall = spec;
      material.onBeforeCompile = shader => {
        shader.uniforms.sourceWallColor = { value: new THREE.Color().setRGB(...spec.color1.slice(0, 3)) };
        shader.uniforms.sourceWallMix = { value: spec.fac };
        shader.fragmentShader = shader.fragmentShader.replace(
          '#include <common>',
          '#include <common>\nuniform vec3 sourceWallColor;\nuniform float sourceWallMix;'
        ).replace('#include <map_fragment>', `
          #ifdef USE_MAP
            vec4 sourceWallSample = texture2D(map, vMapUv);
            diffuseColor.rgb *= mix(sourceWallColor, sourceWallSample.rgb, sourceWallMix);
            diffuseColor.a *= sourceWallSample.a;
          #endif
        `);
      };
      material.customProgramCacheKey = () => JSON.stringify(['source-wall-mix', spec.color1, spec.fac]);
      material.needsUpdate = true;
      records.push({ material: material.name, mix: spec.fac, color: spec.color1, uvScale: spec.uvScale });
    }
  });
  return { records, dispose: () => { for (const texture of textures) texture.dispose(); } };
}
