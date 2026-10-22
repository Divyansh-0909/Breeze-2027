import * as THREE from 'three';
import {tunnelGeometry} from './blockoutGeometry';
import {tunnelOutsideQuarryRear} from './quarryRollout';
import {world} from './world';
import material from '@/public/models/gullyverse/recovered-c8-material/manifest.json';

/** Remove the 56 existing INNER rings only. The complete private 42m passage
 * replaces them; every retained exterior attribute stays identical. */
export function caveLegacyInterface(authoredQuarry: boolean) {
  const source = authoredQuarry ? tunnelOutsideQuarryRear() : tunnelGeometry();
  const first = 56 * (world.tunnel.profile.length - 1) * 3 * 6;
  const geometry = new THREE.BufferGeometry();
  for (const [name, attribute] of Object.entries(source.attributes)) {
    const values = attribute.array.slice(first * attribute.itemSize);
    geometry.setAttribute(name, new THREE.BufferAttribute(values, attribute.itemSize, attribute.normalized));
  }
  source.dispose(); geometry.computeBoundingBox(); geometry.computeBoundingSphere();
  return geometry;
}

/** Private material compatibility only. Positions/normals and authoritative
 * geometry are unchanged. White vertex colours remove the old painted darkness
 * before borrowing the real C8 PBR maps; no second AO shadow is introduced. */
export function mapCaveLegacyMaterial(geometry: THREE.BufferGeometry) {
  const p = geometry.getAttribute('position'), n = geometry.getAttribute('normal');
  const uv = new Float32Array(p.count * 2), tangent = new Float32Array(p.count * 4);
  // Host UVs are metre/2. The borrowed material already owns the base repeat
  // and /3 sampling; applying that repeat again here would enlarge it twice.
  const colour = new Float32Array(p.count * 3).fill(1), repeat = 0.5;
  const islandPeriod = 8 / material.approvedUVRepeat;
  const a = new THREE.Vector3(), b = new THREE.Vector3(), c = new THREE.Vector3();
  const e1 = new THREE.Vector3(), e2 = new THREE.Vector3(), face = new THREE.Vector3();
  const normal = new THREE.Vector3(), t = new THREE.Vector3(), bitangent = new THREE.Vector3(), ortho = new THREE.Vector3();
  for (let i = 0; i < p.count; i += 3) {
    a.fromBufferAttribute(p, i); b.fromBufferAttribute(p, i+1); c.fromBufferAttribute(p, i+2);
    e1.subVectors(b,a); e2.subVectors(c,a); face.crossVectors(e1,e2);
    const axis = Math.abs(face.x) >= Math.abs(face.y) && Math.abs(face.x) >= Math.abs(face.z) ? 0 : Math.abs(face.y) >= Math.abs(face.z) ? 1 : 2;
    const axes = axis === 0 ? [1,2] : axis === 1 ? [0,2] : [0,1];
    for (let k=0; k<3; k++) {
      const v = k===0 ? a : k===1 ? b : c;
      uv[(i+k)*2] = v.getComponent(axes[0])*repeat + axis*islandPeriod;
      uv[(i+k)*2+1] = v.getComponent(axes[1])*repeat;
    }
    const du1=uv[(i+1)*2]-uv[i*2], dv1=uv[(i+1)*2+1]-uv[i*2+1];
    const du2=uv[(i+2)*2]-uv[i*2], dv2=uv[(i+2)*2+1]-uv[i*2+1];
    const determinant=du1*dv2-du2*dv1;
    if (Math.abs(determinant)<1e-12) throw new Error('Invalid inherited cave UV triangle');
    t.copy(e1).multiplyScalar(dv2).addScaledVector(e2,-dv1).divideScalar(determinant);
    bitangent.copy(e2).multiplyScalar(du1).addScaledVector(e1,-du2).divideScalar(determinant);
    for (let k=0; k<3; k++) {
      normal.fromBufferAttribute(n,i+k).normalize();
      ortho.copy(t).addScaledVector(normal,-normal.dot(t));
      if (ortho.lengthSq()<1e-18) throw new Error('Invalid inherited cave tangent frame');
      ortho.normalize(); tangent.set([ortho.x,ortho.y,ortho.z,new THREE.Vector3().crossVectors(normal,ortho).dot(bitangent)<0?-1:1],(i+k)*4);
    }
  }
  geometry.setAttribute('uv',new THREE.BufferAttribute(uv,2));
  geometry.setAttribute('tangent',new THREE.BufferAttribute(tangent,4));
  geometry.setAttribute('color',new THREE.BufferAttribute(colour,3));
  return geometry;
}
