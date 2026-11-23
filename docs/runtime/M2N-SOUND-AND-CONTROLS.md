# M2N Sound, walking feel and controls

## Controls

The walking controls sit bottom-left in a **CONTROLS** panel. Keys show as chips with a dark grey fill and a light white outline, in the style of the shadcn `Kbd` component, next to spaced uppercase labels:

| Key | Action |
|---|---|
| W A S D (or arrows) | Walk (2.4 m/s) |
| Shift (hold) | Sprint (4.2 m/s) |
| Drag | Look |
| E | The nearby destination's action (Leave a message, View team murals, Watch Aftermovie, View accommodation, Browse event posters), only when one is in reach |
| M | Map / Close map |
| V | Sound on / off (remembered) |
| Esc | Leave a focused view or the map |

Every row with an action is also a button. The current place shows as the same chip top-left (hidden while the map is open). On phones and touch screens the keyboard-only rows are hidden and the movement pad sits bottom-right. The map uses the same chips for every stop and for the hint (`M` / `Esc`).

## Walking feel

Walking moves at 2.4 m/s and holding Shift sprints at 4.2 m/s, the former single pace. A stride clock driven by distance walked sets the rhythm: about 1.25 m and 1.9 footfalls a second when walking, 1.45 m and 2.9 a second when sprinting. The head bob follows it: sprinting moves the camera about 2 cm vertically and 1 cm sideways with a quarter-degree roll, and walking under half of that. The lowest point is at each footfall, and the motion settles when you stop. It is off in focused views, on the map, in review captures, and when the visitor prefers reduced motion. A random camera shake is deliberately not used, because it causes motion sickness. Earlier scenes keep their single 4.2 m/s pace (`ImmersiveRuntime.pace`).

## Sound

The soundscape is described in [M2O sound design](M2O-SOUND-DESIGN.md). The continuous traffic-and-hiss bed and the plaza crowd murmur were removed. Browsers allow audio only after a user gesture, so the context starts on the first click, tap or key press. It suspends when the tab is hidden. `V` and the Sound row toggle it, and the choice is stored in `localStorage` (`breeze:sound`).

## Listening to each layer

`/runtime-preview/sounds` (private; needs `GULLYVERSE_RUNTIME_PREVIEW=1`) renders every layer on its own through the same `GullyAudio` code, offline, as a 10-second clip heard from a listening spot in the gully (with placement, distance filtering and reverb). It shows each layer's real peak level, and it can normalise quiet layers to −3 dB so they can be judged by ear. `window.renderGullySound(layer, normalise)` returns the clip as a base64 WAV for scripted capture.
