import {readFile,writeFile} from 'node:fs/promises';
import {chromium} from 'playwright';
import path from 'node:path';
const R='reports/canal-material-study-2026-10-23';
const md=await readFile('docs/gullyverse-stage-3a-dried-canal-material-study.md','utf8');
const escape=s=>s.replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;');
const inline=s=>escape(s).replace(/\[([^\]]+)\]\(([^)]+)\)/g,'<a href="$2">$1</a>').replace(/`([^`]+)`/g,'<code>$1</code>').replace(/\*\*([^*]+)\*\*/g,'<b>$1</b>');
let html='',table=false;
for(const line of md.split('\n')){
 if(line.startsWith('|')){if(!table){html+='<table>';table=true;}if(/^\|[-:| ]+\|$/.test(line))continue;html+='<tr>'+line.split('|').slice(1,-1).map(c=>'<td>'+inline(c.trim())+'</td>').join('')+'</tr>';continue;}
 if(table){html+='</table>';table=false;}
 if(line.startsWith('# '))html+='<h1>'+inline(line.slice(2))+'</h1>';else if(line.startsWith('## '))html+='<h2>'+inline(line.slice(3))+'</h2>';else if(line.trim())html+='<p>'+inline(line)+'</p>';
}
const full='<!doctype html><meta charset="utf-8"><title>Gullyverse canal technical report</title><style>@page{size:A4;margin:17mm 14mm}body{font:10.5pt/1.48 Arial;color:#1b2924}h1{font-size:23pt}h2{font-size:15pt;margin-top:22px;break-after:avoid}p{overflow-wrap:anywhere}a{color:#155b46}code{font:9pt monospace}table{width:100%;border-collapse:collapse;font-size:8pt;margin:14px 0}td{border-bottom:1px solid #ccc;padding:5px;overflow-wrap:anywhere;vertical-align:top}tr:first-child{font-weight:bold;background:#eee}tr{break-inside:avoid}</style>'+html;
await writeFile(R+'/review/technical-report.html',full);const browser=await chromium.launch({executablePath:'/usr/bin/chromium',headless:true});try{const p=await browser.newPage();await p.setContent(full,{waitUntil:'load'});await p.pdf({path:R+'/review/Gullyverse-Dried-Canal-Technical-Report.pdf',format:'A4',printBackground:true,displayHeaderFooter:true,headerTemplate:'<span></span>',footerTemplate:'<div style="width:100%;text-align:center;font-size:8px;color:#444">PRIVATE MATERIAL STUDY · <span class="pageNumber"></span> / <span class="totalPages"></span></div>'});}finally{await browser.close();}
