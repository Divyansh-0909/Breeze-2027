"use client";

import { useRef, useState } from "react";
import { GullyAudio, music, previewLayers, type PreviewLayer } from "@/components/gullyverse-runtime/gully-audio";

const seconds = 8;

/** 16-bit stereo WAV, optionally normalised to -3 dBFS peak so quiet layers can be judged by ear. */
function wav(buffer: AudioBuffer, normalise: boolean): Blob {
  const channels = [buffer.getChannelData(0), buffer.getChannelData(buffer.numberOfChannels > 1 ? 1 : 0)];
  let peak = 0;
  for (const channel of channels) for (const v of channel) peak = Math.max(peak, Math.abs(v));
  const scale = normalise && peak > 0 ? 0.708 / peak : 1;
  const frames = buffer.length, out = new DataView(new ArrayBuffer(44 + frames * 4));
  const text = (offset: number, value: string) => [...value].forEach((c, i) => out.setUint8(offset + i, c.charCodeAt(0)));
  text(0, "RIFF"); out.setUint32(4, 36 + frames * 4, true); text(8, "WAVE"); text(12, "fmt ");
  out.setUint32(16, 16, true); out.setUint16(20, 1, true); out.setUint16(22, 2, true);
  out.setUint32(24, buffer.sampleRate, true); out.setUint32(28, buffer.sampleRate * 4, true);
  out.setUint16(32, 4, true); out.setUint16(34, 16, true); text(36, "data"); out.setUint32(40, frames * 4, true);
  for (let i = 0; i < frames; i++) for (let c = 0; c < 2; c++) {
    const v = Math.max(-1, Math.min(1, channels[c][i] * scale));
    out.setInt16(44 + (i * 2 + c) * 2, v * 0x7fff, true);
  }
  return new Blob([out.buffer], { type: "audio/wav" });
}

const peakDb = (buffer: AudioBuffer) => {
  let peak = 0;
  for (let c = 0; c < buffer.numberOfChannels; c++) for (const v of buffer.getChannelData(c)) peak = Math.max(peak, Math.abs(v));
  return peak > 0 ? 20 * Math.log10(peak) : -Infinity;
};

let track: Promise<ArrayBuffer> | null = null;

async function render(layer: PreviewLayer, normalise: boolean) {
  const needsMusic = layer === "shop-radio" || layer === "plaza-stage";
  if (needsMusic) track ??= fetch(music).then(response => response.arrayBuffer());
  const buffer = await GullyAudio.renderLayer(layer, seconds, needsMusic ? await track! : undefined);
  return { blob: wav(buffer, normalise), peakDb: peakDb(buffer) };
}

declare global {
  interface Window { renderGullySound?: (layer: PreviewLayer, normalise: boolean) => Promise<{ wav: string; peakDb: number }> }
}

if (typeof window !== "undefined") {
  window.renderGullySound = async (layer, normalise) => {
    const { blob, peakDb } = await render(layer, normalise);
    const bytes = new Uint8Array(await blob.arrayBuffer());
    let binary = "";
    for (let i = 0; i < bytes.length; i += 0x8000) binary += String.fromCharCode(...bytes.subarray(i, i + 0x8000));
    return { wav: btoa(binary), peakDb };
  };
}

export default function SoundBoard() {
  const [urls, setUrls] = useState<Partial<Record<PreviewLayer, { url: string; peakDb: number }>>>({});
  const [normalise, setNormalise] = useState(true);
  const busy = useRef(new Set<PreviewLayer>());

  const play = async (layer: PreviewLayer) => {
    if (busy.current.has(layer)) return;
    busy.current.add(layer);
    const { blob, peakDb } = await render(layer, normalise);
    busy.current.delete(layer);
    setUrls(current => ({ ...current, [layer]: { url: URL.createObjectURL(blob), peakDb } }));
  };

  return (
    <main style={{ maxWidth: 720, margin: "40px auto", padding: 20, font: "15px/1.5 ui-sans-serif, system-ui", color: "#eee", background: "#111" }}>
      <h1>Gully sounds</h1>
      <p>Each layer the site plays, rendered on its own by the site&apos;s audio code ({seconds} s, without 3D placement).</p>
      <label><input type="checkbox" checked={normalise} onChange={event => setNormalise(event.target.checked)} /> Make quiet layers loud enough to judge (normalise to −3 dB)</label>
      <ol>
        {(Object.keys(previewLayers) as PreviewLayer[]).map(layer => (
          <li key={layer} style={{ margin: "14px 0" }}>
            <strong>{previewLayers[layer]}</strong>{" "}
            <button type="button" onClick={() => void play(layer)}>Render</button>
            {urls[layer] && <>
              <span style={{ opacity: .7 }}> site peak {urls[layer]!.peakDb.toFixed(1)} dBFS</span>
              <br /><audio controls autoPlay src={urls[layer]!.url} />
            </>}
          </li>
        ))}
      </ol>
    </main>
  );
}
