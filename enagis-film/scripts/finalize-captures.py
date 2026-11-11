"""Index the actual browser captures and measured editorial camera/cursor moves."""
import json, hashlib, csv
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
def camera(*rows):return [dict(seconds=t,x=x,y=y,zoom=z) for t,x,y,z in rows]
def cursor(*rows):return [dict(seconds=t,x=x,y=y,click=bool(c)) for t,x,y,c in rows]
def states(*rows):return [dict(seconds=t,src='footage/'+name+'.png') for t,name in rows]
shots=[
 dict(id='search',durationSeconds=14,savedAnalysis=False,
      states=states((0,'search-0'),(1.65,'search-1'),(6.55,'search-2')),
      camera=camera((0,960,540,1),(1,720,240,1.9),(5.8,720,240,1.9),(7,950,230,1.9),(11,960,540,1),(14,960,540,1)),
      cursor=cursor((0,560,220,0),(1.5,400,34,1),(3.1,400,34,0),(5.8,550,130,0),(6.4,833,34,1),(9,900,180,0),(14,900,180,0)),
      notes='Actual search text entry and actual value-chain selection. No Analyze request is implied. Explicit transition to a dated saved example.'),
 dict(id='evidence',durationSeconds=12,savedAnalysis=True,
      states=states((0,'evidence-harvest'),(5.65,'evidence-data'),(8.6,'demand-card')),
      camera=camera((0,960,540,1),(1,700,450,1.75),(4.8,700,450,1.75),(6.4,650,470,2.1),(8.4,650,470,2.1),(9.4,1050,510,1.35),(12,1050,510,1.35)),
      cursor=cursor((0,180,180,0),(4.8,180,350,0),(5.5,44,420,1),(7.8,44,420,0),(12,880,510,0)),
      notes='Harvest, Map data, and a real selected catchment. Result panels are edited screen captures; source data unchanged.'),
 dict(id='access',durationSeconds=12,savedAnalysis=True,
      states=states((0,'access-dry'),(4.45,'access-rainy')),
      camera=camera((0,960,540,1.15),(1,1000,470,1.4),(3,1300,250,1.9),(4.6,1300,250,1.9),(6,620,440,2.1),(10.3,620,440,2.1),(12,960,540,1.1)),
      cursor=cursor((0,1150,300,0),(3.5,1500,160,0),(4.3,1662,34,1),(5,1662,34,0),(7,350,470,0),(12,350,470,0)),
      notes='Actual dry/rainy toggle and resulting rankings. Both captured with Satellite selected.'),
 dict(id='demand',durationSeconds=17,savedAnalysis=True,
      states=states((0,'ranking'),(1.95,'demand-card'),(12.25,'demand-assumptions')),
      camera=camera((0,630,540,1.8),(1,620,540,2),(2.3,960,540,1.1),(3.5,1435,300,2.2),(11.6,1435,300,2.2),(13,1420,300,2.1),(17,1420,300,2.1)),
      cursor=cursor((0,440,700,0),(1.8,266,619,1),(2.5,266,619,0),(4,1700,380,0),(11.4,1700,380,0),(12.1,1610,337,1),(13.5,1600,460,0),(17,1600,460,0)),
      notes='Click targets measured from actual DOM. The 142 kWh/day, 56–388 range, ESTIMATED label and formula are retained. Assumptions were only read.'),
 dict(id='uncertainty',durationSeconds=14,savedAnalysis=True,
      states=states((0,'uncertainty'),(9.35,'evidence-data')),
      camera=camera((0,960,540,1),(1.3,610,440,2.2),(8.5,610,440,2.2),(10,640,420,2),(14,640,420,2)),
      cursor=cursor((0,500,450,0),(8.6,200,470,0),(9.2,44,420,1),(10,200,440,0),(14,200,440,0)),
      notes='Actual How sure and Map data panels. 300 existing scenario draws; no claim of field tests or new model training.'),
 dict(id='predictions',durationSeconds=11,savedAnalysis=True,
      states=states((0,'predictions'),(4.7,'predictions-card')),
      camera=camera((0,960,540,1),(1,1130,550,1.4),(4.4,1130,550,1.4),(5.8,1430,350,1.9),(9.4,1430,350,1.9),(11,960,540,1)),
      cursor=[],
      notes='Editorial cut from actual predicted layer to actual Look-alike 1 card selected via its list row. No reconstructed click on overlapping map markers. PREDICTED remains visible.'),
 dict(id='shortlist',durationSeconds=10,savedAnalysis=True,
      states=states((0,'shortlist'),(5.8,'demand-card')),
      camera=camera((0,960,540,1),(1.3,630,760,1.95),(3,630,760,1.95),(4.6,960,540,1),(6.7,1420,610,1.95),(10,1420,610,1.95)),
      cursor=cursor((0,600,700,0),(2.1,351,917,1),(3,351,917,0),(5,650,650,0),(7,1650,740,0),(10,1650,740,0)),
      notes='CSV button clicked and download verified. The displayed export summary is an editorial excerpt of that actual file, not an app success toast.'),
]
files={}
for shot in shots:
    shot.update(src=shot['states'][0]['src'],width=1920,height=1080,reviewed=True,satelliteVerified=True,containsCursor=False)
    for state in shot['states']:
        path=ROOT/'public'/state['src']
        with Image.open(path) as im:
            if im.size!=(1920,1080):raise ValueError((path,im.size))
        files[state['src']]=hashlib.sha256(path.read_bytes()).hexdigest()
manifest=dict(version=2,status='captured-and-reviewed',source='http://127.0.0.1:8765/',publicUrl='https://enagis.netlify.app/',
 requiredBasemap='satellite',savedAnalysisDate='2026-10-10',captureDate='2026-10-20',
 captureMethod='Actual UI screenshots edited into a guided walkthrough; animated camera and cursor in Remotion. Not continuous screen recording.',
 shots=shots,sha256=files)
(ROOT/'src/capture-manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf8')
with (ROOT/'review/exported-shortlist.csv').open(encoding='utf-8-sig',newline='') as f: rows=list(csv.DictReader(f))
dry=sorted([r for r in rows if r['season']=='dry'],key=lambda r:int(r['rank']))
excerpt=[dict(rank=int(r['rank']),name=r['name'],central=round(float(r['kwh_day_central'])),low=round(float(r['kwh_day_p5'])),high=round(float(r['kwh_day_p95'])),question=r['question']) for r in dry[:3]]
(ROOT/'src/export-excerpt.json').write_text(json.dumps(dict(totalRows=len(rows),dryRows=len(dry),rows=excerpt),indent=2),encoding='utf8')
print(f'Indexed {len(files)} verified captures, {len(shots)} scenes, and {len(rows)} exported rows.')
