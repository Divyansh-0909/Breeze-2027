# Current user-approved Gullyverse baseline

Captured 11 October 2026 before source changes. Current implementation overrides historic visual requirements. Later authoring requires user review; no composition redesign authorized here.

Branch `codex/navigation-board`; HEAD `8919589d47385efd674ca91b52376f1ad310b797`; no staged changes. Starting status:

```
 M components/immersive/AftermovieScene.tsx
 M components/immersive/HubScene.tsx
 M components/immersive/ImmersiveShell.tsx
 M components/immersive/aerial.ts
 M components/immersive/blockoutGeometry.ts
 M public/models/gullyverse/blockout.layout.json
 M tests/immersive/runtime.test.ts
?? components/immersive/AftermovieEnvironment.tsx
?? reports/
```

Recoverable source/config/assets snapshot: [archive](../reports/stage-1-final-2026-10-11/raw/current-approved-baseline.tar.gz), [hashes](../reports/stage-1-final-2026-10-11/raw/baseline-hashes.json), [binary diff](../reports/stage-1-final-2026-10-11/raw/baseline.patch). Excludes environment/credential files; includes important untracked AftermovieEnvironment and prior audit. No automatic commit.

## Navigation and geometry

One persistent ImmersiveShell/R3F Canvas on `/` and `/aftermovie`. Shared runtime, navigation.ts and metre-based blockout.layout.json own directions, bounds, arrivals and markers. Ordinary pages leave this Canvas. Only Hub/Aftermovie immersive destinations implemented; Events/Team/Contact use existing pages, Sponsors/Accommodation disabled.

Actual polygon footprint 97.8 × 123.5 m, X [-49.8,48.0], Z [-165.5,-42]. This is collision footprint, not a tight rock-mesh bounding box. Current 25 procedural rock masses, 42 m bent tunnel, dry generated ground and stall anchors retained. Scaffold origin [0, 0, -70], dimensions 24 × 14.5 × 3.4 m. Existing reused stage front beam/logo, Gullyverse-only 10×2.4 header at y11.4; Events/Past Sponsors at y8.8, Team/Contact y7.25, Aftermovie y5.65, navigation text .58 m. Arrows derived from shared travel-zone centers; Main Stage/Accommodation hanging signs absent intentionally.

## Locked lighting/material configuration

Hub/map background/fog #737d87, fog205–520; hemisphere sky#a9bfd4/ground#8a8274 intensity1.35; directional[-70,37,-145], #efd0a4 intensity1.35. Stage mode background/fog#b2bbb9, fog55–130; hemisphere#d8e0dd/#686b59 .65, hub directional omitted. Scaffold practical #ffc681 intensity42 distance21 decay2. No new shadows/postprocessing. Hub rock roughness.98 flat vertex color, ground Lambert tint#c8c2b4. Current stage-local49×39 floor#07080b roughness.9 metalness.1 at local[0,.012,7.5] and cream Gullyverse return placard remain locked. Mode switch and rectangle edge are recorded design-review concerns, not authorization to remove restored elements.

## Stage, camera and assets

Stage world origin[-12, 0, -134.3] yaw0. Original /models/breeze/aftermovie-stage.glb, /models/Man.glb, /models/Animated-Woman.glb and /after-movie.mp4 retained (actual paths also see manifest/source). Stage/Trusses/Speakers/Barricades/Lights/Fireworks/palette and LED shader visuals retained. Stage crowd seeded original model4poses,900/600/300 tiercounts; hub capsules are temporary, no replacement approved. Shared movie source/VideoTexture across threeLEDs, progressive HTTP Range. Current AftermovieEnvironment preserves open rear quarry sightline.

Eyeheight1.72, FOV58, near.1, far700; current portrait composition and aerial fitting unchanged. Landing[0, 1.72, 11.5]; Hub spawn[0, 1.72, -51], arrival[0, 1.72, -46]; Aftermovie spawn[-10.5, 1.72, -110.8], arrival[-10.5, 1.72, -106.8]. Filmfocuslocal[0, 5.9, 17]. Complete registry below includes inspection camera poses, artists, bounds, stall placement, direction zones.

## Existing interaction and performance policy

Visitor clicks/taps/Enter to start landing (intentional). Bent entrance authored7.2s, local WASD/arrows/drag/touch controls; automatic directional hub thresholds; stage bounded walking with text destination menu and hysteresis; Map/M/Esc same-world aerial; browser history/directAftermovie and native fallback. Source inspection is not runtime PASS: fresh evidence recorded in [captures](../reports/stage-1-final-2026-10-11/baseline/captures.json), final runtime checks in separate acceptance report.

Quality0/1/2/3 DPRcaps1.25/1/.75/.6; stage counts900/600/300; twelve covered warmframes, textureinit/compileAsync,45s failure fallback; static world/stage resident from landing, nearcrowd later, video onPlay. Antialiasoff, no realtime shadows. Cloud has SwiftShader, no physical GPU/mobile available; emulation nothardware certification.

