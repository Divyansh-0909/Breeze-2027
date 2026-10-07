"use client";

import { useEffect, useState } from "react";
import * as THREE from "three";

import { coordinators, groups, type Group, type Person } from "./teamData";

const TEXTURE_WIDTH = 2048;
const TEXTURE_HEIGHT = 1185;
const PAPER = "#eee2c8";
const INK = "#211d17";
const RED = "#a94434";
const GOLD = "#d2aa4b";

type LoadedImage = HTMLImageElement | null;

function font(size: number, weight = 700, family = "Satoshi") {
  return `${weight} ${size}px "${family}", Arial, sans-serif`;
}

function fittedFont(ctx: CanvasRenderingContext2D, text: string, maxWidth: number, start: number, min = 13) {
  let size = start;
  while (size > min) {
    ctx.font = font(size);
    if (ctx.measureText(text).width <= maxWidth) break;
    size -= 1;
  }
  return font(size);
}

function fillRoundedRect(ctx: CanvasRenderingContext2D, x: number, y: number, w: number, h: number, radius: number) {
  ctx.beginPath();
  ctx.roundRect(x, y, w, h, radius);
  ctx.fill();
}

function drawImageCover(ctx: CanvasRenderingContext2D, image: HTMLImageElement, x: number, y: number, w: number, h: number) {
  const scale = Math.max(w / image.naturalWidth, h / image.naturalHeight);
  const sw = w / scale;
  const sh = h / scale;
  const sx = (image.naturalWidth - sw) / 2;
  const sy = Math.max(0, (image.naturalHeight - sh) * 0.3);
  ctx.drawImage(image, sx, sy, sw, sh, x, y, w, h);
}

function initials(name: string) {
  return name.split(" ").filter(Boolean).map((word) => word[0]).join("").slice(0, 2).toUpperCase();
}

function drawPortrait(
  ctx: CanvasRenderingContext2D,
  person: Person,
  image: LoadedImage,
  x: number,
  y: number,
  w: number,
  h: number,
  featured = false,
) {
  ctx.save();
  ctx.shadowColor = "rgba(2, 7, 3, .48)";
  ctx.shadowBlur = featured ? 22 : 14;
  ctx.shadowOffsetY = featured ? 12 : 8;
  ctx.fillStyle = "#f0e7d5";
  fillRoundedRect(ctx, x, y, w, h, 5);
  ctx.shadowColor = "transparent";

  const pad = featured ? 14 : 10;
  const labelHeight = featured ? 64 : 52;
  const photoX = x + pad;
  const photoY = y + pad;
  const photoW = w - pad * 2;
  const photoH = h - labelHeight - pad * 1.5;

  ctx.fillStyle = "#8b8a7d";
  ctx.fillRect(photoX, photoY, photoW, photoH);
  if (image) {
    ctx.save();
    ctx.beginPath();
    ctx.rect(photoX, photoY, photoW, photoH);
    ctx.clip();
    drawImageCover(ctx, image, photoX, photoY, photoW, photoH);
    ctx.restore();
  } else {
    ctx.fillStyle = "#e7dfcc";
    ctx.font = font(featured ? 44 : 32, 400, "Aerosoldier");
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.fillText(initials(person.name), x + w / 2, photoY + photoH / 2);
  }

  ctx.fillStyle = "#ad392e";
  ctx.beginPath();
  ctx.arc(x + w / 2, y - 2, featured ? 7 : 5.5, 0, Math.PI * 2);
  ctx.fill();

  ctx.fillStyle = INK;
  ctx.textAlign = "center";
  ctx.textBaseline = "alphabetic";
  ctx.font = fittedFont(ctx, person.name.toUpperCase(), w - 16, featured ? 21 : 18, 12);
  ctx.fillText(person.name.toUpperCase(), x + w / 2, y + h - (featured ? 31 : 27));
  ctx.fillStyle = RED;
  ctx.font = fittedFont(ctx, person.role.toUpperCase(), w - 18, featured ? 14 : 12, 9);
  ctx.fillText(person.role.toUpperCase(), x + w / 2, y + h - (featured ? 13 : 11));
  ctx.restore();
}

