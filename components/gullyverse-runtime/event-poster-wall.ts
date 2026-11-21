import { CanvasTexture, Mesh, MeshStandardMaterial, SRGBColorSpace, type Object3D } from "three";
import type { CypherEvent } from "../../lib/events/cypher-catalog";

export const eventsPerPage = 8;
const centralSlots = [1, 2, 0, 3, 5, 6, 4, 7];

export function eventPosterSlots(scene: Object3D) {
  const slots: (Mesh | undefined)[] = Array(eventsPerPage).fill(undefined);
  scene.traverse(object => {
    const match = /^EVENTS clearly labelled placeholder ([0-7])$/.exec(object.userData.sourceObjectName ?? "");
    if (object instanceof Mesh && match) slots[Number(match[1])] = object;
  });
  return slots;
}

export function paintEventPage(slots: ReturnType<typeof eventPosterSlots>, events: readonly CypherEvent[]) {
  const bySlot = new Map(centralSlots.slice(0, events.length).sort((a, b) => a - b)
    .map((slot, index) => [slot, events[index]]));
  const undo: (() => void)[] = [];
  slots.forEach((slot, index) => {
    if (!slot) return;
    const event = bySlot.get(index);
    const visible = slot.visible;
    slot.visible = !!event;
    undo.push(() => { slot.visible = visible; });
    if (!event || !(slot.material instanceof MeshStandardMaterial)) return;

    const canvas = document.createElement("canvas");
    canvas.width = 384;
    canvas.height = 512;
    const ink = canvas.getContext("2d");
    if (!ink) return;
    const original = slot.material;
    const texture = new CanvasTexture(canvas);
    texture.colorSpace = SRGBColorSpace;
    texture.flipY = false;
    const material = original.clone();
    material.onBeforeCompile = original.onBeforeCompile;
    material.customProgramCacheKey = original.customProgramCacheKey;
    material.map = texture;
    if (original.emissiveMap) material.emissiveMap = texture;
    material.color.set(0xffffff);
    slot.material = material;
    slot.userData.wallEventId = event.id;

    const draw = (image?: HTMLImageElement) => {
      ink.fillStyle = "#f0dfb6";
      ink.fillRect(0, 0, canvas.width, canvas.height);
      ink.fillStyle = "#24221c";
      ink.fillRect(9, 9, 366, 494);
      if (image) {
        const scale = Math.min(366 / image.naturalWidth, 494 / image.naturalHeight);
        const width = image.naturalWidth * scale, height = image.naturalHeight * scale;
        ink.drawImage(image, (384 - width) / 2, (512 - height) / 2, width, height);
      } else {
        ink.fillStyle = "#f0dfb6";
        ink.textAlign = "center";
        ink.font = "bold 36px sans-serif";
        ink.fillText(event.event_name, 192, 230, 320);
        ink.font = "23px sans-serif";
        ink.fillText(event.event_date ?? "Date to be announced", 192, 284, 320);
        ink.fillText(event.event_org ?? "Breeze 2027", 192, 322, 320);
      }
      texture.needsUpdate = true;
    };
    draw();
    let image: HTMLImageElement | undefined;
    if (event.image_url && /^(?:https:\/\/|\/(?![/\\]))/i.test(event.image_url)) {
      image = new Image();
      image.crossOrigin = "anonymous";
      image.onload = () => {
        if (image?.naturalWidth && image.naturalHeight) draw(image);
      };
      image.src = event.image_url;
    }
    undo.push(() => {
      if (image) { image.onload = null; image.removeAttribute("src"); }
      delete slot.userData.wallEventId;
      slot.material = original;
      material.dispose();
      texture.dispose();
    });
  });
  return () => undo.forEach(reset => reset());
}
