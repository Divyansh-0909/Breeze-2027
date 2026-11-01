const upload = async (item) => {
 const O=load("worldO"), folders=load("worldFolders"), parent=folders[item.folder||"checkpoint"].id;
 const prior=(load("worldUploads")||[]).find(x=>x.name===item.name);
 if(prior){if(prior.sha256!==item.sha256)throw Error("Previously uploaded differing file");return prior;}
 const mime=item.name.endsWith(".zip")?"application/zip":item.name.endsWith(".pdf")?"application/pdf":item.name.endsWith(".mp4")?"video/mp4":item.name.endsWith(".png")?"image/png":item.name.endsWith(".json")?"application/json":item.name.endsWith(".blend")?"application/octet-stream":"text/markdown";
 const response=await tools.mcp__codex_apps__google_drive_upload_file({file_name:item.name,file_uri:item.path,mime_type:mime,parent_folder_id:parent});
 const u=response.structuredContent;if(response.isError||!u?.id)throw Error("Upload failed");
 const m=(await tools.mcp__codex_apps__google_drive_get_file_metadata({fileId:u.id,fields:"id,name,size,parents,webViewLink"})).structuredContent;
 if(Number(m.size)!==item.bytes||!m.parent_ids?.includes(parent))throw Error("Remote metadata mismatch");
 const raw=(await tools.mcp__codex_apps__google_drive_fetch({url:u.url,download_raw_file:true,include_base64:false})).structuredContent;
 const receipt=O+"/checkpoint/verified-"+u.id+".json";
 await tools.write_stdin({session_id:load("worldWorker"),chars:JSON.stringify({url:raw.file_uri.download_url,id:u.id,name:item.name,bytes:item.bytes,sha256:item.sha256,receipt})+"\n",yield_time_ms:1000,max_output_tokens:1000});
 let verified=false;for(let n=0;n<35;n++){const c=await tools.exec_command({cmd:"cat '"+receipt+"'",max_output_tokens:500});if(c.exit_code===0){if(!JSON.parse(c.output).verified)throw Error("Hash verification failed");verified=true;break;}await tools.write_stdin({session_id:load("worldWorker"),chars:"",yield_time_ms:1000,max_output_tokens:1000});}
 if(!verified)throw Error("Download verification timed out");
 const rec={...item,id:u.id,url:u.url,parent,fullAuthenticatedDownloadBackVerified:true};
 store("worldUploads",[...(load("worldUploads")||[]),rec]);
 await tools.apply_patch("*** Begin Patch\n*** Add File: "+O+"/checkpoint/uploaded-"+u.id+".json\n+"+JSON.stringify(rec,null,2).replace(/\n/g,"\n+")+"\n*** End Patch");
 notify({uploadedAndVerified:item.name,id:u.id,bytes:item.bytes});return rec;
};
