import assert from "node:assert/strict";
import { test } from "node:test";
import { DoubleSide, Euler, Mesh, MeshBasicMaterial, PerspectiveCamera, Raycaster, Vector3 } from "three";
import { ImmersiveRuntime } from "../../components/immersive/runtime";
import { boundaryClearance, boundaryCrossings, constrain, crossedHubDestination, destinationOptions, locationFromPath, movementBoundary, spawnPose, travelZones } from "../../components/immersive/navigation";
import { constrainQuarry, landingPose, lookAtPose, obstacles, tunnelCenter, world } from "../../components/immersive/world";
import { mapCamera } from "../../components/immersive/aerial";
import { portalGeometry, quarryGeometry, tunnelGeometry } from "../../components/immersive/blockoutGeometry";

function advance(runtime: ImmersiveRuntime, seconds: number, hz = 60) {
  for (let i = 0; i < Math.ceil(seconds * hz); i++) runtime.tick(1 / hz);
}
function hub() {
  const runtime = new ImmersiveRuntime("hub"); runtime.markReady(0); runtime.enter(); advance(runtime, 7.3); return runtime;
}
function approach(runtime: ImmersiveRuntime) {
  const target = travelZones.find((zone)=>zone.id==="aftermovie")!.center;
  runtime.input.lookX = runtime.pose.yaw - lookAtPose([runtime.pose.x,runtime.pose.y,runtime.pose.z],target).yaw;
  runtime.input.forward = 1;
  for (let frame=0;frame<2400 && runtime.getSnapshot().phase==="local";frame++) runtime.tick(1/60);
}
test("landing owns controls, entrance reaches hub, and frames don't publish React state", () => {
  const runtime = new ImmersiveRuntime("hub"); runtime.input.forward = 1; advance(runtime, 1);
  assert.equal(runtime.pose.z, world.landing.position[2]); runtime.markReady(0); assert.equal(runtime.getSnapshot().phase, "landing");
  runtime.enter(); advance(runtime, 7.3); assert.equal(runtime.getSnapshot().phase, "local"); assert.deepEqual(runtime.pose, spawnPose("hub"));
  let changes = 0; runtime.subscribe(() => changes++); runtime.input.strafe = 1; advance(runtime, 1);
  assert.ok(runtime.pose.x > 3.8); assert.equal(changes, 0);
});
test("physical threshold uses guided departure and never reveals before critical readiness", () => {
  const runtime = hub(); approach(runtime);
  assert.equal(runtime.getSnapshot().phase, "departure"); advance(runtime, 2);
  assert.equal(runtime.getSnapshot().scene, "aftermovie"); assert.equal(runtime.opacity, 1);
  advance(runtime, 12); assert.equal(runtime.getSnapshot().phase, "covered");
  runtime.markReady(0); advance(runtime, 1); assert.equal(runtime.getSnapshot().phase, "covered");
  runtime.markReady(runtime.getSnapshot().serial); advance(runtime, 1.3);
  assert.equal(runtime.getSnapshot().phase, "local"); assert.equal(runtime.opacity, 0);
  assert.deepEqual(runtime.pose, spawnPose("aftermovie"));
});
test("local movement is delta-aware, diagonal speed is bounded, and stage/backstage are inaccessible", () => {
  const a = hub(), b = hub(); a.input.strafe = b.input.strafe = 1;
  advance(a, 2, 30); advance(b, 2, 60); assert.ok(Math.abs(a.pose.x - b.pose.x) < 0.08);
  const runtime = new ImmersiveRuntime("aftermovie"); runtime.markReady(0); advance(runtime, 0.7);
  runtime.input.forward = 1; runtime.input.strafe = 1; advance(runtime, 30);
  assert.ok(boundaryClearance("aftermovie",runtime.pose)>=-.00001);
  assert.equal(runtime.getSnapshot().destinationMenu,true);
  assert.equal(runtime.getSnapshot().phase, "local");
});
test("route commitment preserves the current walking velocity without a stop or jump", () => {
  const runtime = hub(); runtime.input.forward = 1;
  runtime.input.lookX = -lookAtPose(world.hub.spawn,travelZones.find((z)=>z.id==="aftermovie")!.center).yaw;
  let previous = runtime.pose.z;
  for (let frame = 0; frame < 2400 && runtime.getSnapshot().phase === "local"; frame++) { previous = runtime.pose.z; runtime.tick(1 / 60); }
  assert.equal(runtime.getSnapshot().phase, "departure");
  const lastWalkStep = Math.abs(runtime.pose.z - previous); previous = runtime.pose.z;
  runtime.tick(1 / 60); const firstGuidedStep = Math.abs(runtime.pose.z - previous);
  assert.ok(firstGuidedStep > lastWalkStep * 0.5 && firstGuidedStep < lastWalkStep * 1.7);
});
test("direct URL skips introduction and an outer boundary waits for explicit covered return", () => {
  const arrivals: string[] = [];
  const runtime = new ImmersiveRuntime("aftermovie", (id, source) => arrivals.push(`${id}:${source}`));
  runtime.markReady(0); advance(runtime, 0.7); assert.deepEqual(arrivals, ["aftermovie:url"]);
  runtime.input.forward = -1; advance(runtime, 1.5);
  assert.equal(runtime.getSnapshot().destination, "aftermovie"); assert.equal(runtime.getSnapshot().destinationMenu,true);
  runtime.requestDestination("hub","physical");
  advance(runtime, 2); runtime.markReady(runtime.getSnapshot().serial); advance(runtime, 1.3);
  assert.equal(runtime.getSnapshot().scene, "hub"); assert.equal(arrivals[1], "hub:physical");
  assert.deepEqual(runtime.pose,spawnPose("hub"), "Explicit return restores the bounded local hub");
  runtime.setMap(true); runtime.request("aftermovie", "map"); assert.equal(runtime.getSnapshot().map, false);
  advance(runtime, 0.4); runtime.markReady(runtime.getSnapshot().serial); advance(runtime, 0.7);
  assert.equal(arrivals[2], "aftermovie:map");
  assert.equal(locationFromPath("/aftermovie"), "aftermovie"); assert.equal(locationFromPath("/events"), null);
});
test("superseding navigation invalidates old readiness; background restore cannot leap across routes", () => {
  const runtime = hub(); runtime.request("aftermovie", "map"); advance(runtime, 0.4);
  const old = runtime.getSnapshot().serial; runtime.request("hub", "url"); advance(runtime, 0.4);
  runtime.markReady(old); advance(runtime, 2); assert.equal(runtime.getSnapshot().phase, "covered");
  runtime.markReady(runtime.getSnapshot().serial); advance(runtime, 0.7);
  runtime.input.strafe = 1; runtime.suspended = true; const x = runtime.pose.x; advance(runtime, 5); assert.equal(runtime.pose.x, x);
  runtime.suspended = false; runtime.tick(20); assert.ok(runtime.pose.x - x < 0.22);
});
test("reduced motion preserves readiness gating and playback restores the visitor's pose", () => {
  const runtime = new ImmersiveRuntime("aftermovie"); runtime.reduced = true; runtime.markReady(0); advance(runtime, 0.3);
  runtime.input.strafe = 1; advance(runtime, 0.5); runtime.clearInput(); const pose = { ...runtime.pose };
  runtime.setMovie(true); advance(runtime, 1); assert.equal(runtime.pose.y, 5.9);
  runtime.setMovie(false); advance(runtime, 1); assert.deepEqual(runtime.pose, pose);
  runtime.request("hub", "map"); advance(runtime, 0.3); assert.equal(runtime.opacity, 1); assert.equal(runtime.getSnapshot().phase, "covered");
});
test("changing motion preferences publishes immediately without taking away local controls", () => {
  const runtime = hub(); const before = { ...runtime.pose }; const notifications: boolean[] = [];
  runtime.input.forward = 1;
  runtime.subscribe(() => notifications.push(runtime.getSnapshot().reduced));
  runtime.reduced = true;
  assert.deepEqual(notifications, [true]); assert.deepEqual(runtime.pose, before);
  assert.equal(runtime.getSnapshot().phase, "local"); assert.equal(runtime.input.forward, 1);
});

