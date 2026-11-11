# EnaGIS product film

**New user-story demo:** `EnaGIS-UserStory-2min`, exactly 2:00 including the
creator's outro. Final shareable MP4:
`outputs/user-story-demo/EnaGIS-User-Story-Demo-2min.mp4` from the repository root.
See `STORY-README.md`. This is a separate film; the promotional cut below is preserved.

**Current revision:** `EnaGIS-Commercial-V2`, 107 seconds, with Ava neural female
narration, the official motto **Mapping Energy. Powering Agriculture.**, a
dedicated Energy section, voice-timed purpose animations, the creator's outro,
and revised camera/cursor choreography. Both motto clips use English-only Ava. Open
**http://localhost:3000/EnaGIS-Commercial-V2**. See `V2-README.md` for delivery notes.

The original 110-second cut remains registered as `EnaGIS-ProductFilm`; its
complete fallback archive is `outputs/product-film-v1-preserved/EnaGIS-v1-Preserved.zip`
from the repository root. The original-version notes follow below.

**Completed editable Remotion film — 110 seconds, 3840 × 2160 canvas, 30 fps.**

Open **EnaGIS-ProductFilm** for the captioned film with narration, original music,
and subtle interaction sounds. **EnaGIS-CleanFilm** has the same sound and visuals
without captions. The ten scenes can also be edited individually.

## Watch

Preview: **http://localhost:3000/EnaGIS-ProductFilm** while Studio runs.
Press Play; use the fullscreen control for the presentation view.

To restart from this folder:

```powershell
npm ci
npm run dev -- --no-open
```

The project is ready for export through Studio's **Render** control. No final
MP4 has been exported; this delivery is the interactive preview and editable
project. Product captures are 1920 × 1080; titles and animation use a 4K canvas.
For these source captures, 1920 × 1080 is the practical submission resolution.

## Film timeline

| Time | Scene |
|---|---|
| 00:00–00:06 | Harvest and energy |
| 00:06–00:12 | Investment question and EnaGIS identity |
| 00:12–00:26 | Place search and value-chain selection |
| 00:26–00:38 | Agricultural evidence and candidate reach |
| 00:38–00:50 | Road access and seasonal comparison |
| 00:50–01:07 | Energy estimate, range, and assumptions |
| 01:07–01:21 | 300-scenario stability and data gaps |
| 01:21–01:32 | Predicted places to investigate |
| 01:32–01:42 | Actual CSV export and site question |
| 01:42–01:50 | Product address and Team Dynamis |

## Picture and evidence

The product sequence uses actual screenshots captured through the app's normal
controls with Satellite selected. Remotion adds camera movement, an animated
cursor at observed click targets, and editorial cuts between captured states.
It is an edited walkthrough, not a continuous screen recording.

Search is separated from the dated saved example by a visible transition.
Analysis scenes identify the saved 10 October 2026 snapshot. Global place search
does not imply worldwide model validation. ESTIMATED, PREDICTED, assumption
ranges, and map attribution remain part of the presentation. The 300 scenarios
are assumption draws, not field tests or training iterations.

The CSV was downloaded from the actual app: 620 rows covering 310 candidates in
each of two seasons. Its dry-season excerpt is shown as an editorial card.
The original export is retained in `review/exported-shortlist.csv`.

The opener uses the approved generated agriculture/solar illustration, labelled
as a concept illustration. The existing EnaGIS wordmark is retained. The close
uses the wordmark, tagline, website, and Team Dynamis. Neither main composition
contains a QR code. Product code, models, and data were not changed.

## Sound and captions

- Narration: synthesized locally using the installed Microsoft Mark voice.
- Music: original procedural instrumental composition, quieter under narration.
- Effects: restrained original click accents.
- Captions: 26 phrases, with speech aligned inside the caption windows.
- Mix: 110 seconds, 48 kHz, approximately −3.35 dBFS peak, zero clipped samples.

Separate editable stems are in `public/audio/`; `preview-mix.wav` combines them.
The narration voice can be replaced without changing the scene structure.

## Review and reproducibility

`src/capture-manifest.json` records source, image hashes, camera moves, and cursor
positions. `review/audio-qa.json` records phrase timing and mix checks.
`review/FINAL-REVIEW.md` records the final review. Assets and font licences are
listed in `asset-manifest.json`.

`scripts/prepare-assets.py` was used for the initial scaffold; rerunning it would
overwrite scene edits. Audio generation and capture indexing scripts are retained
separately. All playback assets are local; watching the finished film does not
need live Satellite tile downloads.
