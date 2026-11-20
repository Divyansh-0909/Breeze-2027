async function download(tools,notify,row){
 const q=s=>"'"+s.replaceAll("'","'\\''")+"'",R='/workspace/Breeze-2027/reports/streetlights-rev15w-overhead-cables-2026-11-14',dest=R+'/restore/downloads/'+row.file;
 let m=await tools.mcp__codex_apps__google_drive_get_file_metadata({fileId:row.id,fields:'id,name,size,mimeType,parents,permissions'});m=m.structuredContent??m;if(Number(m.size)!==row.bytes||m.permissions.find(x=>x.role==='owner')?.emailAddress!=='losersamurai09@gmail.com')throw Error('Restore input metadata mismatch: '+row.file);
 const exists=await tools.exec_command({cmd:'test -f '+q(dest),max_output_tokens:100});let local;
 if(exists.exit_code!==0){let f=await tools.mcp__codex_apps__google_drive_fetch({url:row.url,download_raw_file:true,include_base64:false});f=f.structuredContent??f;local=await tools.download_file({file_id:f.file_uri.file_id.replace('sediment://','')});}
 const p=await tools.exec_command({cmd:'python '+q(R+'/source/verify-download.py')+' '+q(JSON.stringify({...row,verifiedOwner:'losersamurai09@gmail.com',verifiedParent:m.parent_ids}))+(local?' '+q(local.path):''),max_output_tokens:300});if(p.exit_code!==0)throw Error(p.output);notify({kind:row.kind,file:row.file,status:'VERIFIED'});return row;
}