test("context restoration keeps the visitor's pose and rejects readiness from before loss", () => {
  const runtime = hub(); runtime.input.strafe = 1; advance(runtime, 0.5);
  const pose = { ...runtime.pose }, old = runtime.getSnapshot().serial;
  runtime.loseContext(); assert.equal(runtime.opacity, 1); assert.equal(runtime.input.strafe, 0);
  advance(runtime, 5); runtime.markReady(old); assert.equal(runtime.getSnapshot().phase, "context-lost");
  runtime.restoreContext(); runtime.markReady(old); assert.equal(runtime.getSnapshot().phase, "recovering");
  runtime.markReady(runtime.getSnapshot().serial); advance(runtime, 1);
  assert.equal(runtime.getSnapshot().phase, "local"); assert.equal(runtime.opacity, 0); assert.deepEqual(runtime.pose, pose);
});

test("context loss pauses entrance choreography and recovers initial preparation", () => {
  const runtime = new ImmersiveRuntime("hub"); runtime.loseContext(); runtime.restoreContext();
  runtime.markReady(runtime.getSnapshot().serial); assert.equal(runtime.getSnapshot().phase, "landing");
  runtime.enter(); advance(runtime, 3); const pose = { ...runtime.pose };
  runtime.loseContext(); advance(runtime, 10); runtime.restoreContext(); runtime.markReady(runtime.getSnapshot().serial);
  assert.deepEqual(runtime.pose, pose); advance(runtime, 4.3);
  assert.equal(runtime.getSnapshot().phase, "local"); assert.deepEqual(runtime.pose, spawnPose("hub"));
});