function drawDepartment(
  ctx: CanvasRenderingContext2D,
  group: Group,
  images: Map<string, LoadedImage>,
  x: number,
  y: number,
  w: number,
  h: number,
) {
  const headerH = h < 300 ? 52 : 64;
  ctx.save();
  ctx.shadowColor = "rgba(7, 14, 8, .42)";
  ctx.shadowBlur = 10;
  ctx.shadowOffsetY = 5;
  ctx.fillStyle = PAPER;
  fillRoundedRect(ctx, x + 6, y, w - 12, headerH, 4);
  ctx.shadowColor = "transparent";
  ctx.fillStyle = RED;
  fillRoundedRect(ctx, x + 17, y + 11, 66, headerH - 22, 3);
  ctx.fillStyle = "#fff5e4";
  ctx.font = font(h < 300 ? 18 : 21);
  ctx.textAlign = "center";
  ctx.textBaseline = "middle";
  ctx.fillText(group.code, x + 50, y + headerH / 2 + 1);
  ctx.fillStyle = INK;
  ctx.textAlign = "left";
  ctx.font = fittedFont(ctx, group.name.toUpperCase(), w - 122, h < 300 ? 24 : 28, 17);
  ctx.fillText(group.name.toUpperCase(), x + 98, y + headerH / 2 + 2);

  const count = group.people.length;
  const gap = count === 3 ? 14 : 18;
  const maxCardW = count === 3 ? 142 : 168;
  const cardW = Math.min(maxCardW, (w - 34 - gap * (count - 1)) / count);
  const cardH = Math.min(h - headerH - 20, h < 300 ? 174 : 206);
  const rowW = cardW * count + gap * (count - 1);
  const startX = x + (w - rowW) / 2;
  const cardY = y + headerH + 13;
  group.people.forEach((person, index) => {
    drawPortrait(ctx, person, images.get(person.image) ?? null, startX + index * (cardW + gap), cardY, cardW, cardH);
  });
  ctx.restore();
}

