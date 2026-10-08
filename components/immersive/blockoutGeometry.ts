import * as THREE from "three";
import { tunnelCenter, world } from "./world";

type Vertex = [number, number, number];
/** Deterministic composition meshes. Final sculpted rock and material work remains Stage 2. */
class RockMesh {
  positions: number[] = [];
  colors: number[] = [];
  uvs: number[] = [];
  triangle(a: Vertex, b: Vertex, c: Vertex, shade: number, base = "#e3dfd6") {
    const color = new THREE.Color(base).multiplyScalar(shade);
    for (const p of [a, b, c]) {
      this.positions.push(...p); this.colors.push(color.r, color.g, color.b);
      this.uvs.push((p[0]+p[2]*.35)*.22,(p[1]+p[2]*.3)*.22);
    }
  }
  quad(a: Vertex, b: Vertex, c: Vertex, d: Vertex, shade: number, base?: string) {
    this.triangle(a,b,c,shade,base); this.triangle(a,c,d,shade*.98,base);
  }
  finish() {
    const g = new THREE.BufferGeometry();
    g.setAttribute("position", new THREE.Float32BufferAttribute(this.positions,3));
    g.setAttribute("color",new THREE.Float32BufferAttribute(this.colors,3));
    g.setAttribute("uv",new THREE.Float32BufferAttribute(this.uvs,2));
    g.computeVertexNormals();
    // Weld only normals across coincident authored vertices. Colour/UV seams
    // stay intact, while triangulation stops looking like repeating panels.
    const normal=g.attributes.normal,position=g.attributes.position,sums=new Map<string,THREE.Vector3>();
    const key=(i:number)=>`${position.getX(i).toFixed(4)},${position.getY(i).toFixed(4)},${position.getZ(i).toFixed(4)}`;
    for(let i=0;i<normal.count;i++) {const k=key(i),sum=sums.get(k)??new THREE.Vector3();sum.x+=normal.getX(i);sum.y+=normal.getY(i);sum.z+=normal.getZ(i);sums.set(k,sum);}
    sums.forEach(n=>n.normalize());for(let i=0;i<normal.count;i++) {const n=sums.get(key(i))!;normal.setXYZ(i,n.x,n.y,n.z);}
    g.computeBoundingSphere(); return g;
  }
}
const lerp=(a:number,b:number,t:number)=>a+(b-a)*t;
export const tunnelCenterX=tunnelCenter;
function tubeNoise(z:number,y:number) {
  const seam=Math.sin((z-world.tunnel.startZ)/(world.tunnel.endZ-world.tunnel.startZ)*Math.PI);
  return (Math.sin(z*1.43+y*2.1)*.1+Math.sin(z*2.74-y*3.8)*.055)*seam;
}
function tubeVertex(z:number,p:readonly number[]):Vertex {
  const n=tubeNoise(z,p[1]);
  return [tunnelCenterX(z)+p[0]+n,p[1]+(p[1]>1?n*.5:0),z];
}
export function quarryGeometry() {
  const rock=new RockMesh(),q=world.quarry;
  const centerZ=(Math.min(...q.boundary.map(p=>p[1]))+Math.max(...q.boundary.map(p=>p[1])))/2;
  for(let i=0;i<q.boundary.length;i++) {
    const a=q.boundary[i],b=q.boundary[(i+1)%q.boundary.length];
    const vertex=(u:number,v:number):Vertex=>{
      const x=lerp(a[0],b[0],u),z=lerp(a[1],b[1],u),radius=Math.hypot(x,z-centerZ);
      const angle=(i+u)/q.boundary.length*Math.PI*2;
      const height=lerp(q.wallHeights[i],q.wallHeights[(i+1)%q.boundary.length],u);
      const fractured=Math.sin(angle*53+v*21)*.8+Math.sin(angle*91-v*9)*.34;
      const bench=Math.floor(v*4),setback=v*7.5+Math.sin(v*Math.PI*8)*.55+fractured*Math.sin(v*Math.PI);
      const base=i===0?Math.max(...world.tunnel.profile.map(p=>p[1]))+.2:0;
      return [x+x/radius*setback,lerp(base,height,v)+Math.sin(angle*17+v*4)*Math.sin(v*Math.PI)*1.2,z+(z-centerZ)/radius*setback+(bench%2?.12:0)];
    };
    for(let s=0;s<10;s++) for(let l=0;l<12;l++) {
      const u=s/10,v=(s+1)/10,y=l/12,ny=(l+1)/12;
      const shade=.77+Math.sin((i+u)*1.4+y*.7)*.035+(l/12)*.12;
      rock.quad(vertex(u,y),vertex(v,y),vertex(v,ny),vertex(u,ny),shade);
    }
  }
  return rock.finish();
}
export function tunnelGeometry() {
  const rock=new RockMesh(),profile=world.tunnel.profile;
  for(let ring=0;ring<56;ring++) {
    const z=lerp(world.tunnel.startZ,world.tunnel.endZ,ring/56),nz=lerp(world.tunnel.startZ,world.tunnel.endZ,(ring+1)/56);
    for(let j=0;j<profile.length-1;j++) for(let split=0;split<3;split++) {
      const a=profile[j],b=profile[j+1],p=[lerp(a[0],b[0],split/3),lerp(a[1],b[1],split/3)],q=[lerp(a[0],b[0],(split+1)/3),lerp(a[1],b[1],(split+1)/3)];
      const shade=.28+Math.pow(ring/56,3)*.5+(j<2||j>7?.06:0);
      rock.quad(tubeVertex(z,p),tubeVertex(nz,p),tubeVertex(nz,q),tubeVertex(z,q),shade);
    }
  }
  // Broad geological mass, continuous with the portal and the quarry front rim.
  const outer=[[-26,-.08],[-28,7],[-20,16],[-8,18],[3,15],[18,16],[27,8],[30,-.08]];
  for(let j=0;j<outer.length-1;j++) for(let segment=0;segment<10;segment++) {
    const a=outer[j],b=outer[j+1];
    const vertex=(u:number,v:number):Vertex=>{
      const x=lerp(a[0],b[0],u),y=lerp(a[1],b[1],u);
      return [x*(1+v*.13)+Math.sin(u*6+v*13)*v*.5,y>0?lerp(y,49,v)+Math.sin(v*18+u*9)*v*.8:y,-3-v*39];
    };
    rock.quad(vertex(0,segment/10),vertex(1,segment/10),vertex(1,(segment+1)/10),vertex(0,(segment+1)/10),.72+(j%3)*.06);
  }
  return rock.finish();
}
export function portalGeometry() {
  const rock=new RockMesh(),inner=world.tunnel.profile;
  const outer=[[-26,-.08],[-28,5.8],[-24,9.2],[-19,13.4],[-12,16.7],[-3,18],[7,16.1],[17,14.2],[25,9.3],[29,4.7],[30,-.08]];
  const vertex=(section:number,ring:number):Vertex=>{
    const index=Math.min(inner.length-2,Math.floor(section/4)),u=section/4-index;
    const p=[lerp(inner[index][0],inner[index+1][0],u),lerp(inner[index][1],inner[index+1][1],u)];
    const o=[lerp(outer[index][0],outer[index+1][0],u),lerp(outer[index][1],outer[index+1][1],u)];
    const progress=ring/8,relief=(Math.sin(section*1.47+ring*2.21)*.66+Math.sin(section*.55-ring*1.11)*.39)*Math.sin(progress*Math.PI);
    return [lerp(p[0],o[0],progress)+relief*.5,lerp(p[1],o[1],progress)+(p[1]>1?relief*.4:0),.28+Math.sin(progress*Math.PI)*1.65+relief*.75-progress*3.3];
  };
  for(let section=0;section<40;section++) for(let ring=0;ring<8;ring++) rock.quad(vertex(section,ring),vertex(section+1,ring),vertex(section+1,ring+1),vertex(section,ring+1),.81+Math.sin(section*.09+ring*.4)*.025);
  return rock.finish();
}
export function exitGeometry() {
  const rock=new RockMesh(),p=world.tunnel.profile;
  for(let j=0;j<p.length-1;j++) {
    const a=p[j],b=p[j+1],out=(v:readonly number[]):Vertex=>[v[0]<0?-5:5,Math.max(v[1],5.8),world.tunnel.endZ];
    rock.quad([a[0],a[1],world.tunnel.endZ],[b[0],b[1],world.tunnel.endZ],out(b),out(a),.8);
  }
  return rock.finish();
}
/** Painted names follow the same non-planar tunnel wall, rather than floating plaques. */
export function wallPaintGeometry(position:readonly number[],side:number,width:number,height:number) {
  const g=new THREE.BufferGeometry(),positions:number[]=[],uvs:number[]=[],indices:number[]=[];
  const profile=world.tunnel.profile,profileSide=side<0?profile.slice(0,6):profile.slice(5).reverse();
  for(let y=0;y<=6;y++) for(let x=0;x<=24;x++) {
    const z=position[2]+(x/24-.5)*width*(side<0?-1:1),py=position[1]+(y/6-.5)*height;
    let wallX=profileSide[0][0];
    for(let j=0;j<profileSide.length-1;j++) if(py>=profileSide[j][1]&&py<=profileSide[j+1][1]) wallX=lerp(profileSide[j][0],profileSide[j+1][0],(py-profileSide[j][1])/(profileSide[j+1][1]-profileSide[j][1]));
    positions.push(tunnelCenterX(z)+wallX+tubeNoise(z,py)-side*.034,py,z); uvs.push(x/24,y/6);
    if(y<6&&x<24) {const a=y*25+x;indices.push(a,a+1,a+26,a,a+26,a+25);}
  }
  g.setAttribute("position",new THREE.Float32BufferAttribute(positions,3));g.setAttribute("uv",new THREE.Float32BufferAttribute(uvs,2));g.setIndex(indices);g.computeVertexNormals();return g;
}
/** Walkable landing, passage, hub and stage floor remain exactly y=0. */
export function groundGeometry() {
  const g=new THREE.PlaneGeometry(...world.quarry.ground.size as [number,number],64,88);g.rotateX(-Math.PI/2);g.translate(0,0,world.quarry.ground.position[2]);
  const position=g.attributes.position;
  const [afMinX,afMaxX,afMinZ,afMaxZ]=world.aftermovie.bounds;
  const marginX=world.quarry.ground.size[0]/64*2,marginZ=world.quarry.ground.size[1]/88*2;
  for(let i=0;i<position.count;i++) {
    const x=position.getX(i),z=position.getZ(i);
    // Expand the exact-flat region by two grid cells so triangle interpolation
    // cannot slope beneath any eye-height navigation pose at the outer edge.
    const walkable=z>-64-marginZ||(x>afMinX-marginX&&x<afMaxX+marginX&&z>afMinZ-marginZ&&z<afMaxZ+marginZ);
    position.setY(i,walkable?0:-.03+Math.sin(x*.14+z*.11)*.022);
  }
  const uv=g.attributes.uv;
  for(let i=0;i<uv.count;i++) uv.setXY(i,position.getX(i)*.2,position.getZ(i)*.2);
  g.computeVertexNormals();return g;
}