test("URL navigation during recovery supersedes the interrupted destination after preparation", () => {
  const runtime = hub(); runtime.request("aftermovie", "map"); advance(runtime, 0.4);
  runtime.loseContext(); runtime.request("hub", "url"); runtime.restoreContext();
  const serial = runtime.getSnapshot().serial; runtime.markReady(serial);
  assert.equal(runtime.getSnapshot().phase, "departure"); advance(runtime, 0.4);
  runtime.markReady(serial); assert.equal(runtime.getSnapshot().phase, "covered");
  runtime.markReady(runtime.getSnapshot().serial); advance(runtime, 0.7);
  assert.equal(runtime.getSnapshot().scene, "hub"); assert.equal(runtime.getSnapshot().phase, "local");
});

test("context loss exits film focus and returns to the saved walking pose", () => {
  const runtime = new ImmersiveRuntime("aftermovie"); runtime.markReady(0); advance(runtime, 0.7);
  runtime.input.strafe = 1; advance(runtime, 0.5); runtime.clearInput(); const pose = { ...runtime.pose };
  let stopped = false;
  runtime.movieActions = { play() {}, stop() { stopped = true; }, sound() {}, status: () => ({ phase: "playing", currentTime: 1, paused: false, muted: true }) };
  runtime.setMovie(true); advance(runtime, 1); runtime.loseContext();
  assert.equal(stopped, true); assert.equal(runtime.getSnapshot().movie, false);
  runtime.restoreContext(); runtime.markReady(runtime.getSnapshot().serial); advance(runtime, 1);
  assert.deepEqual(runtime.pose, pose); assert.equal(runtime.getSnapshot().phase, "local");
});