function drawBoard(canvas: HTMLCanvasElement, images: Map<string, LoadedImage>) {
  const ctx = canvas.getContext("2d");
  if (!ctx) return;
  const { width: w, height: h } = canvas;

  const wash = ctx.createLinearGradient(0, 0, w, h);
  wash.addColorStop(0, "#263d2e");
  wash.addColorStop(0.48, "#4c674b");
  wash.addColorStop(1, "#203529");
  ctx.fillStyle = wash;
  ctx.fillRect(0, 0, w, h);

  for (let i = 0; i < 3100; i += 1) {
    const px = (i * 71.13) % w;
    const py = (i * 43.79) % h;
    ctx.fillStyle = i % 5 ? "rgba(3, 22, 13, .055)" : "rgba(227, 210, 151, .08)";
    ctx.beginPath();
    ctx.arc(px, py, 1 + (i % 3), 0, Math.PI * 2);
    ctx.fill();
  }

  const margin = 40;
  const gap = 18;
  const sideW = 548;
  const centerX = margin + sideW + gap;
  const centerW = w - margin * 2 - sideW * 2 - gap * 2;
  const rightX = centerX + centerW + gap;

  const leftH = (h - margin * 2 - gap * 2) / 3;
  groups.slice(0, 3).forEach((group, index) => {
    drawDepartment(ctx, group, images, margin, margin + index * (leftH + gap), sideW, leftH);
  });

  const rightH = (h - margin * 2 - gap * 3) / 4;
  groups.slice(3).forEach((group, index) => {
    drawDepartment(ctx, group, images, rightX, margin + index * (rightH + gap), sideW, rightH);
  });

  ctx.save();
  ctx.strokeStyle = "rgba(235, 222, 184, .20)";
  ctx.setLineDash([8, 12]);
  ctx.lineWidth = 2;
  ctx.beginPath();
  ctx.moveTo(centerX - 7, 44);
  ctx.lineTo(centerX - 7, h - 44);
  ctx.moveTo(centerX + centerW + 7, 44);
  ctx.lineTo(centerX + centerW + 7, h - 44);
  ctx.stroke();
  ctx.restore();

  const titleX = centerX + 36;
  const titleY = 58;
  const titleW = centerW - 72;
  const titleH = 280;
  ctx.save();
  ctx.shadowColor = "rgba(4, 10, 5, .48)";
  ctx.shadowBlur = 18;
  ctx.shadowOffsetY = 11;
  ctx.fillStyle = PAPER;
  fillRoundedRect(ctx, titleX, titleY, titleW, titleH, 6);
  ctx.shadowColor = "transparent";
  ctx.textAlign = "center";
  ctx.fillStyle = RED;
  ctx.font = font(17);
  ctx.letterSpacing = "4px";
  ctx.fillText("BREEZE '27 / FESTIVAL OFFICE", centerX + centerW / 2, titleY + 42);
  ctx.letterSpacing = "0px";
  ctx.fillStyle = INK;
  ctx.font = font(68, 400, "Aerosoldier");
  ctx.fillText("THE PEOPLE", centerX + centerW / 2, titleY + 115);
  ctx.fillStyle = RED;
  ctx.font = font(82, 400, "Aerosoldier");
  ctx.fillText("BEHIND BREEZE", centerX + centerW / 2, titleY + 195);
  ctx.strokeStyle = "rgba(32, 27, 21, .28)";
  ctx.beginPath();
  ctx.moveTo(titleX + 58, titleY + 220);
  ctx.lineTo(titleX + titleW - 58, titleY + 220);
  ctx.stroke();
  const total = coordinators.length + groups.reduce((count, group) => count + group.people.length, 0);
  ctx.fillStyle = "#645b4b";
  ctx.font = font(16);
  ctx.fillText(`${total} CREW  ·  07 TEAMS  ·  ONE VISION`, centerX + centerW / 2, titleY + 254);
  ctx.restore();

  ctx.fillStyle = RED;
  fillRoundedRect(ctx, centerX + centerW / 2 - 123, 370, 246, 54, 4);
  ctx.fillStyle = "#fff3e1";
  ctx.font = font(16);
  ctx.textAlign = "center";
  ctx.textBaseline = "middle";
  ctx.fillText("COORDINATORS", centerX + centerW / 2, 397);

  const coordGapX = 22;
  const coordGapY = 22;
  const coordCardW = (centerW - 92 - coordGapX) / 2;
  const coordCardH = 252;
  coordinators.forEach((person, index) => {
    const column = index % 2;
    const row = Math.floor(index / 2);
    drawPortrait(ctx, person, images.get(person.image) ?? null, centerX + 46 + column * (coordCardW + coordGapX), 456 + row * (coordCardH + coordGapY), coordCardW, coordCardH, true);
  });

  ctx.fillStyle = "#eee4cf";
  ctx.font = font(31, 400, "Aerosoldier");
  ctx.textAlign = "center";
  ctx.textBaseline = "alphabetic";
  ctx.fillText("MAKE IT LOUD. MAKE IT MATTER.", centerX + centerW / 2, 1060);

  ctx.save();
  ctx.translate(centerX + 118, 1098);
  ctx.rotate(-0.035);
  ctx.fillStyle = GOLD;
  fillRoundedRect(ctx, 0, 0, 250, 56, 3);
  ctx.fillStyle = "#292318";
  ctx.font = font(14);
  ctx.textAlign = "center";
  ctx.fillText("SHOW DAY / EVERY SECOND COUNTS", 125, 35);
  ctx.restore();

  const vignette = ctx.createRadialGradient(w / 2, h / 2, h * 0.16, w / 2, h / 2, h * 0.72);
  vignette.addColorStop(0, "rgba(0,0,0,0)");
  vignette.addColorStop(1, "rgba(2,8,4,.32)");
  ctx.fillStyle = vignette;
  ctx.fillRect(0, 0, w, h);
}

function loadImage(src: string): Promise<[string, LoadedImage]> {
  return new Promise((resolve) => {
    const image = new Image();
    image.decoding = "async";
    image.onload = () => resolve([src, image]);
    image.onerror = () => resolve([src, null]);
    image.src = src;
  });
}

export function useTeamBoardTexture() {
  const [texture, setTexture] = useState<THREE.CanvasTexture | null>(null);

  useEffect(() => {
    let active = true;
    const canvas = document.createElement("canvas");
    canvas.width = TEXTURE_WIDTH;
    canvas.height = TEXTURE_HEIGHT;
    const nextTexture = new THREE.CanvasTexture(canvas);
    nextTexture.colorSpace = THREE.SRGBColorSpace;
    nextTexture.anisotropy = 8;
    drawBoard(canvas, new Map());
    nextTexture.needsUpdate = true;
    setTexture(nextTexture);

    const people = [...coordinators, ...groups.flatMap((group) => group.people)];
    Promise.all([document.fonts.ready, Promise.all(people.map((person) => loadImage(person.image)))])
      .then(([, entries]) => {
        if (!active) return;
        drawBoard(canvas, new Map(entries));
        nextTexture.needsUpdate = true;
      })
      .catch(() => {
        // The fallback board is already usable if a font or portrait fails to load.
      });

    return () => {
      active = false;
      nextTexture.dispose();
    };
  }, []);

  return texture;
}
