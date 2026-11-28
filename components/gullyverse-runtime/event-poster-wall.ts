import type { Object3D } from "three";

/** Events shown per page of the events dialog (the wall itself shows up to six posters: zone-dressing.ts). */
export const eventsPerPage = 8;

/** The baked poster slots; Phase 3 hides them behind the weathered poster atlas (zone-dressing.ts). */
export const isEventPosterSlot = (object: Object3D) =>
  /^EVENTS clearly labelled placeholder ([0-7])$/.test(object.userData.sourceObjectName ?? "");
