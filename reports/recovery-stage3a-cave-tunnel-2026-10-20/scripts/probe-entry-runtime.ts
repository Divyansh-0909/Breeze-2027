import * as THREE from 'three';
import {GLTFLoader} from 'three/examples/jsm/loaders/GLTFLoader.js';
import {readFile,writeFile} from 'node:fs/promises';
import {caveLegacyInterface,mapCaveLegacyMaterial} from '../../../components/immersive/caveLegacyInterface';
async function main(){
const root='public/models/gullyverse/';
async function load(path:string){let b=await readFile(root+path);return new GLTFLoader().parseAsync(new Uint8Array(b).buffer,'');}
const [foundation,cave,clearance]=await Promise.all(['quarry-foundation-refined/foundation-geometry.glb','c9-cave-recovery/cave-entrance.glb','c9-cave-recovery/entry-clearance.glb'].map(load));
const scene=new THREE.Scene();scene.add(foundation.scene,cave.scene);
for(const tile of ['1_2','2_2']) for(let level=0;level<3;level++){
 const target=scene.getObjectByName(`Foundation_Terrain_${tile}_LOD${level}`)as THREE.Mesh;
 target.geometry=(clearance.scene.getObjectByName(`Cave_Entry_Clearance_${tile}_LOD${level}`)as THREE.Mesh).geometry;
}
scene.traverse(o=>{if(o instanceof THREE.Mesh){o.visible=!/LOD[12]$/.test(o.name);o.material=new THREE.MeshBasicMaterial({side:THREE.DoubleSide});}});
const legacy=new THREE.Mesh(mapCaveLegacyMaterial(caveLegacyInterface(true)),new THREE.MeshBasicMaterial({side:THREE.DoubleSide}));legacy.name='Retained_Legacy_Tunnel';scene.add(legacy);scene.updateMatrixWorld(true);
const origin=new THREE.Vector3(0,1.72,11.5),rows=[];
for(let p of [[-.4,9,0],[-3.7,2.2,0],[-3.5,.8,2],[-3,1.72,-12],[-2.2,1.72,-8],[-4.1,1.72,-12],[-6,1.72,-16],[0,2,-12],[-2.5,4,-18],[0,3.5,0]]){
 let dir=new THREE.Vector3().fromArray(p).sub(origin).normalize();let ray=new THREE.Raycaster(origin,dir,0,60);
 let hits=ray.intersectObjects(scene.children,true).filter(h=>h.object.visible).slice(0,5).map(h=>({mesh:h.object.name,distance:h.distance,point:h.point.toArray(),normalDotRay:h.face?.normal.dot(dir)}));
 rows.push({origin:origin.toArray(),target:p,hits});
}
await writeFile('reports/recovery-stage3a-cave-tunnel-2026-10-20/raw/entry-selected-geometry-hit-probe.json',JSON.stringify({method:'Read-only CPU intersection of exact current selected GLBs and retained runtime generator. Same transforms and protected camera poses; DoubleSide inspection identifies hidden/back-facing geometry, no renderer changes.',rows},null,2));console.log(JSON.stringify(rows.map(r=>({target:r.target,first:r.hits[0]})),null,2));

}
main().catch(error=>{console.error(error);process.exitCode=1;});
