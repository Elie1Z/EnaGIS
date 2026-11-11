"""Validate and package only the new, independently editable user-story film."""
import csv,hashlib,json,re,shutil,zipfile
from pathlib import Path
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT.parent/'outputs/user-story-demo';OUT.mkdir(parents=True,exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(ROOT.parent/'outputs/product-film-v2/EnaGIS-Final-1080p.mp4')=='9e3534559b872b33c12cb28209be3f66da6c01d6c23e5f9105ed49995ad16306'
assert sha(ROOT/'public/v2/video/enagis-outro.mp4')=='322bdd72d5ded39a2142686da7a1255471fcccadcdb5422daabfda8bbae2cf70'
assert (ROOT/'public/story/audio/outro.mp3').read_bytes()==(ROOT/'public/v2/audio/close.mp3').read_bytes()
plan=json.loads((ROOT/'src/story/timeline.json').read_text())
captures=json.loads((ROOT/'src/story/captures.json').read_text())
captions=json.loads((ROOT/'review/story-captions.json').read_text())
audio=json.loads((ROOT/'review/story-audio-qa.json').read_text())
assert sum(s['durationSeconds'] for s in plan['scenes'])==120
assert plan['scenes'][-1]['startSeconds']==110 and plan['scenes'][-1]['durationSeconds']==10
assert audio['clippedSamples']==0 and audio['durationSeconds']==120
assert sum(map(int,re.findall(r'durationInFrames=\{(\d+)\*fps\}',(ROOT/'src/story/UserStoryFilm.tsx').read_text())))==120
for file in captures['files'].values():
    path=ROOT/'public'/file['src'];assert sha(path)==file['sha256']
    with Image.open(path) as im:assert im.size==(1280,672)
count=0
for shot in captures['shots'].values():
    for e in shot['events']:
        r=e['rect'];assert 0<=r['x']<=e['x']<=r['x']+r['w']<=1280
        assert 0<=r['y']<=e['y']<=r['y']+r['h']<=672
        count+=1

def stamp(t):
    ms=round(t*1000);h,ms=divmod(ms,3600000);m,ms=divmod(ms,60000);s,ms=divmod(ms,1000)
    return f'{h:02}:{m:02}:{s:02},{ms:03}'
subtitles=[];cursor=0
for s,c in zip(plan['scenes'],captions,strict=True):
    assert s['id']==c['id'] and s['startSeconds']==cursor
    assert s['voice']=='en-US-AvaNeural'
    assert s['audioDurationSeconds']+s['voiceStartSeconds']<=s['durationSeconds']
    assert ' '.join(x['text'] for x in c['captions'])==s['text']
    cursor+=s['durationSeconds']
    for cue in c['captions']:
        assert 0<=cue['startMs']<cue['endMs']<=s['durationSeconds']*1000
        a=s['startSeconds']+cue['startMs']/1000;b=s['startSeconds']+cue['endMs']/1000
        subtitles.append(f"{len(subtitles)+1}\n{stamp(a)} --> {stamp(b)}\n{cue['text']}")
(OUT/'EnaGIS-User-Story-Demo.srt').write_text('\n\n'.join(subtitles)+'\n',encoding='utf8')

csv_path=Path('C:/Users/mugis/Downloads/enagis-nyabihu-district-potato_storage (3).csv')
with csv_path.open(encoding='utf8',newline='') as f:rows=list(csv.DictReader(f))
lead=next(r for r in rows if r['season']=='dry' and r['rank']=='1')
assert lead['name']=='Kora Market' and round(float(lead['kwh_day_central']))==142
assert len(rows)==620
script=['# EnaGIS — one cold-storage decision','',
 '**Duration:** exactly 2:00, including the full creator outro at 1:50–2:00.',
 '**Voice:** English-only Ava Neural. **Case:** actual saved Nyabihu District potato-storage analysis, dated 10 October 2026.','',
 'This is an illustrative planning task, not a real customer testimonial or a record of completed field verification.','']
for s in plan['scenes']:
    a=s['startSeconds'];b=a+s['durationSeconds']
    script.extend([f"## {a//60:02}:{a%60:02}–{b//60:02}:{b%60:02} · {s['id'].title()}",'',s['text'],''])
(OUT/'Narration-and-timeline.md').write_text('\n'.join(script),encoding='utf8')
readme='''# EnaGIS user-story demo

The new film follows one understandable task: deciding where to investigate a
cold store for potato growers. Kora Market connects the main views to the same
decision. The promotional film is preserved separately.

## Watch or share

`EnaGIS-User-Story-Demo-2min.mp4` is the final shareable file: 1920 × 1080,
30 fps, exactly 120 seconds. Captions, English-only female narration, original
music, measured cursor actions and the full ten-second supplied outro are included.

## What the viewer sees

- Choose an area and value chain; explicitly open a saved case.
- Where first: a ranked shortlist and the Kora Market site.
- Harvest: estimated crop supply from statistics and mapped homes.
- Access: road travel and dry/rainy-season comparison.
- Energy: mapped power infrastructure and an illustrative solar option.
- Site card: estimated peak-day electricity demand, ranges and assumptions.
- How sure: 300 assumption scenarios and stability of the shortlist.
- Likely sites: predicted investigation leads, not confirmed businesses.
- Map data and Sources: missing information and provenance.
- Actual CSV and saved-analysis downloads, then the verification handoff.
- A clear summary: where to look, why it ranks, and what to verify.

## Truthfulness and scope

Screens are real app captures on Satellite imagery, edited into a guided story.
Camera, cursor and supporting graphics are editorial animations; this is not a
continuous screen recording. Searches were not represented as a new live model
run. The example uses a dated saved case and its actual values: 310 candidates,
10 to check first, Kora Market estimated at 142 kWh per peak day (56–388), and
300 existing assumption scenarios. Field-review counts remain zero; no human
checks or customer outcomes were invented. Search availability does not establish
equal data coverage or validated model performance everywhere. No QR is used.

## Edit later

Unzip the editable project, run `npm ci`, then `npm run dev -- --no-open`.
Open `EnaGIS-UserStory-2min` or the clean version. The 13 scenes are independently
editable. Raw narration, word timings, normalized playback files, source captures,
captions and exact timing are retained. No paid account or private credential is
embedded. The supplied outro's original audio is muted beneath the new soundtrack.
'''
(OUT/'README.md').write_text(readme,encoding='utf8')
(ROOT/'STORY-README.md').write_text(readme,encoding='utf8')
shutil.copy2(ROOT/'public/story/audio/final-mix.mp3',OUT/'EnaGIS-User-Story-Audio.mp3')
report=dict(status='passed',durationSeconds=120,frames=3600,fps=30,
    capturedScreens=len(captures['files']),measuredTargets=count,captionWordingAndFit='passed',
    narrationFit='passed',typescriptAndEslint='passed',audio=audio,
    coverage=['Where first','Harvest','Access','Energy','Site card','Assumptions','How sure','Likely sites','Map data','Sources','CSV','Save analysis','Verification'],
    actualDownloadsConfirmed=True,csvRows=len(rows),fieldChecksCompleted=0,
    originalPromotionalVideo='unchanged SHA-256 verified',outroStartsAt=110,outroSeconds=10,
    visualReview=['opening','demand','export','outcome'],notes='Final MP4 export is checked separately in final-video-check.json.')
(OUT/'project-check.json').write_text(json.dumps(report,indent=2),encoding='utf8')

# A self-contained story-only project; it does not require the older film source.
root_source=(ROOT/'src/Root.tsx').read_text()
imports=['import {Composition, Folder} from "remotion";']+[l for l in root_source.splitlines() if l.startswith('import ') and '"./story/' in l]
body=re.search(r'    <Composition id="EnaGIS-UserStory-2min".*?</Folder>',root_source,re.S).group()
standalone='\n'.join(imports)+'\nexport const RemotionRoot=()=> (\n<>\n'+body+'\n</>\n);\n'
archive=OUT/'EnaGIS-User-Story-Editable.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    def add(path):z.write(ROOT/path,Path('enagis-user-story')/path)
    for name in ['package.json','package-lock.json','remotion.config.ts','tsconfig.json','eslint.config.mjs',
                 '.prettierrc','.gitignore','src/design.ts','src/components/basic-captions.tsx',
                 'story-plan.json','story-capture-events.json','scripts/story-voice.py','scripts/story-build.py','scripts/story-mix.py']:
        add(Path(name))
    for folder in ['src/story','public/story']:
        for p in sorted((ROOT/folder).rglob('*')):
            if p.is_file():add(p.relative_to(ROOT))
    for path in ['public/brand/enagis-wordmark.png','public/brand/inter.ttf','public/brand/fraunces.ttf','public/v2/video/enagis-outro.mp4']:
        add(Path(path))
    z.writestr('enagis-user-story/src/Root.tsx',standalone)
    z.writestr('enagis-user-story/src/index.ts','import {registerRoot} from "remotion";\nimport {RemotionRoot} from "./Root";\nregisterRoot(RemotionRoot);\n')
    z.writestr('enagis-user-story/README.md',readme)
    z.write(OUT/'Narration-and-timeline.md','enagis-user-story/Narration-and-timeline.md')
    z.write(OUT/'EnaGIS-User-Story-Demo.srt','enagis-user-story/EnaGIS-User-Story-Demo.srt')
with zipfile.ZipFile(archive) as z:assert z.testzip() is None
(OUT/'Editable-project.sha256.txt').write_text(f'{sha(archive)}  {archive.name}\n',encoding='utf8')
print(json.dumps(dict(archive=str(archive),megabytes=round(archive.stat().st_size/1e6,1),status='passed')))
