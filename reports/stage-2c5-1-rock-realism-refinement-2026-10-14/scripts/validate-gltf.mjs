import{createRequire}from'node:module';import{readFile,writeFile,readdir}from'node:fs/promises';
const require=createRequire(import.meta.url),validator=require(process.env.GULLYVERSE_GLTF_VALIDATOR_MODULE||'/tmp/gullyverse-limestone-validator-20261012/node_modules/gltf-validator');
const dir='public/models/gullyverse/quarry-foundation-refined',rows=[];
for(const name of await readdir(dir)){if(!name.endsWith('.glb'))continue;
 const data=await readFile(dir+'/'+name),result=await validator.validateBytes(new Uint8Array(data),{uri:name});
 rows.push({file:name,bytes:data.length,result});console.log(name,result.issues.numErrors,'errors',result.issues.numWarnings,'warnings');
 if(result.issues.numErrors||result.issues.numWarnings)process.exitCode=1;
}
const shared=await readFile('public/models/gullyverse/quarry-foundation/foundation-materials.glb');
const sharedResult=await validator.validateBytes(new Uint8Array(shared),{uri:'foundation-materials.glb'});
rows.push({file:'../quarry-foundation/foundation-materials.glb',bytes:shared.length,retainedSharedSource:true,result:sharedResult});
if(sharedResult.issues.numErrors||sharedResult.issues.numWarnings)process.exitCode=1;
await writeFile('reports/stage-2c5-1-rock-realism-refinement-2026-10-14/raw/glTF-validator.json',JSON.stringify({validatorVersion:validator.version(),rows},null,2));
