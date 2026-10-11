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
const tunnelOuterProfile=[[-26,-.08],[-28,7],[-20,16],[-8,18],[3,15],[18,16],[27,8],[30,-.08]];
function outerTunnelVertex(section:number,u:number,v:number):Vertex {
  const a=tunnelOuterProfile[section],b=tunnelOuterProfile[section+1];
  const x=lerp(a[0],b[0],u),y=lerp(a[1],b[1],u);
  // Weld the last two exterior rings: the old section-local noise left seams
  // at the quarry-facing rim. The entrance and enclosed passage stay unchanged.
  const phase=lerp(u,section+u,Math.max(0,(v-.8)/.2));
  return [x*(1+v*.13)+Math.sin(phase*6+v*13)*v*.5,y>0?lerp(y,49,v)+Math.sin(v*18+phase*9)*v*.8:y,lerp(-3,world.tunnel.endZ,v)];
}
/** Work-in-progress-2027's original faceted rock ring, fitted to the current layout. */
export function quarryGeometry() {
  const rock=new RockMesh(),boundary=world.quarry.boundary;
  const minX=Math.min(...boundary.map(p=>p[0])),maxX=Math.max(...boundary.map(p=>p[0]));
  const minZ=Math.min(...boundary.map(p=>p[1])),maxZ=Math.max(...boundary.map(p=>p[1]));
  const centerX=(minX+maxX)/2,centerZ=(minZ+maxZ)/2;
  // Uniform scaling keeps the original rock proportions around the larger world.
  const scale=((maxX-minX)/94+(maxZ-minZ)/126)/2;
  const source=new THREE.DodecahedronGeometry(1,0),vertices=source.getAttribute("position");
  try {
    for(let i=0;i<28;i++) {
      // Preserve the original three-rock gap around the current tunnel opening.
      if(i===0 || i===1 || i===27) continue;
      const angle=i/28*Math.PI*2,dx=Math.sin(angle),dz=Math.cos(angle);
      let distance=Infinity,edge=0;
      for(let j=0;j<boundary.length;j++) {
        const a=boundary[j],b=boundary[(j+1)%boundary.length];
        const ex=b[0]-a[0],ez=b[1]-a[1],denominator=dx*ez-dz*ex;
        if(Math.abs(denominator)<.00001) continue;
        const ax=a[0]-centerX,az=a[1]-centerZ;
        const t=(ax*ez-az*ex)/denominator,u=(ax*dz-az*dx)/denominator;
        if(t>0 && u>=0 && u<=1 && t<distance) {distance=t;edge=j;}
      }
      const a=boundary[edge],b=boundary[(edge+1)%boundary.length];
      const ex=b[0]-a[0],ez=b[1]-a[1],length=Math.hypot(ex,ez),nx=-ez/length,nz=ex/length;
      const h=21+Math.sin(i*4.1)*6;
      const matrix=new THREE.Matrix4().compose(new THREE.Vector3(),
        new THREE.Quaternion().setFromEuler(new THREE.Euler(.08*Math.sin(i),angle,.1*Math.cos(i))),
        new THREE.Vector3(14*scale,h*scale,12*scale));
      const points:Vertex[]=[];
      let minimum=Infinity;
      for(let j=0;j<vertices.count;j++) {
        const p=new THREE.Vector3().fromBufferAttribute(vertices,j).applyMatrix4(matrix);
        minimum=Math.min(minimum,p.x*nx+p.z*nz);points.push([p.x,p.y,p.z]);
      }
      // Keep the complete rock outside the existing walkable collision perimeter.
      const offset=.25-minimum,x=centerX+dx*distance+nx*offset,z=centerZ+dz*distance+nz*offset;
      for(const p of points) {p[0]+=x;p[1]+=(h*.47-2)*scale;p[2]+=z;}
      for(let j=0;j<points.length;j+=3) rock.triangle(points[j],points[j+1],points[j+2],1,i%3===0?"#74776d":"#838479");
    }
    return rock.finish();
  } finally {source.dispose();}
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
  for(let j=0;j<tunnelOuterProfile.length-1;j++) for(let segment=0;segment<10;segment++) {
    rock.quad(outerTunnelVertex(j,0,segment/10),outerTunnelVertex(j,1,segment/10),outerTunnelVertex(j,1,(segment+1)/10),outerTunnelVertex(j,0,(segment+1)/10),.72+(j%3)*.06);
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
  // Close the full exterior mass around the actual tunnel opening, rather
  // than leaving a detached 10m collar inside the much wider quarry-rock gap.
  // Retain every authored corner of both profiles, with broad facets matching
  // the surrounding blockout rocks instead of another thin rectangular panel.
  const sections=[...new Set([
    ...p.map((_,i)=>i/(p.length-1)),
    ...tunnelOuterProfile.map((_,i)=>i/(tunnelOuterProfile.length-1)),
  ])].sort((a,b)=>a-b),rings=5;
  const vertex=(section:number,ring:number):Vertex=>{
    const t=sections[section],inner=t*(p.length-1),j=Math.min(p.length-2,Math.floor(inner)),u=inner-j;
    const a=p[j],b=p[j+1],outer=t*(tunnelOuterProfile.length-1),k=Math.min(tunnelOuterProfile.length-2,Math.floor(outer));
    // The shell edges are straight between its corners; match those edges
    // exactly rather than resampling their original noise into a new curve.
    const rimA=outerTunnelVertex(k,0,1),rimB=outerTunnelVertex(k,1,1);
    const rim=rimA.map((v,i)=>lerp(v,rimB[i],outer-k)),progress=ring/rings;
    const envelope=Math.sin(progress*Math.PI),relief=envelope*(3.8+1.7*Math.sin(section*1.71+ring*1.93));
    const x=lerp(lerp(a[0],b[0],u)+tunnelCenterX(world.tunnel.endZ),rim[0],progress)+envelope*Math.sin(t*Math.PI)*Math.sin(section*2.17+ring)*.7;
    const y=lerp(lerp(a[1],b[1],u),rim[1],progress)+envelope*Math.sin(t*Math.PI)*Math.sin(section+ring*2.3)*1.1;
    // Relief stays outside the playable quarry; inner and outer edges match
    // the passage and shell exactly, with no surface stretched over the hole.
    return [x,y,world.tunnel.endZ+relief];
  };
  for(let section=0;section<sections.length-1;section++) for(let ring=0;ring<rings;ring++) {
    const shade=.91+Math.sin(section*.37+ring*1.73)*.045;
    rock.quad(vertex(section,ring),vertex(section+1,ring),vertex(section+1,ring+1),vertex(section,ring+1),shade,"#838479");
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
