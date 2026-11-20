/** Loopback-only, disposable PostgreSQL and actual existing Contact API handler. */
import fs from "node:fs/promises";
import path from "node:path";
import os from "node:os";
import { randomBytes } from "node:crypto";
import { createServer as createSocket } from "node:net";
import { createServer } from "node:http";
import { spawnSync } from "node:child_process";
// @ts-expect-error node16 exports are resolved by the existing tsx runner.
import EmbeddedPostgres from "embedded-postgres";
import { NextRequest } from "next/server";

async function main(){
  const root=path.resolve(process.argv[2]??"public/models/gullyverse/locked-rev15z-m2a"),port=Number(process.env.GULLYVERSE_PREVIEW_PORT??8897);
  const socket=createSocket();await new Promise<void>(r=>socket.listen(0,"127.0.0.1",r));const dbPort=(socket.address()as any).port;await new Promise<void>(r=>socket.close(()=>r()));
  const directory=await fs.mkdtemp(path.join(os.tmpdir(),"breeze-contact-journey-")),password=randomBytes(20).toString("hex");
  const db=new EmbeddedPostgres({databaseDir:directory,user:"postgres",password,port:dbPort,persistent:true,createPostgresUser:false,postgresFlags:["-h","127.0.0.1"],onLog:()=>{},onError:()=>{}});
  let prisma:typeof import("../../lib/prisma").prisma|undefined;
  let server:ReturnType<typeof createServer>|undefined;
  let stopping=false;
  const stop=async()=>{if(stopping)return;stopping=true;await new Promise<void>(r=>server?server.close(()=>r()):r());await prisma?.$disconnect();await db.stop();await fs.rm(directory,{recursive:true,force:true});};
  try{
    await db.initialise();await db.start();await db.createDatabase("breeze_runtime_tests_journey");
    process.env.DATABASE_URL=process.env.DIRECT_URL=`postgresql://postgres:${password}@127.0.0.1:${dbPort}/breeze_runtime_tests_journey`;
    process.env.NEXT_PUBLIC_SUPABASE_URL="http://127.0.0.1:9";process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY="isolated-anonymous-placeholder-no-live-access";
    for(const key of ["EMAIL_HOST","EMAIL_USERNAME","EMAIL_PASSWORD","SENDGRID_API_KEY","SUPABASE_SERVICE_ROLE_KEY"])delete process.env[key];
    const pushed=spawnSync(process.execPath,["node_modules/prisma/build/index.js","db","push","--skip-generate"],{env:process.env,encoding:"utf8"});if(pushed.status!==0)throw Error("Disposable schema setup failed");
    ({prisma}=await import("../../lib/prisma"));const {POST}=await import("../../app/api/contact/route");
    const types:Record<string,string>={".html":"text/html; charset=utf-8",".js":"text/javascript; charset=utf-8",".css":"text/css; charset=utf-8",".json":"application/json",".png":"image/png",".wasm":"application/wasm",".glb":"model/gltf-binary",".ktx2":"image/ktx2"};
    server=createServer(async(req,res)=>{
      try{
        const pathname=new URL(req.url??"/",`http://127.0.0.1:${port}`).pathname;
        if(pathname==="/api/preview-health"){res.setHeader("Content-Type","application/json");res.setHeader("Cache-Control","no-store");res.end(JSON.stringify({isolated:true}));return;}
        if(pathname==="/__test__/state"){res.setHeader("Content-Type","application/json");res.end(JSON.stringify({rows:await prisma!.contactSubmission.count()}));return;}
        if(pathname==="/api/contact"){
          if(req.method!=="POST"){res.writeHead(405);res.end();return;}
          const chunks:Buffer[]=[];let length=0;for await(const chunk of req){length+=chunk.length;if(length>8192){res.writeHead(413);res.end();return;}chunks.push(chunk);}
          const response=await POST(new NextRequest(`http://127.0.0.1:${port}/api/contact`,{method:"POST",headers:{"Content-Type":"application/json"},body:Buffer.concat(chunks).toString()}));
          res.writeHead(response.status,{"Content-Type":"application/json","Cache-Control":"no-store"});res.end(await response.text());return;
        }
        if(!["GET","HEAD"].includes(req.method??"")){res.writeHead(405);res.end();return;}
        const target=path.resolve(root,"."+decodeURIComponent(pathname==="/"?"/index.html":pathname));
        if(!target.startsWith(root+path.sep)){res.writeHead(403);res.end();return;}
        const data=await fs.readFile(target);res.writeHead(200,{"Content-Type":types[path.extname(target)]??"application/octet-stream","Cache-Control":"no-store"});res.end(req.method==="HEAD"?undefined:data);
      }catch(error:any){res.writeHead(error.code==="ENOENT"?404:500);res.end("Preview request failed");}
    });
    await new Promise<void>(r=>server!.listen(port,"127.0.0.1",r));
    console.log(JSON.stringify({status:"JOURNEY_SERVER_READY",url:`http://127.0.0.1:${port}/`,backend:"Actual Contact handler + disposable loopback PostgreSQL",messagesSentExternally:false}));
    for(const signal of ["SIGINT","SIGTERM"]as const)process.once(signal,()=>void stop().then(()=>process.exit(0)));
  }catch(error){await stop();throw error;}
}
void main().catch(error=>{console.error(String(error));process.exitCode=1;});
