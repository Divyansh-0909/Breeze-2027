import { NextResponse } from "next/server";
export function GET(){
  let isolated=false;
  try{
    const database=new URL(process.env.DATABASE_URL??"");
    isolated=process.env.GULLYVERSE_RUNTIME_PREVIEW==="1" && process.env.GULLYVERSE_ISOLATED_TEST_BACKEND==="1" &&
      ["localhost","127.0.0.1","[::1]"].includes(database.hostname) && database.pathname.startsWith("/breeze_runtime_tests");
  }catch{}
  return NextResponse.json({isolated},{headers:{"Cache-Control":"no-store"}});
}
