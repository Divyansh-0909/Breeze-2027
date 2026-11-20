import * as THREE from 'three';

export async function loadBrick(spec) {
  const albedo = await new THREE.TextureLoader().loadAsync(spec.texture);
  albedo.colorSpace = THREE.SRGBColorSpace;
  albedo.wrapS = albedo.wrapT = THREE.RepeatWrapping;
  albedo.anisotropy = 4;
  const relief = albedo.clone();
  relief.colorSpace = THREE.NoColorSpace;
  relief.needsUpdate = true;
  return { spec, albedo, relief, dispose() { albedo.dispose(); relief.dispose(); } };
}

export function applyBrick(material, brick, isWall = false) {
  material.roughness = .91;
  material.metalness = 0;
  material.userData.brick = brick.spec;
  material.onBeforeCompile = shader => {
    Object.assign(shader.uniforms, {
      brickAlbedo: { value: brick.albedo }, brickRelief: { value: brick.relief },
      brickTile: { value: new THREE.Vector2(brick.spec.tileWidthM, brick.spec.tileHeightM) },
      brickDepth: { value: brick.spec.reliefM * brick.spec.bumpStrength },
      brickIsWall: { value: isWall ? 1 : 0 }
    });
    shader.vertexShader = shader.vertexShader.replace('#include <common>', '#include <common>\nvarying vec3 reviewPosition;')
      .replace('#include <begin_vertex>', '#include <begin_vertex>\nreviewPosition = (modelMatrix * vec4(transformed, 1.0)).xyz;');
    shader.fragmentShader = shader.fragmentShader.replace('#include <common>', `#include <common>
      varying vec3 reviewPosition;
      uniform sampler2D brickAlbedo;
      uniform sampler2D brickRelief;
      uniform vec2 brickTile;
      uniform float brickDepth;
      uniform float brickIsWall;
      vec2 brickUV() { return vec2(-reviewPosition.z, reviewPosition.y) / brickTile; }
      float brickHeight() {
        float raw = dot(texture2D(brickRelief, brickUV()).rgb, vec3(.2126, .7152, .0722));
        return clamp((raw - .02) / .17, 0.0, 1.0) * brickDepth;
      }
    `).replace('#include <map_fragment>', `#include <map_fragment>
      if (brickIsWall > .5) diffuseColor.rgb *= texture2D(brickAlbedo, brickUV()).rgb;
    `).replace('#include <normal_fragment_maps>', `#include <normal_fragment_maps>
      float height = brickHeight();
      vec3 surfaceX = dFdx(-vViewPosition), surfaceY = dFdy(-vViewPosition);
      vec3 crossY = cross(surfaceY, normal), crossX = cross(normal, surfaceX);
      float determinant = dot(surfaceX, crossY);
      vec3 gradient = dFdx(height) * crossY + dFdy(height) * crossX;
      normal = normalize(abs(determinant) * normal - sign(determinant) * gradient);
    `);
  };
  material.customProgramCacheKey = () => 'rev15k-black-brick-' + Number(isWall);
  material.needsUpdate = true;
  return material;
}

export function makeBrickWall(facade, brick) {
  const { x, y, z } = facade;
  const geometry = new THREE.BufferGeometry();
  geometry.setAttribute('position', new THREE.Float32BufferAttribute([
    x-.001,z[0],-y[1], x-.001,z[0],-y[0], x-.001,z[1],-y[0], x-.001,z[1],-y[1]
  ], 3));
  geometry.setIndex([0,1,2,0,2,3]);
  geometry.computeVertexNormals();
  const material = applyBrick(new THREE.MeshStandardMaterial({color:0xffffff, side:THREE.FrontSide}), brick, true);
  const wall = new THREE.Mesh(geometry, material);
  wall.name = 'REV15K / black-painted brick wall finish';
  return wall;
}
