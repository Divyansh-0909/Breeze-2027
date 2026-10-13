import{createRequire}from'node:module';import{readFile,writeFile}from'node:fs/promises';
const require=createRequire(import.meta.url),validator=require('/tmp/gullyverse-limestone-validator-20261012/node_modules/gltf-validator');
const file='public/models/gullyverse/rock-look-restore/rock-pilot-material.glb',data=await readFile(file);
const result=await validator.validateBytes(new Uint8Array(data),{uri:file});
await writeFile('reports/stage-2c4-rock-look-restore-2026-10-13/raw/glTF-validator.json',JSON.stringify({file,bytes:data.length,validatorVersion:validator.version(),result},null,2));
console.log(file,result.issues.numErrors,'errors',result.issues.numWarnings,'warnings');
if(result.issues.numErrors||result.issues.numWarnings)process.exitCode=1;