## Historical differences

[Actual hash comparison to audit](../reports/stage-1-final-2026-10-11/raw/audit-source-comparison.json). No individual edit authorship inferred. Current values win even where unchanged from audit. Earlier163×190 footprint, smaller scaffold/old hierarchy and daylight recommendations are historical. Reverted Phase2 additions absent at start; its fixes are not assumed present. Restored dark stage floor and placard are preserved, despite older integration recommendations. Aerial map is explicitly approved.

## Exact spatial configuration

```json
{
  "status": "Stage 1 Revision 2 composition study, awaiting human visual approval",
  "units": "metres",
  "eyeHeight": 1.72,
  "playerRadius": 0.38,
  "camera": {
    "fov": 58,
    "near": 0.1,
    "far": 700,
    "minimumHorizontalFov": 42
  },
  "landing": {
    "walkBounds": [
      -15,
      15
    ],
    "position": [
      0,
      1.72,
      11.5
    ],
    "yaw": 0,
    "pitch": 0.15
  },
  "portal": {
    "position": [
      0,
      0,
      0
    ],
    "width": 58,
    "height": 18
  },
  "tunnel": {
    "walkHalfWidth": 2,
    "startZ": 0,
    "endZ": -42,
    "centerline": [
      [
        0,
        0
      ],
      [
        -2.2,
        -8
      ],
      [
        -6,
        -16
      ],
      [
        -6,
        -24
      ],
      [
        -2.6,
        -34
      ],
      [
        0,
        -42
      ]
    ],
    "profile": [
      [
        -2.95,
        0
      ],
      [
        -2.85,
        1.35
      ],
      [
        -2.65,
        2.9
      ],
      [
        -2.15,
        4.15
      ],
      [
        -1.1,
        5.15
      ],
      [
        0.3,
        5.6
      ],
      [
        1.55,
        5.05
      ],
      [
        2.55,
        3.85
      ],
      [
        2.9,
        2.6
      ],
      [
        2.85,
        1.15
      ],
      [
        2.95,
        0
      ]
    ],
    "artists": [
      {
        "label": "NEHA KAKKAR",
        "position": [
          -4.7,
          2.2,
          -7
        ],
        "yaw": 1.5707963267948966
      },
      {
        "label": "CHAAR DIWAARI",
        "position": [
          -2.25,
          2.7,
          -14
        ],
        "yaw": -1.5707963267948966
      },
      {
        "label": "RITVIZ",
        "position": [
          -8.7,
          2.4,
          -22
        ],
        "yaw": 1.5707963267948966
      },
      {
        "label": "KHULLAR G",
        "position": [
          -1.65,
          2.65,
          -29
        ],
        "yaw": -1.5707963267948966
      },
      {
        "label": "TWIN STRINGS",
        "position": [
          -4.5,
          2.4,
          -36
        ],
        "yaw": 1.5707963267948966
      }
    ]
  },
  "quarry": {
    "boundary": [
      [
        -5,
        -42
      ],
      [
        5,
        -42
      ],
      [
        10.8,
        -43.3
      ],
      [
        22.8,
        -47.85
      ],
      [
        36.0,
        -58.9
      ],
      [
        45.6,
        -74.5
      ],
      [
        48.0,
        -99.2
      ],
      [
        44.4,
        -124.55
      ],
      [
        35.4,
        -146.65
      ],
      [
        24.0,
        -157.7
      ],
      [
        4.2,
        -165.5
      ],
      [
        -13.2,
        -164.2
      ],
      [
        -30.0,
        -158.35
      ],
      [
        -42.6,
        -142.1
      ],
      [
        -49.2,
        -118.7
      ],
      [
        -49.8,
        -94.0
      ],
      [
        -44.4,
        -72.55
      ],
      [
        -33.6,
        -56.95
      ],
      [
        -18.6,
        -47.2
      ],
      [
        -14,
        -42
      ]
    ],
    "wallHeights": [
      31.85,
      33.15,
      35.75,
      37.7,
      35.1,
      40.3,
      37.05,
      41.6,
      38.35,
      36.4,
      39.65,
      35.75,
      39.0,
      37.7,
      41.6,
      36.4,
      38.35,
      34.45,
      35.75,
      32.5
    ],
    "benchHeights": [
      0,
      14,
      28,
      43
    ],
    "benchSetbacks": [
      0,
      1.2,
      3.5,
      6
    ],
    "ground": {
      "position": [
        0,
        -0.06,
        -104
      ],
      "size": [
        600,
        600
      ]
    }
  },
  "stage": {
    "origin": [
      -12,
      0,
      -134.3
    ],
    "yaw": 0,
    "filmFocusLocal": [
      0,
      5.9,
      17
    ],
    "asset": "/models/breeze/aftermovie-stage.glb"
  },
  "scaffold": {
    "position": [
      0,
      0,
      -70
    ],
    "width": 24,
    "height": 14.5,
    "depth": 3.4
  },
  "stalls": [
    {
      "id": "left-1",
      "position": [
        -27.6,
        0,
        -77.1
      ],
      "size": [
        7,
        3.5,
        4
      ],
      "yaw": 1.5707963267948966
    },
    {
      "id": "left-2",
      "position": [
        -30.6,
        0,
        -91.4
      ],
      "size": [
        7,
        3.5,
        4
      ],
      "yaw": 1.5707963267948966
    },
    {
      "id": "left-3",
      "position": [
        -29.4,
        0,
        -100
      ],
      "size": [
        7,
        3.5,
        4
      ],
      "yaw": 1.5707963267948966
    },
    {
      "id": "right-1",
      "position": [
        27.0,
        0,
        -77.1
      ],
      "size": [
        7,
        3.5,
        4
      ],
      "yaw": -1.5707963267948966
    },
    {
      "id": "right-2",
      "position": [
        30.6,
        0,
        -91.4
      ],
      "size": [
        7,
        3.5,
        4
      ],
      "yaw": -1.5707963267948966
    },
    {
      "id": "right-3",
      "position": [
        28.8,
        0,
        -109.6
      ],
      "size": [
        7,
        3.5,
        4
      ],
      "yaw": -1.5707963267948966
    }
  ],
  "destinations": [
    {
      "id": "stage",
      "label": "Main Stage / Aftermovie",
      "position": [
        -12,
        0,
        -134.3
      ],
      "anchor": [
        -10.5,
        1.72,
        -110.8
      ],
      "size": [
        34,
        12,
        30
      ],
      "yaw": 0,
      "href": "/aftermovie",
      "status": "active"
    },
    {
      "id": "team",
      "interactionRadius": 3,
      "label": "Team",
      "position": [
        -21.0,
        0,
        -65.4
      ],
      "anchor": [
        -17.4,
        1.72,
        -65.4
      ],
      "size": [
        8,
        3.8,
        1.2
      ],
      "yaw": 1.5707963267948966,
      "href": "/team",
      "status": "spatial-reservation"
    },
    {
      "id": "contact",
      "interactionRadius": 3,
      "label": "Contact Us",
      "position": [
        21.6,
        0,
        -65.4
      ],
      "anchor": [
        18.0,
        1.72,
        -65.4
      ],
      "size": [
        7,
        3.5,
        4
      ],
      "yaw": -1.5707963267948966,
      "href": "/get-in-touch",
      "status": "spatial-reservation"
    },
    {
      "id": "events",
      "label": "Events",
      "position": [
        -41,
        0,
        -99.85
      ],
      "anchor": [
        -36,
        1.72,
        -99.85
      ],
      "size": [
        12,
        0.15,
        10
      ],
      "yaw": 0,
      "href": "/events",
      "status": "reserved"
    },
    {
      "id": "sponsors",
      "label": "Past Sponsors",
      "position": [
        34.8,
        0,
        -100.5
      ],
      "anchor": [
        29.4,
        1.72,
        -100.5
      ],
      "size": [
        12,
        0.15,
        10
      ],
      "yaw": 0,
      "href": "/sponsors",
      "status": "reserved"
    },
    {
      "id": "accommodation",
      "label": "Accommodation",
      "position": [
        26.4,
        0,
        -128.45
      ],
      "anchor": [
        21.0,
        1.72,
        -128.45
      ],
      "size": [
        14,
        0.15,
        12
      ],
      "yaw": 0,
      "href": null,
      "status": "reserved"
    }
  ],
  "population": {
    "exit": {
      "center": [
        -10,
        -55
      ],
      "size": [
        8,
        8
      ],
      "count": 8
    },
    "circulation": {
      "center": [
        7.8,
        -90.1
      ],
      "size": [
        10.8,
        27.95
      ],
      "count": 32
    },
    "stallGroupCount": 5,
    "stageFarCount": 260
  },
  "hub": {
    "movementBoundary": [
      [
        -8,
        -44
      ],
      [
        8,
        -44
      ],
      [
        18,
        -49
      ],
      [
        18,
        -59
      ],
      [
        8,
        -64
      ],
      [
        -8,
        -64
      ],
      [
        -18,
        -59
      ],
      [
        -18,
        -49
      ]
    ],
    "travelZones": [
      {
        "id": "aftermovie",
        "sign": null,
        "edge": 0,
        "range": [
          0.2,
          0.8
        ]
      },
      {
        "id": "events",
        "edge": 5,
        "range": [
          0.1,
          0.6
        ]
      },
      {
        "id": "team",
        "edge": 0,
        "range": [
          0.015,
          0.165
        ]
      },
      {
        "id": "contact",
        "edge": 0,
        "range": [
          0.835,
          0.985
        ]
      },
      {
        "id": "sponsors",
        "edge": 3,
        "range": [
          0.4,
          0.9
        ]
      }
    ],
    "spawn": [
      0,
      1.72,
      -51
    ],
    "arrivalStart": [
      0,
      1.72,
      -46
    ],
    "yaw": 0,
    "pitch": 0.2,
    "bounds": [
      -18,
      18,
      -64,
      -44
    ]
  },
  "aftermovie": {
    "movementBoundary": [
      [
        -19.2,
        -106.3
      ],
      [
        -4.8,
        -106.3
      ],
      [
        -4.0,
        -107.1
      ],
      [
        -4.0,
        -117.7
      ],
      [
        -4.8,
        -118.5
      ],
      [
        -19.2,
        -118.5
      ],
      [
        -20.0,
        -117.7
      ],
      [
        -20.0,
        -107.1
      ]
    ],
    "returnSignLocal": [
      6,
      2.8,
      27.8
    ],
    "spawn": [
      -10.5,
      1.72,
      -110.8
    ],
    "arrivalStart": [
      -10.5,
      1.72,
      -106.8
    ],
    "yaw": 0,
    "pitch": 0.16,
    "bounds": [
      -20.0,
      -4.0,
      -118.5,
      -106.3
    ]
  },
  "cameras": [
    {
      "id": "landing",
      "position": [
        0,
        1.72,
        11.5
      ],
      "target": [
        0,
        3.5,
        0
      ],
      "fov": 58
    },
    {
      "id": "tunnel-near",
      "position": [
        -0.825,
        1.72,
        -3
      ],
      "target": [
        -4,
        2.3,
        -12
      ],
      "fov": 58
    },
    {
      "id": "tunnel-mid",
      "position": [
        -6,
        1.72,
        -22
      ],
      "target": [
        -2.6,
        2.4,
        -34
      ],
      "fov": 58
    },
    {
      "id": "tunnel-first-exit-reveal",
      "position": [
        -4.64,
        1.72,
        -28
      ],
      "target": [
        0,
        3.1,
        -42
      ],
      "fov": 58
    },
    {
      "id": "exit",
      "position": [
        -1.3,
        1.72,
        -38
      ],
      "target": [
        0,
        7.4,
        -70
      ],
      "fov": 58
    },
    {
      "id": "scaffold-front",
      "position": [
        0,
        1.72,
        -46
      ],
      "target": [
        0,
        8,
        -70
      ],
      "fov": 58
    },
    {
      "id": "scaffold-diagonal",
      "position": [
        -10,
        1.72,
        -52
      ],
      "target": [
        0,
        8,
        -70
      ],
      "fov": 58
    },
    {
      "id": "quarry",
      "position": [
        0,
        1.72,
        -51
      ],
      "target": [
        0.0,
        6.6,
        -92.7
      ],
      "fov": 58
    },
    {
      "id": "left-stalls",
      "position": [
        -18.0,
        1.72,
        -72.55
      ],
      "target": [
        -27.0,
        2.2,
        -87.5
      ],
      "fov": 58
    },
    {
      "id": "right-stalls",
      "position": [
        17.4,
        1.72,
        -72.55
      ],
      "target": [
        26.4,
        2.2,
        -87.5
      ],
      "fov": 58
    },
    {
      "id": "overview",
      "position": [
        0,
        145,
        -77
      ],
      "target": [
        0,
        0,
        -77
      ],
      "fov": 65
    },
    {
      "id": "stage-front",
      "position": [
        -10.5,
        1.72,
        -110.8
      ],
      "target": [
        -12.0,
        5.9,
        -128.3
      ],
      "fov": 58
    },
    {
      "id": "stage-return",
      "position": [
        -10.5,
        1.72,
        -108.3
      ],
      "target": [
        0,
        5,
        -42
      ],
      "fov": 58
    }
  ],
  "inspection": {
    "overheadPadding": 1.08
  }
}
```

Relevant sources: [HubScene](../components/immersive/HubScene.tsx), [geometry](../components/immersive/blockoutGeometry.ts), [paint](../components/immersive/worldPaint.ts), [layout](../public/models/gullyverse/blockout.layout.json), [world](../components/immersive/world.ts), [navigation](../components/immersive/navigation.ts), [runtime](../components/immersive/runtime.ts), [aerial](../components/immersive/aerial.ts), [stage scene](../components/immersive/AftermovieScene.tsx), [stage environment](../components/immersive/AftermovieEnvironment.tsx). Asset SHA256s in snapshot manifest. Baseline captures are actual running website images, separate from new acceptance images. Matched camera views are review probes, not visitor-route proof.
