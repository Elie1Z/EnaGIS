"""Index revision captures, build phrase captions, and create editable scene nodes."""
import hashlib,json,re,subprocess
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'src/v2'
DATA.mkdir(parents=True,exist_ok=True)
(DATA/'scenes').mkdir(exist_ok=True)
timeline=json.loads((ROOT/'v2-timeline.json').read_text())
ffprobe=ROOT/'node_modules/@remotion/compositor-win32-x64-msvc/ffprobe.exe'
files={}
for path in (ROOT/'public/v2/footage').glob('*.png'):
    if path.stem in ['probe','energy-full']:continue
    with Image.open(path) as im: size=im.size
    assert size==(1280,672),(path,size)
    files[path.stem]=dict(src='v2/footage/'+path.name,width=size[0],height=size[1],sha256=hashlib.sha256(path.read_bytes()).hexdigest())
def event(t,x,y,w,h,label):return dict(seconds=t,x=x,y=y,rect=dict(x=x-w/2,y=y-h/2,w=w,h=h),label=label)
def shot(before,after,click,extra=None):
    result=dict(states=[dict(seconds=0,image=before),dict(seconds=click['seconds']+.2,image=after)],events=[click])
    if extra:result.update(extra)
    return result
shots={
 'search':shot('search-empty','search-filled',event(1.95,364,34,288,30,'Choose a place'),dict(states=[dict(seconds=0,image='search-empty'),dict(seconds=2.15,image='search-filled'),dict(seconds=6.65,image='search-milling')],events=[event(1.95,364,34,288,30,'Choose a place'),event(6.45,636.74,34,216,44,'Choose a purpose')])),
 'evidence':shot('harvest','coverage',event(1.95,43.67,419.67,71.33,70,'Map data')),
 'access':shot('access-dry','access-rain',event(2.45,1022.06,34,111.5,38,'Rainy season')),
 'energy':shot('access-dry','energy',event(1.95,43.67,267.67,71.33,70,'Energy'),dict(states=[dict(seconds=0,image='access-dry'),dict(seconds=2.15,image='energy'),dict(seconds=6.45,image='energy-solar-list'),dict(seconds=8.15,image='energy-card'),dict(seconds=10,image='energy-options')],events=[event(1.95,43.67,267.67,71.33,70,'Energy'),event(7.95,266.33,339.72,287.33,57.2,'Solar option')])),
 'demand':shot('ranking','demand',event(1.95,266.33,339.77,287.33,57.2,'Open the site'),dict(states=[dict(seconds=0,image='ranking'),dict(seconds=2.15,image='demand'),dict(seconds=9.15,image='assumptions')],events=[event(1.95,266.33,339.77,287.33,57.2,'Open the site'),event(8.95,970.11,337.18,54.89,40.67,'Trace the estimate')])),
 'confidence':shot('access-dry','confidence',event(1.95,43.67,495.67,71.33,70,'How sure'),dict(states=[dict(seconds=0,image='access-dry'),dict(seconds=2.15,image='confidence'),dict(seconds=8.2,image='coverage')],events=[event(1.95,43.67,495.67,71.33,70,'How sure')])),
 'discover':shot('discover-list','discover-card',event(1.95,266.33,339.73,287.33,57.2,'Inspect the suggestion')),
 'shortlist':dict(states=[dict(seconds=0,image='shortlist')],events=[event(1.95,351.35,509.33,47.11,36,'Export CSV')]),
}
for key,shot_data in shots.items():
    for state in shot_data['states']:assert state['image'] in files,(key,state)
manifest=dict(version=2,captureMethod='Real app screenshots; measured UI targets; editorial camera/cursor motion',basemap='Satellite',savedCaseDate='2026-10-10',source='http://127.0.0.1:8765/',files=files,shots=shots)
(DATA/'captures.json').write_text(json.dumps(manifest,indent=2),encoding='utf8')
captions=[]
for s in timeline['scenes']:
    offset=s.get('voiceStartSeconds',3.2 if s['id']=='close' else .35)
    s['voiceStartSeconds']=offset
    words=json.loads((ROOT/'public/v2/audio'/f"{s['id']}-words.json").read_text())
    original_tokens=s['text'].split()
    assert len(original_tokens)==len(words),(s['id'],len(original_tokens),len(words))
    # Keep the original punctuation; service word events omit sentence marks.
    for word,token in zip(words,original_tokens,strict=True):word['text']=token
    groups=[];group=[]
    for word in words:
        group.append(word)
        if re.search(r'[.!?]$',word['text']) or len(group)>=6:
            groups.append(group);group=[]
    if group:groups.append(group)
    caps=[dict(text=' '.join(w['text'] for w in g),startMs=round(g[0]['startMs']+offset*1000),endMs=round(g[-1]['endMs']+offset*1000+150),timestampMs=None,confidence=None,pageBreakAfter=True) for g in groups]
    for i,c in enumerate(caps[:-1]):c['endMs']=min(c['endMs'],caps[i+1]['startMs']-30)
    assert caps[-1]['endMs']<s['durationSeconds']*1000,(s['id'],caps[-1])
    caps[-1]['endMs']=min(s['durationSeconds']*1000-150,caps[-1]['endMs']+200)
    duration=float(subprocess.check_output([str(ffprobe),'-v','error','-show_entries','format=duration','-of','csv=p=0',str(ROOT/'public'/s['audio'])],text=True).strip())
    assert duration+offset<=s['durationSeconds'],(s['id'],duration)
    s['audioDurationSeconds']=duration
    captions.append(dict(id=s['id'],startSeconds=s['startSeconds'],captions=caps))
    name=s['id'].title()
    media='Audio,Video' if s['id']=='close' else 'Audio'
    scene_import='' if s['id']=='close' else 'import {AdScene} from "../AdScene";'
    visual='<Video name="Creator-supplied EnaGIS outro" src={staticFile("v2/video/enagis-outro.mp4")} muted premountFor={fps} style={{position:"absolute",inset:0,width:"100%",height:"100%"}} objectFit="contain"/>' if s['id']=='close' else f'<AdScene id="{s["id"]}"/>'
    body=f'''import {{{media}}} from "@remotion/media";
import {{staticFile,useVideoConfig}} from "remotion";
import {{BasicCaptions}} from "../../components/basic-captions";
{scene_import}
export const {name}V2 = ({{captions}}:{{captions:boolean}}) => {{
 const {{fps}}=useVideoConfig();
 return <>
  {visual}
  <Audio name="{name} · neural female narration" from={{{offset}*fps}} src={{staticFile("v2/audio/{s['id']}-normalized.mp3")}} premountFor={{fps}}/>
  {{captions ? <div className="ad-captions"><BasicCaptions name="{name} · captions" premountFor={{fps}} width={{3040}}
    style={{{{position:"absolute",left:400,bottom:70}}}}
    captions={{{json.dumps(caps,indent=6)}}}/></div> : null}}
 </>;
}};
'''
    (DATA/'scenes'/f'{name}V2.tsx').write_text(body,encoding='utf8')
(DATA/'timeline.json').write_text(json.dumps(timeline,indent=2),encoding='utf8')
(ROOT/'review/v2-captions.json').write_text(json.dumps(captions,indent=2),encoding='utf8')
print(f'{len(files)} real captures, {len(timeline["scenes"])} authored scenes; all narration fits.')
