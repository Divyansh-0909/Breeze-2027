"use client";
import { useEffect, useLayoutEffect, useMemo, useRef } from "react";
import * as THREE from "three";
import Trusses from "@/components/landing-page/stage3d/Trusses";
import { exitGeometry, groundGeometry, portalGeometry, quarryGeometry, tunnelGeometry, wallPaintGeometry } from "./blockoutGeometry";
import { point3, world } from "./world";
import { travelZones } from "./navigation";
import { makeBoardTexture, makeGraffitiTexture, makeGroundTexture, makeRockTexture, requireWorldFonts } from "./worldPaint";
import { quarryWithoutWallFace, type WallReplacement } from "./wallSection";
import {tunnelOutsideQuarryRear} from "./quarryRollout";
import {caveLegacyInterface,mapCaveLegacyMaterial} from './caveLegacyInterface';

export function WorldSign({ label, position, rotation=[0,0,0], size=[4.5,.84], color="#e4ded0", arrow, textSize }: { label:string;position:[number,number,number];rotation?:[number,number,number];size?:[number,number];color?:string;arrow?:[number,number];textSize?:number }) {
  requireWorldFonts();
  const [width,height]=size,arrowX=arrow?.[0],arrowY=arrow?.[1];
  const board=useMemo(()=>{
    const g=new THREE.BoxGeometry(width,height,.16);
    g.setIndex(Array.from(g.index!.array).filter((_,i)=>i<24||i>=30));g.clearGroups();return g;
  },[width,height]);
  const texture=useMemo(()=>makeBoardTexture(label,color,arrowX===undefined||arrowY===undefined?undefined:[arrowX,arrowY],width/height,textSize===undefined?undefined:textSize/height),[label,color,arrowX,arrowY,width,height,textSize]);
  useEffect(()=>()=>{board.dispose();texture.dispose();},[board,texture]);
  return <group position={position} rotation={rotation}>
    <mesh><primitive object={board} attach="geometry" dispose={null} /><meshLambertMaterial color="#363932" /></mesh>
    <mesh position-z={.081}><planeGeometry args={[width,height]} /><meshBasicMaterial map={texture} /></mesh>
  </group>;
}
function Rock({ geometry,map,quarry=false }: { geometry:THREE.BufferGeometry;map:THREE.Texture;quarry?:boolean }) {
  useEffect(()=>()=>geometry.dispose(),[geometry]);
  return <mesh><primitive object={geometry} attach="geometry" dispose={null} />{quarry
    ? <meshStandardMaterial roughness={.98} flatShading vertexColors side={THREE.DoubleSide} />
    : <meshLambertMaterial map={map} vertexColors side={THREE.DoubleSide} />}</mesh>;
}
type Box={p:[number,number,number];size:[number,number,number];color:string;rotation?:THREE.Quaternion};
function Boxes({entries}:{entries:Box[]}) {
  const mesh=useRef<THREE.InstancedMesh>(null);
  useLayoutEffect(()=>{
    const m=new THREE.Matrix4(),p=new THREE.Vector3(),s=new THREE.Vector3(),q=new THREE.Quaternion();
    entries.forEach((e,i)=>{m.compose(p.fromArray(e.p),e.rotation??q.identity(),s.fromArray(e.size));mesh.current!.setMatrixAt(i,m);mesh.current!.setColorAt(i,new THREE.Color(e.color));});
    mesh.current!.instanceMatrix.needsUpdate=true;mesh.current!.instanceColor!.needsUpdate=true;mesh.current!.computeBoundingSphere();
  },[entries]);
  return <instancedMesh ref={mesh} args={[undefined,undefined,entries.length]}><boxGeometry /><meshLambertMaterial /></instancedMesh>;
}
function Cables({segments}:{segments:number[]}) {
  const geometry=useMemo(()=>{const g=new THREE.BufferGeometry();g.setAttribute("position",new THREE.Float32BufferAttribute(segments,3));return g;},[segments]);
  useEffect(()=>()=>geometry.dispose(),[geometry]);
  return <lineSegments><primitive attach="geometry" object={geometry} dispose={null} /><lineBasicMaterial color="#202721" /></lineSegments>;
}
function Bulbs({positions,scale=.075}:{positions:number[][];scale?:number}) {
  const mesh=useRef<THREE.InstancedMesh>(null);
  useLayoutEffect(()=>{const m=new THREE.Matrix4();positions.forEach((p,i)=>{m.makeScale(scale,scale,scale);m.setPosition(...point3(p));mesh.current!.setMatrixAt(i,m);});mesh.current!.instanceMatrix.needsUpdate=true;mesh.current!.computeBoundingSphere();},[positions,scale]);
  return <instancedMesh ref={mesh} args={[undefined,undefined,positions.length]}><sphereGeometry args={[1,8,4]} /><meshBasicMaterial color="#ffdaa0" toneMapped={false} /></instancedMesh>;
}
function HangingLamps() {
  const mesh=useRef<THREE.InstancedMesh>(null),positions=useMemo(()=>[[-6.4,10,2.35],[0,10,2.35],[6.4,10,2.35]],[]);
  useLayoutEffect(()=>{const m=new THREE.Matrix4();positions.forEach((p,i)=>{m.makeTranslation(...point3(p));mesh.current!.setMatrixAt(i,m);});mesh.current!.instanceMatrix.needsUpdate=true;mesh.current!.computeBoundingSphere();},[positions]);
  return <>
    <instancedMesh ref={mesh} args={[undefined,undefined,3]}><coneGeometry args={[.42,.38,12,1,true]} /><meshLambertMaterial color="#50574b" side={THREE.DoubleSide} /></instancedMesh>
    <Bulbs positions={positions.map(p=>[p[0],p[1]-.16,p[2]])} scale={.18} />
    <pointLight position={[0,9.75,2.6]} intensity={42} distance={21} decay={2} color="#ffc681" />
  </>;
}
function Scaffold() {
  const {position:p,width:w,height:h,depth:d}=world.scaffold;
  // One world-space font size fits even Past Sponsors beside its arrow.
  const navigationTextSize=.58;
  const signs=[
    {label:"EVENTS",id:"events",x:-5.1,y:8.8,tilt:.026,size:[6.4,1.16]},
    {label:"PAST SPONSORS",id:"sponsors",x:5.1,y:8.8,tilt:-.025,size:[6.5,1.16]},
    {label:"TEAM",id:"team",x:-5.1,y:7.25,tilt:.018,size:[6.3,1.13]},
    {label:"CONTACT US",id:"contact",x:5.1,y:7.25,tilt:-.032,size:[6.5,1.13]},
    {label:"AFTERMOVIE",id:"aftermovie",x:0,y:5.65,tilt:0,size:[9.2,1.18]},
  ];
  const cables=useMemo(()=>{
    const segments:number[]=[];
    const cable=(x:number,top:number,bottom:number,z=1.8)=>segments.push(x,top,z,x,bottom,z);
    // The entire hanging hierarchy is carried by the reused front top beam.
    for(const x of [-3.7,3.7]) cable(x,h-.5,11.4+1.2/Math.cos(.02)+x*Math.tan(.02));
    for(const x of [-7.4,-2.8,2.8,7.4]) {
      cable(x,h-.5,9.38);cable(x,8.22,7.815);
    }
    for(const x of [-3.3,3.3]) cable(x,6.685,6.24);
    // Run lamp suspension behind the header before reaching the shades below it.
    for(const x of [-6.4,0,6.4]) segments.push(x,h-.5,1.7,x,10.19,1.7,x,10.19,1.7,x,10.19,2.35);
    return segments;
  },[h]);
  const feet=useMemo<Box[]>(()=>[-w/2,w/2].map(x=>({p:[x,.18,d/2],size:[1.2,.36,1.2],color:"#6f6b5f"})),[w,d]);
  return <group position={point3(p)}>
    <Trusses frontOnly width={w} height={h} frontZ={d/2} />
    <Boxes entries={feet} /><Cables segments={cables} /><HangingLamps />
    <WorldSign label="GULLYVERSE" position={[0,11.4,1.8]} rotation={[0,0,.02]} size={[10,2.4]} />
    {signs.map(sign=>{
      const zone=travelZones.find(zone=>zone.id===sign.id);
      const target=zone!.center;
      const dx=target[0]-world.hub.spawn[0],dz=target[2]-world.hub.spawn[2];
      // Diagonal arrows match the corresponding corner sectors. Aftermovie
      // stays directly behind the visitor, so its arrow remains downward.
      const arrow:[number,number]=[Math.sign(dx),Math.sign(dz)];
      const c=Math.cos(sign.tilt),s=Math.sin(sign.tilt);
      return <WorldSign key={sign.label} label={sign.label} position={[sign.x,sign.y,1.8]} rotation={[0,0,sign.tilt]} size={sign.size as [number,number]} textSize={navigationTextSize} arrow={[arrow[0]*c+arrow[1]*s,-arrow[0]*s+arrow[1]*c]} />;
    })}
  </group>;
}
function StallBlocks() {
  const entries=useMemo(()=>{
    const boxes:Box[]=[];
    [...world.stalls,...world.destinations.filter(d=>d.id==="contact")].forEach((stall,i)=>{
      const [x,y,z]=stall.position,[width,height,depth]=stall.size,rotation=new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(0,1,0),stall.yaw);
      const add=(local:[number,number,number],size:[number,number,number],color:string)=>boxes.push({p:point3(new THREE.Vector3(...local).applyQuaternion(rotation).add(new THREE.Vector3(x,y,z)).toArray()),size,color,rotation});
      add([0,.6,0],[width,1.2,depth*.55],"#6e5942");add([0,height,0],[width+.7,.18,depth+.7],i%2?"#7d5542":"#515f55");
      for(const px of [-width/2,width/2]) for(const pz of [-depth/2,depth/2]) add([px,height/2,pz],[.12,height,.12],"#484e45");
    });
    const team=world.destinations.find(d=>d.id==="team")!;boxes.push({p:[team.position[0],1.9,team.position[2]],size:[1.2,3.8,8],color:"#716448"});
    return boxes;
  },[]);
  const bulbs=useMemo(()=>world.stalls.flatMap(stall=>Array.from({length:9},(_,i)=>{
    const local=new THREE.Vector3(-3.4+i*.85,3.25-Math.sin(i/8*Math.PI)*.3,2.12).applyAxisAngle(new THREE.Vector3(0,1,0),stall.yaw);return local.add(new THREE.Vector3(...point3(stall.position))).toArray();
  })),[]);
  const cables=useMemo(()=>{const result:number[]=[];for(let i=0;i<bulbs.length-1;i++) if(i%9!==8) result.push(...bulbs[i],...bulbs[i+1]);return result;},[bulbs]);
  return <>
    <Boxes entries={entries} /><Bulbs positions={bulbs} /><Cables segments={cables} />
    {world.destinations.filter(d=>d.id==="team"||d.id==="contact").map(d=><WorldSign key={d.id} label={d.label.toUpperCase()} position={[d.position[0]+Math.sin(d.yaw)*(d.size[2]/2+.16),3.05,d.position[2]]} rotation={[0,d.yaw,0]} size={[5,.8]} />)}
    {world.destinations.filter(d=>d.status==="reserved"&&d.id!=="accommodation").map(d=><group key={d.id}>
      <WorldSign label={d.label.toUpperCase()} position={[d.position[0],1.5,d.position[2]]} size={[7,1]} />
      <mesh position={[d.position[0],.65,d.position[2]-.1]}><boxGeometry args={[.12,1.3,.12]} /><meshLambertMaterial color="#5e6254" /></mesh>
    </group>)}
  </>;
}
function TunnelPaint() {
  const resources=useMemo(()=>world.tunnel.artists.map((a,i)=>({geometry:wallPaintGeometry(a.position,a.yaw>0?-1:1,5.5,1.55),texture:makeGraffitiTexture(a.label,["#d7bea2","#c77868","#aba4c9","#c8ae57","#81aca3"][i],481+i*99)})),[]);
  useEffect(()=>()=>resources.forEach(r=>{r.geometry.dispose();r.texture.dispose();}),[resources]);
  return <>{resources.map((r,i)=><mesh key={i}><primitive object={r.geometry} attach="geometry" dispose={null} /><meshBasicMaterial map={r.texture} transparent alphaTest={.08} side={THREE.DoubleSide} depthWrite={false} /></mesh>)}</>;
}
function EntrancePaint({portal}:{portal:THREE.BufferGeometry}) {
  const texture=useMemo(()=>makeGraffitiTexture("GULLYVERSE","#e8dfc6",154),[]);
  const geometry=useMemo(()=>{
    const g=new THREE.PlaneGeometry(8,1.95,40,8),material=new THREE.MeshBasicMaterial({side:THREE.DoubleSide}),rock=new THREE.Mesh(portal,material),ray=new THREE.Raycaster();
    const positions=g.attributes.position,origin=new THREE.Vector3(),direction=new THREE.Vector3(0,0,-1);
    for(let i=0;i<positions.count;i++) {
      const x=positions.getX(i)-.2,y=positions.getY(i)+6.8;
      ray.set(origin.set(x,y,4),direction);const hit=ray.intersectObject(rock)[0];
      positions.setXYZ(i,x,y,hit?hit.point.z+.035:.3);
    }
    material.dispose();g.computeVertexNormals();return g;
  },[portal]);
  useEffect(()=>()=>{texture.dispose();geometry.dispose();},[texture,geometry]);
  return <mesh><primitive object={geometry} attach="geometry" dispose={null} /><meshBasicMaterial map={texture} transparent alphaTest={.07} depthWrite={false} /></mesh>;
}
/** Explicit human-scale blockout markers; production crowd assets remain Stage 4 work. */
function Population({nearStage,quality}:{nearStage:boolean;quality:number}) {
  const mesh=useRef<THREE.InstancedMesh>(null);
  const people=useMemo(()=>{
    const result:[number,number,number][]=[];
    const group=(center:number[],size:number[],count:number,seed:number)=>{for(let i=0;i<count;i++) result.push([center[0]+(((i*37+seed*17)%101)/101-.5)*size[0],.85,center[1]+(((i*61+seed*29)%103)/103-.5)*size[1]]);};
    group(world.population.exit.center,world.population.exit.size,world.population.exit.count,1);group(world.population.circulation.center,world.population.circulation.size,world.population.circulation.count,2);
    world.stalls.forEach((stall,i)=>group([stall.position[0]+Math.sign(-stall.position[0])*5,stall.position[2]],[3,5],world.population.stallGroupCount,i+3));
    if(!nearStage) for(let i=0;i<(quality>=2?160:world.population.stageFarCount);i++) {const x=((i*37)%101)/101*44-22,z=4.5+((i*61)%103)/103*18;if(Math.abs(x)<3.7) continue;result.push([world.stage.origin[0]+x,.85,world.stage.origin[2]+z]);}
    return result;
  },[nearStage,quality]);
  useLayoutEffect(()=>{const matrix=new THREE.Matrix4();people.forEach((p,i)=>{matrix.makeTranslation(...p);mesh.current!.setMatrixAt(i,matrix);mesh.current!.setColorAt(i,new THREE.Color(["#454b48","#5e6653","#775b4d","#46515c"][i%4]));});mesh.current!.instanceMatrix.needsUpdate=true;mesh.current!.instanceColor!.needsUpdate=true;mesh.current!.computeBoundingSphere();},[people]);
  return <instancedMesh ref={mesh} args={[undefined,undefined,people.length]}><capsuleGeometry args={[.23,1.24,2,5]} /><meshLambertMaterial /></instancedMesh>;
}
function GroundDetail() {
  const stones=useRef<THREE.InstancedMesh>(null),grass=useRef<THREE.InstancedMesh>(null);
  const tufts=useMemo(()=>{
    const g=new THREE.BufferGeometry(),p:number[]=[];
    for(let i=0;i<3;i++) {const a=i*Math.PI/3,x=Math.cos(a)*.11,z=Math.sin(a)*.11;p.push(-x,0,-z,x,0,z,.04,.28+i*.035,.02);}
    g.setAttribute("position",new THREE.Float32BufferAttribute(p,3));g.computeVertexNormals();return g;
  },[]);
  useEffect(()=>()=>tufts.dispose(),[tufts]);
  useLayoutEffect(()=>{
    const m=new THREE.Matrix4();
    for(let i=0;i<340;i++) {
      const side=i%2?-1:1,z=21-((i*61)%263),x=side*(4+((i*47)%61));
      m.makeScale(.06+(i%5)*.022,.026,.06+(i%3)*.021);m.setPosition(x,.024,z);stones.current!.setMatrixAt(i,m);stones.current!.setColorAt(i,new THREE.Color(i%3?"#696b61":"#97968a"));
    }
    for(let i=0;i<180;i++) {const side=i%2?-1:1,z=17-((i*47)%229),x=side*(10+((i*31)%57));m.makeRotationY(i*1.9);m.setPosition(x,-.005,z);grass.current!.setMatrixAt(i,m);}
    stones.current!.instanceMatrix.needsUpdate=true;stones.current!.instanceColor!.needsUpdate=true;stones.current!.computeBoundingSphere();grass.current!.instanceMatrix.needsUpdate=true;grass.current!.computeBoundingSphere();
  },[]);
  return <>
    <instancedMesh ref={stones} args={[undefined,undefined,340]}><icosahedronGeometry args={[1,0]} /><meshLambertMaterial /></instancedMesh>
    <instancedMesh ref={grass} args={[undefined,undefined,180]}><primitive object={tufts} attach="geometry" dispose={null} /><meshLambertMaterial color="#626849" side={THREE.DoubleSide} /></instancedMesh>
  </>;
}
function BorrowedCaveRock({geometry,material,map}:{geometry:THREE.BufferGeometry;material:THREE.MeshStandardMaterial|null;map:THREE.Texture}) {
  const fallback=useMemo(()=>new THREE.MeshLambertMaterial({map,vertexColors:true,side:THREE.DoubleSide}),[map]);
  useEffect(()=>()=>geometry.dispose(),[geometry]);
  useEffect(()=>()=>fallback.dispose(),[fallback]);
  return <mesh geometry={geometry} material={material??fallback} dispose={null}/>;
}
export default function HubScene({nearStage,quality,stageView=false,wallReplacement=null,authoredQuarry=false,caveReview=false,caveActive=false,caveMaterial=null}:{nearStage:boolean;quality:number;overview:boolean;stageView?:boolean;wallReplacement?:WallReplacement;authoredQuarry?:boolean;caveReview?:boolean;caveActive?:boolean;caveMaterial?:THREE.MeshStandardMaterial|null}) {
  requireWorldFonts();
  const quarry=useMemo(()=>authoredQuarry?null:wallReplacement?quarryWithoutWallFace(wallReplacement):quarryGeometry(),[wallReplacement,authoredQuarry]),tunnel=useMemo(()=>caveActive?mapCaveLegacyMaterial(caveLegacyInterface(authoredQuarry)):authoredQuarry?tunnelOutsideQuarryRear():tunnelGeometry(),[authoredQuarry,caveActive]),portal=useMemo(()=>caveActive?null:portalGeometry(),[caveActive]),exit=useMemo(()=>authoredQuarry?null:exitGeometry(),[authoredQuarry]),ground=useMemo(groundGeometry,[]);
  const rockTexture=useMemo(makeRockTexture,[]),groundTexture=useMemo(makeGroundTexture,[]);
  useEffect(()=>()=>{ground.dispose();rockTexture.dispose();groundTexture.dispose();},[ground,rockTexture,groundTexture]);
  return <>
    <color attach="background" args={[stageView?"#b2bbb9":"#737d87"]} /><fog attach="fog" args={stageView?["#b2bbb9",55,130]:["#737d87",205,520]} />
    <hemisphereLight args={stageView?["#d8e0dd","#686b59",.65]:["#a9bfd4","#8a8274",1.35]} />
    {!stageView && <directionalLight position={[-70,37,-145]} intensity={1.35} color="#efd0a4" />}
    {quarry&&<Rock geometry={quarry} map={rockTexture} quarry />}
    {caveReview?<BorrowedCaveRock geometry={tunnel} material={caveActive?caveMaterial:null} map={rockTexture}/>:<Rock geometry={tunnel} map={rockTexture} />}
    {portal&&<Rock geometry={portal} map={rockTexture} />}{exit&&<Rock geometry={exit} map={rockTexture} quarry />}
    <mesh><primitive object={ground} attach="geometry" dispose={null} /><meshLambertMaterial map={groundTexture} color="#c8c2b4" /></mesh>
    {!caveReview&&portal&&<EntrancePaint portal={portal} />}{!caveReview&&<TunnelPaint />}<Scaffold /><StallBlocks /><Population nearStage={nearStage} quality={quality} /><GroundDetail />
  </>;
}