test("all six destinations and both stage aliases cross deliberately while unavailable sectors stay truthful", () => {
  for (const zone of travelZones) {
    const runtime=hub(),routes:{href:string;opacity:number;phase:string}[]=[];
    runtime.onCoveredRoute=(href)=>routes.push({href,opacity:runtime.opacity,phase:runtime.getSnapshot().phase});
    const direction=lookAtPose([runtime.pose.x,runtime.pose.y,runtime.pose.z],zone.center);
    runtime.input.lookX=runtime.pose.yaw-direction.yaw;runtime.input.forward=1;
    let frames=0;
    while(frames++<8*60 && runtime.getSnapshot().phase==="local" && !runtime.getSnapshot().unavailableDestination) runtime.tick(1/60);
    assert.ok(frames<8*60,zone.id+" must be nearby");
    if (zone.available) {
      assert.equal(runtime.getSnapshot().phase,"departure",zone.id);
      if (zone.id!=="aftermovie") {
        assert.deepEqual(routes,[],"Routing cannot start before coverage");advance(runtime,1);
        assert.deepEqual(routes,[{href:zone.href!,opacity:1,phase:"covered"}]);
        runtime.markReady(runtime.getSnapshot().serial);advance(runtime,2);
        assert.equal(runtime.getSnapshot().phase,"covered","External route stays covered until shell unmounts");
      }
    } else {
      assert.equal(runtime.getSnapshot().phase,"local");assert.equal(runtime.getSnapshot().unavailableDestination,zone.id);
      assert.equal(runtime.getSnapshot().destinationMenu,false,"No central hub destination menu");assert.deepEqual(routes,[]);
    }
  }
});
test("straight forward walking selects Main Stage and its right-hand Aftermovie alias selects the same scene", () => {
  assert.equal(travelZones.length,7,"Two stage aliases plus five other destination sectors");
  assert.equal(new Set(travelZones.map((zone)=>zone.id)).size,6);
  const primary=travelZones.find((zone)=>zone.sign==="main-stage")!;
  const side=travelZones.find((zone)=>zone.id==="aftermovie" && !zone.sign)!;
  assert.equal(primary.id,side.id);assert.equal(primary.edge,4);assert.equal(side.edge,3);
  const forward=hub();forward.input.forward=1;
  for(let frame=0;frame<5*60 && forward.getSnapshot().phase==="local";frame++) forward.tick(1/60);
  assert.equal(forward.getSnapshot().phase,"departure");assert.equal(forward.getSnapshot().destination,"aftermovie");
  assert.equal(forward.getSnapshot().unavailableDestination,null);
  const right=hub();approach(right);assert.equal(right.getSnapshot().destination,"aftermovie");assert.equal(right.getSnapshot().phase,"departure");
  assert.equal(crossedHubDestination([{edge:4,t:.72,outward:1}]),null,"Gap separates Main Stage and Accommodation");
});
test("collision stops capsules before every solid footprint and quarry wall", () => {
  for (const o of obstacles) {
    const p={x:o.x+.01,y:world.eyeHeight,z:o.z+.01,yaw:0,pitch:0}; constrainQuarry(p);
    assert.ok(Math.abs(p.x-o.x)>=o.halfX+world.playerRadius-.00001 || Math.abs(p.z-o.z)>=o.halfZ+world.playerRadius-.00001,o.id);
  }
  for (let i=0;i<world.quarry.boundary.length;i++) {
    if (i===0) continue; // This face contains the actual connected tunnel opening.
    const a=world.quarry.boundary[i],b=world.quarry.boundary[(i+1)%world.quarry.boundary.length];
    const dx=b[0]-a[0],dz=b[1]-a[1],length=Math.hypot(dx,dz),nx=dz/length,nz=-dx/length;
    const p={x:(a[0]+b[0])/2-nx*3,y:world.eyeHeight,z:(a[1]+b[1])/2-nz*3,yaw:0,pitch:0};constrainQuarry(p);
    assert.ok((p.x-a[0])*nx+(p.z-a[1])*nz>=world.playerRadius-.00001,"Wall face "+i);
  }
});
test("nearby hub commitment relocates to the distant stage only after black coverage", () => {
  const runtime=hub();approach(runtime);let previous={...runtime.pose},worst=0;
  while(runtime.getSnapshot().phase==="departure") {
    runtime.tick(1/60);
    if(runtime.opacity<1) worst=Math.max(worst,Math.hypot(runtime.pose.x-previous.x,runtime.pose.z-previous.z));
    else assert.equal(runtime.getSnapshot().phase,"covered");
    previous={...runtime.pose};
  }
  assert.ok(worst<.18,"Visible guided frames stay within a normal walking step budget");
  assert.deepEqual(runtime.pose,spawnPose("aftermovie",true));
});
test("stage, destination marker and film focus stay in the same authored coordinates", () => {
  assert.deepEqual(world.stage.origin,world.destinations.find((d)=>d.id==="stage")!.position);
  const runtime=new ImmersiveRuntime("aftermovie");runtime.markReady(0);advance(runtime,.7);
  runtime.setMovie(true);advance(runtime,1);
  assert.equal(runtime.pose.x,world.stage.origin[0]+world.stage.filmFocusLocal[0]);
  assert.equal(runtime.pose.z,world.stage.origin[2]+world.stage.filmFocusLocal[2]);
});
test("inspection cannot move a visitor and portrait framing preserves the original stage camera", () => {
  const runtime=hub(),saved={...runtime.pose};
  assert.equal(runtime.inspect("overview"),false,"Normal builds cannot activate an authoring camera");
  assert.ok(runtime.cameraPose(390/844).fov>world.camera.fov);
  runtime.inspectionEnabled=true;assert.equal(runtime.inspect("overview"),true);
  const overview=runtime.cameraPose(390/844);
  assert.ok(Math.abs(overview.yaw)<.00001);assert.equal(overview.pitch,-Math.PI/2);
  assert.ok(overview.y<320,"Revised overview removes excessive empty space");
  assert.ok(runtime.cameraPose(390/844).fov<=82);
  runtime.input.forward=1;advance(runtime,2);assert.deepEqual(runtime.pose,saved);
  runtime.inspect(null);assert.deepEqual(runtime.pose,saved);
  const stage=new ImmersiveRuntime("aftermovie");
  assert.equal(stage.cameraPose(390/844).fov,58,"Preserve original portrait stage composition and cost");
});
test("entrance choreography physically follows the bent tunnel without crossing rock", () => {
  const runtime=new ImmersiveRuntime("hub");runtime.markReady(0);runtime.enter();
  let previous={...runtime.pose},maximumStep=0;
  for(let i=0;i<7.3*60;i++) {
    runtime.tick(1/60);
    maximumStep=Math.max(maximumStep,Math.hypot(runtime.pose.x-previous.x,runtime.pose.z-previous.z));
    if(runtime.pose.z<=world.tunnel.startZ && runtime.pose.z>=world.tunnel.endZ) {
      assert.equal(runtime.pose.x,tunnelCenter(runtime.pose.z));
      assert.ok(Math.abs(runtime.pose.x-tunnelCenter(runtime.pose.z))<world.tunnel.walkHalfWidth);
    }
    assert.equal(runtime.pose.y,world.eyeHeight);previous={...runtime.pose};
  }
  assert.equal(runtime.getSnapshot().phase,"local");assert.deepEqual(runtime.pose,spawnPose("hub"));
  assert.ok(maximumStep<.35,"Connected choreography cannot jump between tunnel bends");
});
test("portal rock shoulders stop a visitor while the arch remains clear", () => {
  const blocked={x:8,y:world.eyeHeight,z:.2,yaw:0,pitch:0};constrainQuarry(blocked);
  assert.ok(blocked.z>=world.playerRadius);
  const doorway={x:0,y:world.eyeHeight,z:.2,yaw:0,pitch:0};constrainQuarry(doorway);
  assert.equal(doorway.z,.2);
});
test("side stepping into a tunnel wall slides locally instead of projecting into the quarry", () => {
  for (const z of [-1,-8,-22,-36,-41.8]) {
    const center=tunnelCenter(z),p={x:center+world.tunnel.walkHalfWidth+.06,y:world.eyeHeight,z,yaw:0,pitch:0};
    constrainQuarry(p);assert.equal(p.z,z);assert.equal(p.x,center+world.tunnel.walkHalfWidth);
  }
});
test("navigation away from playback stops media without snapping the visible film camera", () => {
  const runtime=new ImmersiveRuntime("aftermovie");runtime.markReady(0);advance(runtime,.7);
  let stopped=false;
  runtime.movieActions={play(){},stop(){stopped=true;},sound(){},status:()=>({phase:"playing",currentTime:1,paused:false,muted:true})};
  runtime.setMovie(true);advance(runtime,1);const view={...runtime.pose};
  runtime.request("hub","url");assert.equal(stopped,true);assert.deepEqual(runtime.pose,view);
  advance(runtime,.2);assert.deepEqual(runtime.pose,view);assert.ok(runtime.opacity>0);
  advance(runtime,.2);assert.equal(runtime.opacity,1);assert.equal(runtime.getSnapshot().phase,"covered");
});

