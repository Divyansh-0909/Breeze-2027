import { NextResponse } from "next/server";
import fs from "node:fs/promises";
import path from "node:path";

/**
 * Dev-only frame sink for the flythrough recorder (`/flythrough-rec`).
 *
 * That page renders the stage scene frame by frame and POSTs each frame here
 * as a PNG data-URL; the frames land in `.rec-frames/` at the repo root and
 * ffmpeg assembles them into the travel video afterwards. Frame-by-frame via
 * HTTP instead of an in-page MediaRecorder because MediaRecorder captures in
 * real time — on a software-rendered headless browser the scene runs at a
 * crawl and the recording would be a slideshow, where deterministic
 * frame-stepping is immune to render speed.
 *
 * Hard-disabled outside development: it writes to disk on request.
 */
const DIR = path.join(process.cwd(), ".rec-frames");

export async function POST(req: Request): Promise<NextResponse> {
  if (process.env.NODE_ENV === "production") {
    return new NextResponse(null, { status: 404 });
  }

  const body = (await req.json()) as { i?: number; data?: string; done?: boolean };
  await fs.mkdir(DIR, { recursive: true });

  if (body.done) {
    await fs.writeFile(path.join(DIR, "done.txt"), "1");
    return NextResponse.json({ ok: true });
  }

  const b64 = String(body.data ?? "").split(",")[1];
  if (!b64 || typeof body.i !== "number") {
    return NextResponse.json({ ok: false }, { status: 400 });
  }
  await fs.writeFile(
    path.join(DIR, `frame_${String(body.i).padStart(4, "0")}.png`),
    Buffer.from(b64, "base64")
  );
  return NextResponse.json({ ok: true });
}
