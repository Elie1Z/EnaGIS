# EnaGIS commercial revision 2

**Official motto: Mapping Energy. Powering Agriculture.**

Preview: http://localhost:3000/EnaGIS-Commercial-V2

**Ready to share:** `outputs/product-film-v2/EnaGIS-Final-1080p.mp4` from the
repository root. Full HD, 30 fps, 1 minute 47 seconds, approximately 36 MB.
The finished MP4 includes the complete narration, score, captions and supplied
outro. Its 3,210 decoded video frames and stereo AAC soundtrack passed checks;
representative frames from the actual export were visually reviewed.

This is a separate 107-second commercial edit. The original 110-second film is
retained as `EnaGIS-ProductFilm`, with its original pictures, audio, and scene code.
A complete fallback archive is saved in the repository's
`outputs/product-film-v1-preserved/EnaGIS-v1-Preserved.zip`.

## Changes

- New continuous scene narration with **Ava Multilingual Neural**, a female
  Microsoft neural voice, replacing the original Windows desktop voice in V2.
- Both motto recordings use **English-only Ava Neural** to prevent automatic
  multilingual pronunciation. All other approved narration remains unchanged.
- Voice-timed Cooling, Storage, Milling and Drying icon/type reveals, with subtle
  tonal accents, editorial labels and animated numerical callouts.
- The supplied `outro enagis.mp4` plays in full, at its original 10-second pace.
  Its original audio is muted; narration begins 3.2 seconds into the logo build.
- The official motto appears and is spoken in the opening identity and close.
- New Energy section covers mapped lines/infrastructure and illustrative PV,
  including the need to verify connection and capacity.
- Camera moves settle before cursor movement. Each cursor approaches an actual
  measured target, pauses, clicks once, and fades before the next camera move.
- Clicks receive a subtle focus border and spotlight. Native app results remain
  visible after the click.
- New dark navy and mint art direction, animated paths, large type, data callouts,
  range graphic, stability bars, export card, and original 104 BPM score.
- No QR code. Source attribution and saved-analysis date are retained.

## Timeline

| Time | Content |
|---|---|
| 00:00–00:06 | Harvest potential |
| 00:06–00:11 | EnaGIS and official motto |
| 00:11–00:22 | Place search and purpose |
| 00:22–00:31 | Connected agricultural evidence |
| 00:31–00:41 | Roads and seasons |
| 00:41–00:55 | Energy: mapped supply and solar option |
| 00:55–01:08 | Demand estimate, range, and assumptions |
| 01:08–01:19 | 300 scenarios and evidence gaps |
| 01:19–01:28 | Predicted investigation leads |
| 01:28–01:37 | Export and investigation question |
| 01:37–01:47 | Creator-supplied logo outro and English motto narration |

## Assets and editing

The main composition is `EnaGIS-Commercial-V2`; `EnaGIS-Commercial-V2-Clean` omits
captions. Each scene has its own registered composition and authored JSX node.
All V2 source is in `src/v2/`; media is in `public/v2/`.

Actual Satellite app captures were made through normal controls at a fixed
1280 × 672 viewport. Remotion supplies editorial camera/cursor animation and
support graphics. The film is an edited walkthrough. The search entry is
explicitly separated from the saved 10 October 2026 example. Search anywhere
does not establish model validity everywhere. Product models and data were not
changed. Numeric callouts come from the saved case and are labelled accordingly.

Narration was generated via edge-tts 7.3.1 using Microsoft's online neural speech
service; voice IDs `en-US-AvaMultilingualNeural` and `en-US-AvaNeural` (motto only).
It is synthesized narration.
Original MP3s and word timings are retained alongside normalized playback files.
The score and interaction accents are original procedural compositions.

The app export was downloaded again during V2 capture. The final question is
quoted directly from the candidate's exported record. Captions retain the exact
script wording and use the service's measured word timings.

Run `npm ci`, then `npm run dev -- --no-open` from this folder to restart Studio.
The final MP4 is already exported and can be played or shared directly. The
editable design canvas is 4K; the delivery file is 1920 × 1080, with the real
interface captures at the viewport resolution listed above.
