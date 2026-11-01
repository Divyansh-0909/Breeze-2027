async function uploadRev10(item){
 const O=load("rev10O"),folders=load("rev10Folders"),parent=folders[item.folder||"checkpoint"];
 const prior=(load("rev10Uploads")||[]).find(x=>x.name===item.name);
 if(prior){if(prior.sha256!==item.sha256)throw Error("Conflicting prior upload");return prior;}
 const mime=item.name.endsWith(".zip")?"application/zip":item.name.endsWith(".pdf")?"application/pdf":item.name.endsWith(".mp4")?"video/mp4":item.name.endsWith(".png")?"image/png":item.name.endsWith(".json")?"application/json":item.name.endsWith(".blend")?"application/octet-stream":"text/markdown";
 const rr=await tools.mcp__codex_apps__google_drive_upload_file({file_name:item.name,file_uri:item.path,mime_type:mime,parent_folder_id:parent});const u=rr.structuredContent;
 if(rr.isError||!u?.id)throw Error("Upload failed");
 const m=(await tools.mcp__codex_apps__google_drive_get_file_metadata({fileId:u.id,fields:"id,name,size,parents,webViewLink,mimeType"})).structuredContent;
 if(Number(m.size)!==item.bytes||!m.parent_ids?.includes(parent)||m.title!==item.name)throw Error("Metadata mismatch");
 const raw=(await tools.mcp__codex_apps__google_drive_fetch({url:u.url,download_raw_file:true,include_base64:false})).structuredContent;
 const receipt=O+"/checkpoint/verified-"+u.id+".json";
 await tools.write_stdin({session_id:load("rev10Worker"),chars:JSON.stringify({url:raw.file_uri.download_url,id:u.id,name:item.name,bytes:item.bytes,sha256:item.sha256,receipt,...(item.save?{save:item.save}:{})})+"\n",yield_time_ms:1000,max_output_tokens:500});
 let verified=false;for(let n=0;n<40;n++){const r=await tools.exec_command({cmd:"cat '"+receipt+"'",max_output_tokens:500});if(r.exit_code===0){if(!JSON.parse(r.output).verified)throw Error("Hash mismatch");verified=true;break;}await tools.write_stdin({session_id:load("rev10Worker"),chars:"",yield_time_ms:1000,max_output_tokens:500});}
 if(!verified)throw Error("Verification timeout");
 const rec={...item,id:u.id,url:u.url,parent,fullAuthenticatedDownloadBackVerified:true};
 store("rev10Uploads",[...(load("rev10Uploads")||[]),rec]);
 await tools.apply_patch("*** Begin Patch\n*** Add File: "+O+"/checkpoint/uploaded-"+u.id+".json\n+"+JSON.stringify(rec,null,2).replace(/\n/g,"\n+")+"\n*** End Patch");
 notify({uploadedAndVerified:item.name,id:u.id,bytes:item.bytes});return rec;
};
