# M2N Sound, walking feel and controls

## Controls

The walking controls sit bottom-left in a **CONTROLS** panel. Keys show as chips with a dark grey fill and a light white outline, in the style of the shadcn `Kbd` component, next to spaced uppercase labels:

| Key | Action |
|---|---|
| W A S D (or arrows) | Move |
| Drag | Look |
| E | The nearby destination's action (Leave a message, View team murals, Play Aftermovie, View accommodation, Browse event posters), only when one is in reach |
| M | Map / Close map |
| V | Sound on / off (remembered) |
| Esc | Leave a focused view or the map |

Every row with an action is also a button. The current place shows as the same chip top-left (hidden while the map is open). On phones and touch screens the keyboard-only rows are hidden and the movement pad sits bottom-right. The map uses the same chips for every stop and for the hint (`M` / `Esc`).

## Walking feel

A stride clock driven by actual walking speed (1.35 m per step, about 3 steps a second) moves the camera by about 2 cm vertically and 1 cm sideways, with a quarter-degree roll. The lowest point is at each footfall, and the motion settles when you stop. It is off in focused views, on the map, in review captures, and when the visitor prefers reduced motion. A random camera shake is deliberately not used, because it causes motion sickness.

## Sound (`components/gullyverse-runtime/gully-audio.ts`)

Everything except the music is synthesised with Web Audio, so it adds no audio files and carries no third-party licences. Royalty-free libraries (Freesound, Pixabay, Sonniss, Kenney) were not reachable from the build environment. Recorded sounds can replace any layer later.

- **Footsteps** at each footfall: an asphalt scuff and heel thump, or a splash inside the 20 puddles and edge pools extracted from the master. Pitch and level vary per step.
- **Lane bed**: distant traffic rumble, a slowly breathing city hiss, and an occasional distant horn.
- **Street lamps**: positional 100 Hz mains buzz at L01, L03, L04 and L06. The two flickering lamps crackle.
- **Shop radio**: the festival's `FireFire.mp3` (already used by the site's sound button), band-passed and placed in an open shop.
- **Plaza**: a crowd murmur, and the same track low-passed and placed at the screen. It cross-fades in from the forecourt.
- The Aftermovie ducks the environment when it plays with sound.

Browsers allow audio only after a user gesture, so the context starts on the first click, tap or key press. It suspends when the tab is hidden. `V` and the Sound row toggle it, and the choice is stored in `localStorage` (`breeze:sound`).

## Listening to each layer

`/runtime-preview/sounds` (private; needs `GULLYVERSE_RUNTIME_PREVIEW=1`) renders every layer on its own through the same `GullyAudio` code, offline and without 3D placement, as an 8-second clip. It shows each layer's real peak level, and it can normalise quiet layers to −3 dB so they can be judged by ear. `window.renderGullySound(layer, normalise)` returns the clip as a base64 WAV for scripted capture.