test("every outer Aftermovie segment and chamfer opens a stationary menu without returning", () => {
  const polygon=movementBoundary("aftermovie");
  for(let edge=0;edge<polygon.length;edge++) {
    const runtime=new ImmersiveRuntime("aftermovie");runtime.markReady(0);advance(runtime,.7);
    const a=polygon[edge],b=polygon[(edge+1)%polygon.length],dx=b[0]-a[0],dz=b[1]-a[1],length=Math.hypot(dx,dz),nx=dz/length,nz=-dx/length;
    runtime.pose.x=(a[0]+b[0])/2+nx*.9;runtime.pose.z=(a[1]+b[1])/2+nz*.9;
    runtime.pose.yaw=Math.atan2(nx,nz);runtime.input.forward=1;advance(runtime,.6);
    assert.equal(runtime.getSnapshot().destinationMenu,true,"outer segment "+edge);
    assert.ok(boundaryClearance("aftermovie",runtime.pose)>=-.00001,"capsule stays inside segment "+edge);
    const stopped={...runtime.pose};runtime.input.forward=1;runtime.input.strafe=1;advance(runtime,3);
    assert.deepEqual(runtime.pose,stopped);assert.equal(runtime.getSnapshot().phase,"local");
    assert.equal(runtime.getSnapshot().scene,"aftermovie");assert.equal(runtime.getSnapshot().destination,"aftermovie");
  }
});
test("front/rear/side/corner and diagonal public movement open the boundary menu", () => {
  for(const [forward,strafe] of [[1,0],[-1,0],[0,1],[0,-1],[1,1],[1,-1],[-1,1],[-1,-1]]) {
    const runtime=new ImmersiveRuntime("aftermovie");runtime.markReady(0);advance(runtime,.7);
    runtime.input.forward=forward;runtime.input.strafe=strafe;advance(runtime,5);
    assert.equal(runtime.getSnapshot().destinationMenu,true,`direction ${forward}/${strafe}`);
    assert.ok(boundaryClearance("aftermovie",runtime.pose)>=-.00001);
  }
});
test("crossing the exact join of irregular perimeter segments clamps inside both faces", () => {
  const polygon=movementBoundary("aftermovie");
  const center=[world.stage.origin[0],(world.aftermovie.bounds[2]+world.aftermovie.bounds[3])/2];
  for(const vertex of polygon) {
    const runtime=new ImmersiveRuntime("aftermovie");runtime.markReady(0);advance(runtime,.7);
    const length=Math.hypot(vertex[0]-center[0],vertex[1]-center[1]);
    const dx=(vertex[0]-center[0])/length,dz=(vertex[1]-center[1])/length;
    runtime.pose.x=vertex[0]-dx*1.2;runtime.pose.z=vertex[1]-dz*1.2;
    runtime.pose.yaw=Math.atan2(-dx,-dz);runtime.input.forward=1;advance(runtime,.6);
    assert.equal(runtime.getSnapshot().destinationMenu,true);assert.ok(boundaryClearance("aftermovie",runtime.pose)>=-.00001);
  }
});
test("Stay Here preserves pose and requires moving away before another deliberate boundary crossing", () => {
  const runtime=new ImmersiveRuntime("aftermovie");runtime.markReady(0);advance(runtime,.7);
  runtime.input.forward=-1;advance(runtime,2);const stopped={...runtime.pose};
  runtime.dismissDestinationMenu();assert.deepEqual(runtime.pose,stopped);assert.equal(runtime.getSnapshot().destinationMenu,false);
  runtime.input.forward=-1;advance(runtime,2);assert.deepEqual(runtime.pose,stopped);assert.equal(runtime.getSnapshot().destinationMenu,false);
  runtime.clearInput();runtime.input.forward=1;advance(runtime,.5);runtime.clearInput();
  assert.ok(boundaryClearance("aftermovie",runtime.pose)>.65);
  runtime.input.forward=-1;advance(runtime,1);assert.equal(runtime.getSnapshot().destinationMenu,true);
});
test("looking at hub signs and sliding along a sector do not navigate", () => {
  const runtime=hub();
  for(const zone of travelZones) {
    runtime.input.lookX=runtime.pose.yaw-lookAtPose([runtime.pose.x,runtime.pose.y,runtime.pose.z],zone.center).yaw;
    runtime.tick(1/60);assert.equal(runtime.getSnapshot().phase,"local");assert.equal(runtime.getSnapshot().unavailableDestination,null);
  }
  assert.equal(crossedHubDestination([{edge:3,t:.5,outward:.2}]),null,"Tangential motion is not deliberate travel");
  assert.equal(crossedHubDestination([{edge:3,t:.95,outward:1}]),null,"Gap beside corner cannot choose a neighboring destination");
  assert.equal(crossedHubDestination([{edge:2,t:.54,outward:1}]),null,"Gap separates Contact and Sponsors");
});
test("internal movement does not open a perimeter menu and playback owns movement", () => {
  const runtime=new ImmersiveRuntime("aftermovie");runtime.markReady(0);advance(runtime,.7);
  runtime.input.strafe=1;advance(runtime,.3);runtime.clearInput();assert.equal(runtime.getSnapshot().destinationMenu,false);
  const before={x:runtime.pose.x,z:runtime.pose.z};assert.deepEqual(boundaryCrossings("aftermovie",before,{x:before.x+.05,z:before.z}),[]);
  runtime.setMovie(true);advance(runtime,1);const playing={...runtime.pose};
  runtime.input.forward=1;runtime.input.strafe=1;advance(runtime,5);
  assert.deepEqual(runtime.pose,playing);assert.equal(runtime.getSnapshot().destinationMenu,false);
});
test("Escape handles overlay first, map second, and playback exactly once", () => {
  const runtime=new ImmersiveRuntime("aftermovie");runtime.markReady(0);advance(runtime,.7);
  let stops=0;runtime.movieActions={play(){},stop(){stops++;runtime.setMovie(false);},sound(){},status:()=>({phase:"playing",currentTime:1,paused:false,muted:true})};
  runtime.input.forward=-1;advance(runtime,2);assert.equal(runtime.handleEscape(),true);assert.equal(stops,0);
  runtime.setMap(true);advance(runtime,1.5);assert.equal(runtime.handleEscape(),true);assert.equal(stops,0);advance(runtime,1.2);
  runtime.setMovie(true);advance(runtime,1);assert.equal(runtime.handleEscape(),true);assert.equal(stops,1);advance(runtime,1);
  assert.equal(runtime.handleEscape(),false);assert.equal(stops,1);
});
test("boundary overlay selections use readiness and external content routing under black", () => {
  for(const id of ["hub","entrance","events","team","contact"] as const) {
    const runtime=new ImmersiveRuntime("aftermovie");runtime.markReady(0);advance(runtime,.7);
    let routed:string|null=null;runtime.onCoveredRoute=(href)=>{assert.equal(runtime.opacity,1);assert.equal(runtime.getSnapshot().phase,"covered");routed=href;};
    runtime.input.forward=-1;advance(runtime,2);assert.equal(runtime.getSnapshot().destinationMenu,true);
    assert.equal(runtime.requestDestination(id,"map"),true);assert.equal(runtime.getSnapshot().destinationMenu,false);assert.equal(routed,null);
    advance(runtime,.4);assert.equal(runtime.opacity,1);assert.equal(runtime.getSnapshot().phase,"covered");
    runtime.markReady(runtime.getSnapshot().serial);advance(runtime,.8);
    if(id==="hub") {assert.deepEqual(runtime.pose,spawnPose("hub"));assert.equal(runtime.getSnapshot().phase,"local");}
    else if(id==="entrance") {assert.deepEqual(runtime.pose,landingPose());assert.equal(runtime.getSnapshot().phase,"landing");runtime.enter();advance(runtime,7.3);assert.equal(runtime.getSnapshot().phase,"local");}
    else {assert.equal(routed,destinationOptions.find((d)=>d.id===id)!.href);assert.equal(runtime.getSnapshot().phase,"covered");}
  }
});
test("map ascent/descent preserves exact player pose and does not publish on every frame", () => {
  const runtime=hub();runtime.input.strafe=1;advance(runtime,.3);runtime.clearInput();runtime.pose.yaw=.74;runtime.pose.pitch=.16;
  const saved={...runtime.pose},start=runtime.cameraPose(16/9);let notifications=0;runtime.subscribe(()=>notifications++);
  runtime.setMap(true);runtime.input.forward=1;advance(runtime,.45);
  assert.equal(runtime.getSnapshot().mapStage,"ascent");assert.ok(runtime.cameraPose(16/9).y>start.y+10);
  assert.deepEqual(runtime.pose,saved);assert.equal(notifications,1);
  advance(runtime,1);assert.equal(runtime.getSnapshot().mapStage,"open");assert.equal(runtime.mapProgress,1);
  assert.equal(runtime.cameraPose(16/9).pitch,-Math.PI/2);
  runtime.setMap(false);assert.equal(runtime.getSnapshot().map,true);advance(runtime,1.2);
  assert.equal(runtime.getSnapshot().map,false);assert.equal(runtime.getSnapshot().mapStage,null);assert.deepEqual(runtime.pose,saved);
  assert.deepEqual(runtime.cameraPose(16/9),start);assert.equal(notifications,4);
});
test("map close/open interruptions reverse continuously and reduced motion remains covered", () => {
  const runtime=hub(),saved={...runtime.pose};runtime.setMap(true);advance(runtime,.4);
  const camera=runtime.cameraPose(390/844);runtime.setMap(false);assert.deepEqual(runtime.cameraPose(390/844),camera);advance(runtime,.1);
  const closing=runtime.cameraPose(390/844);runtime.setMap(true);assert.deepEqual(runtime.cameraPose(390/844),closing);advance(runtime,1.4);
  runtime.setMap(false);advance(runtime,1.2);assert.deepEqual(runtime.pose,saved);
  runtime.reduced=true;runtime.setMap(true);advance(runtime,.2);assert.equal(runtime.getSnapshot().mapStage,"open");runtime.setMap(false);advance(runtime,.2);assert.equal(runtime.getSnapshot().map,false);
});
test("map marker travel fades the overhead view before changing the destination pose", () => {
  const runtime=hub();runtime.setMap(true);advance(runtime,1.5);const overhead=runtime.cameraPose(390/844);
  runtime.requestDestination("aftermovie","map");assert.deepEqual(runtime.cameraPose(390/844),overhead);
  advance(runtime,.2);assert.deepEqual(runtime.cameraPose(390/844),overhead);assert.ok(runtime.opacity>0 && runtime.opacity<1);
  advance(runtime,.2);assert.equal(runtime.opacity,1);assert.deepEqual(runtime.pose,spawnPose("aftermovie",true));
});
test("context loss during aerial transition restores the saved walking pose and input ownership", () => {
  const runtime=hub(),saved={...runtime.pose};runtime.setMap(true);advance(runtime,.5);runtime.loseContext();
  assert.equal(runtime.getSnapshot().map,false);assert.equal(runtime.mapProgress,0);assert.deepEqual(runtime.pose,saved);
  runtime.restoreContext();runtime.markReady(runtime.getSnapshot().serial);advance(runtime,.1);
  assert.equal(runtime.getSnapshot().phase,"local");assert.deepEqual(runtime.pose,saved);assert.equal(runtime.getSnapshot().map,false);
});
test("desktop and portrait map cameras fit the actual generated quarry rim and entrance", () => {
  const geometry=quarryGeometry(),vertices=geometry.getAttribute("position"),point=new Vector3();
  try {
    for(const aspect of [1366/768,390/844,844/390]) {
      const view=mapCamera(aspect),camera=new PerspectiveCamera(view.fov,aspect,world.camera.near,world.camera.far);
      camera.position.set(view.x,view.y,view.z);camera.quaternion.setFromEuler(new Euler(view.pitch,view.yaw,0,"YXZ"));camera.updateMatrixWorld();
      for(let i=0;i<vertices.count;i++) {
        point.fromBufferAttribute(vertices,i).project(camera);
        assert.ok(Math.abs(point.x)<1.015 && Math.abs(point.y)<1.015,`quarry vertex ${i} fits ${aspect}: ${point.x}/${point.y}`);
      }
      point.set(0,world.eyeHeight,world.landing.position[2]).project(camera);
      assert.ok(Math.abs(point.x)<1 && Math.abs(point.y)<1,"Entrance and tunnel stay in the same full-screen map");
    }
  } finally {geometry.dispose();}
});
test("actual cave geometry physically occludes the exit, scaffold and stage from landing and tunnel entry", () => {
  const geometries=[portalGeometry(),tunnelGeometry()],material=new MeshBasicMaterial({side:DoubleSide});
  const meshes=geometries.map((geometry)=>{const mesh=new Mesh(geometry,material);mesh.updateMatrixWorld();return mesh;});
  try {
    const landing=world.landing.position,near=world.cameras.find((camera)=>camera.id==="tunnel-near")!.position;
    const targets=[
      {label:"exit daylight",point:[0,2.4,world.tunnel.endZ]},
      {label:"navigation scaffold",point:[world.scaffold.position[0],6.3,world.scaffold.position[2]]},
      {label:"original stage",point:[world.stage.origin[0],5.9,world.stage.origin[2]+6]},
    ];
    for(const [label,position] of [["landing",landing],["near entrance",near]] as const) for(const target of targets) {
      const origin=new Vector3(position[0],position[1],position[2]),end=new Vector3(target.point[0],target.point[1],target.point[2]),distance=origin.distanceTo(end);
      const ray=new Raycaster(origin,end.sub(origin).normalize(),.01,distance-.05);
      const hits=ray.intersectObjects(meshes,false);
      assert.ok(hits.length>0,`${target.label} must be blocked by rendered rock from ${label}`);
      assert.ok(hits[0].distance<distance-.05,"The blocker lies before the target, not at the exit plane");
    }
  } finally {for(const geometry of geometries) geometry.dispose();material.dispose();}
});
test("actual bent-tunnel rock releases a clear exit sightline at the authored mid and first-reveal cameras", () => {
  const geometries=[portalGeometry(),tunnelGeometry()],material=new MeshBasicMaterial({side:DoubleSide});
  const meshes=geometries.map((geometry)=>{const mesh=new Mesh(geometry,material);mesh.updateMatrixWorld();return mesh;});
  try {
    for(const id of ["tunnel-mid","tunnel-first-exit-reveal"]) {
      const position=world.cameras.find((camera)=>camera.id===id)!.position;
      const origin=new Vector3(position[0],position[1],position[2]),end=new Vector3(0,2.4,world.tunnel.endZ),distance=origin.distanceTo(end);
      const ray=new Raycaster(origin,end.sub(origin).normalize(),.01,distance-.05);
      assert.equal(ray.intersectObjects(meshes,false).length,0,"Exit sightline remains clear from "+id);
    }
  } finally {for(const geometry of geometries) geometry.dispose();material.dispose();}
});
