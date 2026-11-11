"""Copy approved assets and write authored scene files for the production timeline."""
from pathlib import Path
import json
import re
import shutil

PROJECT = Path(__file__).resolve().parents[1]
REPO = PROJECT.parent
PUBLIC = PROJECT / "public"
for folder in ["brand", "imagery", "footage", "audio"]:
    (PUBLIC / folder).mkdir(parents=True, exist_ok=True)

assets = {
    "live/assets/brand/enagis-wordmark.png": "brand/enagis-wordmark.png",
    "live/assets/brand/enagis-mark.png": "brand/enagis-mark.png",
    "live/assets/inter.ttf": "brand/inter.ttf",
    "live/assets/fraunces.ttf": "brand/fraunces.ttf",
    "live/assets/OFL-Inter.txt": "brand/OFL-Inter.txt",
    "live/assets/OFL-Fraunces.txt": "brand/OFL-Fraunces.txt",
    "outputs/poster-professional/assets/agriculture-energy-panorama.png": "imagery/agriculture-energy-panorama.png",
}
for source, target in assets.items():
    shutil.copy2(REPO / source, PUBLIC / target)

caption_source = (PROJECT / "basic-captions-source.md").read_text(encoding="utf-8")
code = re.search(r"```tsx[^\n]*\n(.*?)\n```", caption_source, re.S).group(1)
(PROJECT / "src/components/basic-captions.tsx").write_text(code + "\n", encoding="utf-8")

timeline = json.loads((REPO / "outputs/promo-demo-preparation/timeline.json").read_text(encoding="utf-8-sig"))
scene_names = {
    "search": ("Search", "Start with a place.", "A place. A value chain. A question worth investigating."),
    "evidence": ("Evidence", "Connect the evidence.", "Mapped activity and the areas each candidate can reach."),
    "access": ("Access", "Understand what is in reach.", "The same place. Two seasons. Different access."),
    "demand": ("Demand", "Estimate the need.", "An energy estimate, its range, and the assumptions behind it."),
    "uncertainty": ("Uncertainty", "See how sure.", "300 scenarios. Ranking stability. Visible information gaps."),
    "predictions": ("Predictions", "Find places to check.", "Predicted opportunities alongside mapped locations."),
    "shortlist": ("Shortlist", "Leave with a shortlist.", "Ranked places, supporting evidence, and the next question."),
}
chunks = {
    "search": [(0.4, 3.0, "Start with a place."), (3.2, 6.1, "Search the map, then choose what you want to study:"),
               (6.3, 12.7, "cooling, storage, milling, or drying.")],
    "evidence": [(0.4, 4.6, "EnaGIS brings open maps and agricultural evidence together,"),
                 (4.8, 8.1, "revealing mapped activity"),
                 (8.3, 11.6, "and the areas each candidate can reach.")],
    "access": [(0.4, 3.2, "Follow the roads."), (3.4, 6.4, "Compare the seasons."),
               (6.6, 11.4, "See how access changes when conditions do.")],
    "demand": [(0.4, 3.9, "Open a promising site."), (4.1, 8.0, "See estimated energy demand"),
               (8.2, 11.9, "with a range around it,"), (12.1, 16.4, "and the assumptions behind the number.")],
    "uncertainty": [(0.4, 5.0, "Stress-test the assumptions across 300 scenarios."),
                    (5.2, 9.0, "See what stays near the top,"), (9.2, 13.4, "and where information is still missing.")],
    "predictions": [(0.4, 4.8, "Explore predicted places to check,"),
                    (5.0, 10.4, "alongside the locations already recorded on the map.")],
    "shortlist": [(0.4, 3.4, "Export a ranked shortlist,"), (3.6, 6.0, "the supporting evidence,"),
                  (6.2, 9.4, "and the question to ask at each site.")],
}
all_captions = []
for number, (scene_id, (name, title, subtitle)) in enumerate(scene_names.items(), 1):
    captions = [
        {"text": text, "startMs": round(start * 1000), "endMs": round(end * 1000),
         "timestampMs": None, "confidence": None, "pageBreakAfter": True}
        for start, end, text in chunks[scene_id]
    ]
    source = f'''import {{useVideoConfig}} from "remotion";
import type {{SceneProps}} from "../design";
import {{ProductShot}} from "../components/ProductShot";
import {{BasicCaptions}} from "../components/basic-captions";

export const {name} = ({{captions}}: SceneProps) => {{
  const {{fps}} = useVideoConfig();
  return <>
    <ProductShot id="{scene_id}" number="{number:02d}"
      title={json.dumps(title)} subtitle={json.dumps(subtitle)}/>
    {{captions ? <BasicCaptions name="{name} narration" premountFor={{fps}} width={{2800}}
      style={{{{position:"absolute",left:520,bottom:56}}}}
      captions={{{json.dumps(captions, indent=8)}}}/> : null}}
  </>;
}};
'''
    (PROJECT / f"src/scenes/{name}.tsx").write_text(source, encoding="utf-8")
    timing = next(scene for scene in timeline["scenes"] if scene["id"] == scene_id)
    all_captions.append({"id": scene_id, "startSeconds": timing["startSeconds"], "captions": captions})

shutil.copy2(REPO / "outputs/promo-demo-preparation/VOICEOVER.txt", PROJECT / "VOICEOVER.txt")
(PROJECT / "caption-timing.json").write_text(json.dumps(all_captions, indent=2), encoding="utf-8")
(PROJECT / "asset-manifest.json").write_text(json.dumps({
    "assets": assets,
    "photographs": "Generated editorial illustration; not map evidence or a surveyed facility.",
    "mapFootage": "Not captured. Satellite required. Offline and synthetic screenshots are excluded.",
    "captions": "Script-timed, not aligned to recorded speech.",
    "voiceover": "Missing; no speech audio has been generated.",
}, indent=2), encoding="utf-8")
print("Approved assets copied. Seven independently editable product scenes prepared.")
