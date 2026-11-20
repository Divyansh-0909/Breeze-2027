"""Seal the adjoining native Contact ground chunk, using the shared GLB serializer."""
from pathlib import Path
import sys,json,struct,hashlib
out=Path(sys.argv[1]);m=json.loads((out/'manifest.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
names=['contact-frontage.png.glb','contact-frontage.optimized.glb','contact-frontage.mobile.glb','lightmap.hdr','lightmap.ktx2','walkable-space.json']
config=Path(__file__).resolve().parents[2]/'components/gullyverse-runtime/contact-space.json';(out/'walkable-space.json').write_bytes(config.read_bytes())
m['chunk']='contact-approach-ground';m['chunks']=[{'id':'contact-approach-ground','status':'M2A adjoining native source ground; other world chunks remain pending'}];m['files']=[{'file':name,'bytes':(out/name).stat().st_size,'sha256':sha(out/name)}for name in names]
raw=(out/'contact-frontage.png.glb').read_bytes();n=struct.unpack_from('<I',raw,12)[0];g=json.loads(raw[20:20+n]);m['counts'].update(pbrTextureImages=len(g['images']),uniqueMaterials=len(g['materials']),externalLightmapImages=1,standaloneGraffitiHeadings=0)
m['sourceBakedDerivative']={'file':'contact-frontage-baked.blend','bytes':(out/'contact-frontage-baked.blend').stat().st_size,'sha256':sha(out/'contact-frontage-baked.blend')}
m['validation']={'uv':'uv-roundtrip-verification.json','rgbm':'rgbm-verification.json','sourceAccounting':'validation/runtime-validation.json','preservation':'Original source-face geometry and earlier UVs; procedural PBR converted with original Generated coordinates','scope':'Bounded native Contact approach, not the complete cypher ground'}
m['collision']={'uri':'walkable-space.json','role':'Native planar capsule bounds; floor height 7.2, original radius and eye height; browser floor probes required'}
(out/'manifest.json').write_text(json.dumps(m,indent=2)+'\n');print('GROUND_MANIFEST_PASS',m['counts'])
