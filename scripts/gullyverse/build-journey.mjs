import path from "node:path";
import fs from "node:fs/promises";
import { fileURLToPath } from "node:url";
import * as esbuild from "esbuild";
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),"../..");
const out=path.resolve(process.argv[2]??path.join(root,"public/models/gullyverse/locked-rev15z-m2a"));
await fs.mkdir(out,{recursive:true});
await fs.copyFile(path.join(root,"components/gullyverse-runtime/journey.html"),path.join(out,"index.html"));
await fs.copyFile(path.join(root,"components/gullyverse-runtime/journey.css"),path.join(out,"journey.css"));
await esbuild.build({entryPoints:[path.join(root,"components/gullyverse-runtime/journey-entry.tsx")],bundle:true,format:"esm",platform:"browser",outfile:path.join(out,"journey.js"),minify:true,define:{"process.env.NODE_ENV":'"production"'}});
// Reuse the already verified clean asset version, never rebake or mutate it.
const assets=path.join(out,"assets");
await fs.mkdir(assets,{recursive:true});
const clean=path.join(root,"public/models/gullyverse/locked-rev15z-clean-v2");
const manifest=JSON.parse(await fs.readFile(path.join(clean,"manifest.json"),"utf8"));
for(const name of ["manifest.json",...manifest.files.map(x=>x.file)]){
 const dest=path.join(assets,name);await fs.mkdir(path.dirname(dest),{recursive:true});await fs.copyFile(path.join(clean,name),dest);
}
const ground=path.join(root,"public/models/gullyverse/locked-rev15z-m2a-contact-ground");
const groundManifest=JSON.parse(await fs.readFile(path.join(ground,"manifest.json"),"utf8"));
for(const name of ["manifest.json",...groundManifest.files.map(x=>x.file)]){
 const dest=path.join(out,"ground",name);await fs.mkdir(path.dirname(dest),{recursive:true});await fs.copyFile(path.join(ground,name),dest);
}
// Both GLBs use the same pinned KTX2 transcoder, copied once per standalone URL base.
await fs.cp(path.join(assets,"transcoders"),path.join(out,"ground/transcoders"),{recursive:true});
console.log("JOURNEY_BUILD_PASS",out);
