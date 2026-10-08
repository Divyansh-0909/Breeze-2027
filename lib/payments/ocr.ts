import path from "node:path";
import { mkdir } from "node:fs/promises";

export async function receiptText(data: Buffer) {
  const sharp = (await import("sharp")).default;
  const info = await sharp(data, { limitInputPixels: 16000000 }).metadata();
  if (!info.width || !info.height || info.width * info.height > 16000000) throw new Error("Receipt image dimensions are too large.");
  const cachePath = process.env.PAYMENT_OCR_CACHE || path.join(process.cwd(), ".payment-ocr-cache");
  await mkdir(cachePath, { recursive: true });
  const { createWorker } = await import("tesseract.js");
  const worker = await createWorker("eng", 1, { cachePath });
  let timer: ReturnType<typeof setTimeout>, terminated = false;
  try {
    const result = await Promise.race([
      worker.recognize(data),
      new Promise<never>((_, reject) => { timer = setTimeout(() => { terminated = true; void worker.terminate().catch(() => {}); reject(new Error("Receipt reading timed out. Submit the image for team review.")); }, 30000); }),
    ]);
    return result.data.text;
  } finally { clearTimeout(timer); if (!terminated) await worker.terminate(); }
}
