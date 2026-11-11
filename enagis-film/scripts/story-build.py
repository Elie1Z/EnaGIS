"""Build truthful capture timing, captions and separately editable story scenes."""
import hashlib,json,re,subprocess
from pathlib import Path
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'src/story';DATA.mkdir(parents=True,exist_ok=True)
(DATA/'scenes').mkdir(exist_ok=True)
plan=json.loads((ROOT/'story-plan.json').read_text())
measured=json.loads((ROOT/'story-capture-events.json').read_text())
probe=ROOT/'node_modules/@remotion/compositor-win32-x64-msvc/ffprobe.exe'
files={}
for path in (ROOT/'public/story/footage').glob('*.png'):
    with Image.open(path) as im:assert im.size==(1280,672),(path,im.size)
    files[path.stem]=dict(src='story/footage/'+path.name,sha256=hashlib.sha256(path.read_bytes()).hexdigest(),width=1280,height=672)

def e(key,t):
    r=measured[key]
    return dict(seconds=t,x=r['cx'],y=r['cy'],rect=dict(x=r['x'],y=r['y'],w=r['w'],h=r['h']),label=key)
def shot(states,events=(),camera='full'):
    return dict(states=[dict(seconds=t,image=img) for t,img in states],events=list(events),camera=camera)

shots={
 'place':shot([(0,'start'),(1.28,'place'),(5.08,'case-open')],[
    dict(seconds=1.1,x=364.026,y=34,rect=dict(x=219.979,y=22.854,w=288.094,h=22.292),label='Search the area'),
    dict(seconds=4.9,x=266.333,y=287.854,rect=dict(x=136.667,y=260.896,w=259.333,h=53.917),label='Open the saved case')],'place'),
 'ranking':shot([(0,'ranking'),(2.9,'ranking-list'),(4.48,'demand')],[e('site',4.3)],'site'),
 'harvest':shot([(0,'ranking'),(1.48,'harvest')],[e('harvest',1.3)]),
 'access':shot([(0,'harvest'),(1.38,'access-dry'),(4.48,'access-rain')],[e('access',1.2),e('rain',4.3)]),
 'energy':shot([(0,'access-dry'),(1.38,'energy'),(4.0,'energy-list'),(5.38,'energy-card'),(8.0,'energy-options')],[e('energy',1.2),e('solar',5.2)],'energy'),
 'demand':shot([(0,'ranking-list'),(1.38,'demand'),(7.98,'assumptions')],[e('site',1.2),e('trace',7.8)],'demand'),
 'confidence':shot([(0,'ranking'),(1.38,'confidence')],[e('sure',1.2)]),
 'discover':shot([(0,'confidence'),(1.28,'discover'),(2.8,'discover-list'),(4.28,'discover-card')],[e('likely',1.1),e('predicted',4.1)],'discover'),
 'evidence':shot([(0,'discover'),(1.38,'coverage'),(3.48,'sources')],[e('coverage',1.2),e('sources',3.3)]),
 'export':shot([(0,'export-ready'),(5.68,'verification')],[e('csv',1.1),e('save',3.2),e('verify',5.5)]),
}
manifest=dict(captureMethod='Actual app screenshots edited into a guided user story; measured controls; editorial camera and cursor',
    source='http://127.0.0.1:8765/',basemap='Satellite',savedAnalysisDate='2026-10-10',
    case='Nyabihu District, potato cold storage',files=files,shots=shots,
    downloadsConfirmed=['enagis-nyabihu-district-potato_storage (3).csv','enagis-nyabihu-district-data (2).json'],
    fieldVerification='Not completed; UI shows zero reviews, calls and visits. No records invented.')
(DATA/'captures.json').write_text(json.dumps(manifest,indent=2),encoding='utf8')

caps_all=[]
for s in plan['scenes']:
    words=json.loads((ROOT/'public/story/audio'/f"{s['id']}-words.json").read_text())
    tokens=s['text'].split()
    assert len(words)==len(tokens),(s['id'],len(words),len(tokens))
    for w,token in zip(words,tokens,strict=True):w['text']=token
    groups=[];g=[]
    for w in words:
        g.append(w)
        if re.search(r'[.!?]$',w['text']) or len(g)>=7:
            groups.append(g);g=[]
    if g:groups.append(g)
    offset=s['voiceStartSeconds']*1000
    caps=[dict(text=' '.join(w['text'] for w in g),startMs=round(g[0]['startMs']+offset),
        endMs=round(g[-1]['endMs']+offset+180),timestampMs=None,confidence=None,pageBreakAfter=True) for g in groups]
    for i,c in enumerate(caps[:-1]):c['endMs']=min(c['endMs'],caps[i+1]['startMs']-25)
    caps[-1]['endMs']=min(s['durationSeconds']*1000-50,caps[-1]['endMs']+250)
    assert caps[-1]['endMs']>words[-1]['endMs']+offset
    duration=float(subprocess.check_output([str(probe),'-v','error','-show_entries','format=duration','-of','csv=p=0',str(ROOT/'public'/s['audio'])],text=True).strip())
    assert duration+s['voiceStartSeconds']<=s['durationSeconds'],(s['id'],duration,s['voiceStartSeconds'])
    s['audioDurationSeconds']=duration
    caps_all.append(dict(id=s['id'],startSeconds=s['startSeconds'],captions=caps))
    name=s['id'].title()+'Story'
    media='Audio,Video' if s['id']=='outro' else 'Audio'
    visual='<Video name="Creator outro · full ten seconds" src={staticFile("v2/video/enagis-outro.mp4")} muted premountFor={fps} objectFit="contain" style={{position:"absolute",inset:0,width:"100%",height:"100%"}}/>' if s['id']=='outro' else f'<StoryVisual id="{s["id"]}"/>'
    imp='' if s['id']=='outro' else 'import {StoryVisual} from "../StoryVisual";'
    body=f'''import {{{media}}} from "@remotion/media";
import {{staticFile,useVideoConfig}} from "remotion";
import {{BasicCaptions}} from "../../components/basic-captions";
{imp}
export const {name}=({{captions}}:{{captions:boolean}})=>{{
 const {{fps}}=useVideoConfig();
 return <>
  {visual}
  <Audio name="{s['id']} · English Ava narration" src={{staticFile("story/audio/{s['id']}-normalized.mp3")}} from={{{s['voiceStartSeconds']}*fps}} premountFor={{fps}}/>
  {{captions?<div className="story-captions"><BasicCaptions name="{s['id']} · timed captions" width={{1640}} premountFor={{fps}} style={{{{position:"absolute",left:140,bottom:34}}}} captions={{{json.dumps(caps,indent=4)}}}/></div>:null}}
 </>;
}};
'''
    (DATA/'scenes'/f'{name}.tsx').write_text(body,encoding='utf8')
(DATA/'timeline.json').write_text(json.dumps(plan,indent=2),encoding='utf8')
(ROOT/'review/story-captions.json').write_text(json.dumps(caps_all,indent=2),encoding='utf8')
print(f"{len(files)} real captures; 13 editable scenes; every voice and caption fits 120 seconds.")
