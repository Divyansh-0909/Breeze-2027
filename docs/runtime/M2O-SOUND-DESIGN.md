# M2O Sound design

The gully's sound follows how open-world games build theirs. The research is in [the sound design report](../../reports/Open%20world%20game%20sound%20design.md). Code: `components/gullyverse-runtime/gully-audio.ts`.

## What the research says, and what the gully does

| Open-world practice | In the gully |
|---|---|
| Beds are quiet, anonymous recordings; synthesised noise beds read as hiss | No constant beds. The traffic-and-hiss bed and the crowd murmur were removed. Recorded beds can be added later (Freesound and similar libraries were not reachable from the build environment) |
| Recognisable detail lives in placed emitters and scattered one-shots with random timing, choice, position and cooldowns (GTA V: 949 ambience zones, 1,210 spawn rules, 518 static emitters) | Placed: lamp buzz (L01, L03, L04, L06), the shop radio and the stage. Scattered: distant horns (every 9–27 s, from beyond either end) and a brief, faint two-wheeler crossing the lane mouth (about 3 s, every 25–55 s, with Doppler). The first one-shots wait 6–25 s, so arriving is quiet. (A temple bell and a shop shutter were tried and removed.) |
| Distance is several curves per sound: volume, low-pass for air absorption, reverb send | Every emitter has HRTF placement, a low-pass that closes with distance, a reverb send that grows with distance, and a reach beyond which it fades out and stops costing anything |
| Occlusion muffles the direct sound and leaves the reflections | The stage is muffled and quieter from the lane (behind the gate and houses) and opens up in the plaza; its reverb still carries |
| Zone reverb, cross-faded by position rather than by timer | Two synthetic convolution reverbs: the lane (0.75 s, quick flutter echoes from walls about 5 m apart) and the plaza (1.5 s, facade echoes at 130 and 210 ms). One 0–1 value over the gate (z −4 to −16) blends the reverbs and the lane and plaza buses |
| Worldised music: speaker EQ and the room | The music is the screen's looping Aftermovie, in sync with the picture. The stage goes through PA-style EQ (no deep sub, 1 kHz and 2.5 kHz presence, rolled-off top); the shop radio plays the same sound band-passed with a boxy mid peak. Watching the Aftermovie plays it directly and ducks everything else |
| Footsteps fire by distance travelled; variations with pitch about ±5 % and level about ±3 dB; occasional extra layers | Distance-triggered, heel then toe, alternating feet (slightly left and right), pitch ±5 %, level ±3 dB, grit on about a third of steps, a clothing swish when sprinting, splashes in the 20 puddles |
| Walk vs sprint differ in cadence and weight | Walk: 2.9 m/s, a soft, slower heel-to-toe roll. Sprint (Shift): 4.2 m/s, heavier, quicker footfalls |
| Ambience 10–15 dB under footsteps; web loudness about −16 to −18 LUFS | Ambient one-shots peak 10–15 dB under walking footsteps; master raised about 4 dB with a limiter |
| Budget: few HRTF voices, two convolvers, slow parameter updates | 6 HRTF emitters plus short-lived one-shots, two convolvers, emitter curves updated about 15 times a second |

## Not done yet

- Recorded material: the report recommends 4–8 recorded footstep variations per surface and 2–3 recorded night beds (an Indian night market: distant two-wheelers, vendors, temple aarti). Footsteps are the hardest sound to synthesise convincingly.
- A separate head-bob switch. Reduced motion turns it off today; accessibility guidance (Xbox guideline 117) recommends an explicit toggle.
- Device checks of HRTF cost on low-end phones.

## Listening

`/runtime-preview/sounds` (private, `GULLYVERSE_RUNTIME_PREVIEW=1`) renders each layer from a listening spot in the gully. See [M2N](M2N-SOUND-AND-CONTROLS.md#listening-to-each-layer).
