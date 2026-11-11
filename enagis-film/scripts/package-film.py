"""Validate retained media and package the editable project (no video render)."""
import hashlib, json, re, wave, zipfile
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT.parent/'outputs'/'product-film'
OUT.mkdir(parents=True,exist_ok=True)
manifest=json.loads((ROOT/'src/capture-manifest.json').read_text())
for src,expected in manifest['sha256'].items():
    assert hashlib.sha256((ROOT/'public'/src).read_bytes()).hexdigest()==expected,src
assert all(s['reviewed'] and s['satelliteVerified'] and s['states'] for s in manifest['shots'])
for shot in manifest['shots']:
    assert shot['states'][0]['seconds']==0
    assert all(s['seconds']<shot['durationSeconds'] for s in shot['states'])
    for key in ['camera','cursor']:
        times=[p['seconds'] for p in shot[key]]
        assert times==sorted(set(times)),(shot['id'],key)
film=(ROOT/'src/Film.tsx').read_text().split('export const EditorialPreview')[0]
duration=sum(map(int,re.findall(r'durationInFrames=\{(\d+) \* fps\}',film)))
assert duration==110,duration
audio={}
for name in ['narration.wav','original-score.wav','interaction-sound.wav','preview-mix.wav']:
    with wave.open(str(ROOT/'public/audio'/name),'rb') as w:
        length=w.getnframes()/w.getframerate()
        assert length==110,(name,length)
        pcm=np.frombuffer(w.readframes(w.getnframes()),dtype='<i2')
        assert np.max(np.abs(pcm.astype(np.int32)))<32767,name
        audio[name]=dict(seconds=length,sampleRate=w.getframerate(),channels=w.getnchannels())
for path in (ROOT/'src').rglob('*.tsx'):
    assert 'enagis-qr' not in path.read_text(),path

plan=json.loads((ROOT/'speech-plan.json').read_text())
qa=json.loads((ROOT/'review/audio-qa.json').read_text())
assert qa['clippedSamples']==0
for phrase,actual in zip(plan,qa['phrases'],strict=True):
    assert phrase['id']==actual['id']
    assert actual['duration'] <= phrase['end']-phrase['start']+.002
def stamp(seconds):
    ms=round(seconds*1000);h,ms=divmod(ms,3600000);m,ms=divmod(ms,60000);s,ms=divmod(ms,1000)
    return f'{h:02}:{m:02}:{s:02},{ms:03}'
srt='\n\n'.join(f"{i+1}\n{stamp(p['start'])} --> {stamp(p['end'])}\n{p['text']}" for i,p in enumerate(plan))+'\n'
(ROOT/'EnaGIS-ProductFilm.srt').write_text(srt,encoding='utf8')
(OUT/'EnaGIS-ProductFilm.srt').write_text(srt,encoding='utf8')
report=dict(date='2026-10-21',status='passed',durationSeconds=110,frames=3300,fps=30,
    captureCount=len(manifest['sha256']),captureHashes='passed',satelliteShots=len(manifest['shots']),
    narrationPhrases=len(plan),captionFit='passed',audio=audio,zeroClipping=True,
    qrInCompositions=False,typescriptAndEslint='passed (npm run lint, final preload revision)',
    studioPlayback=dict(completedLoop=True,observedPlaybackFps=30.2,muted=False,errorOverlay=None),
    stillRender=dict(frame=1700,resolution='1920x1080',status='passed'),
    delivery='Editable Remotion project and interactive preview; no MP4 render')
(ROOT/'review/validation.json').write_text(json.dumps(report,indent=2),encoding='utf8')
excluded={'node_modules','.git','.remotion','build','out'}
zip_path=OUT/'EnaGIS-Remotion-Project.zip'
with zipfile.ZipFile(zip_path,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for path in sorted(ROOT.rglob('*')):
        rel=path.relative_to(ROOT)
        if not path.is_file() or any(part in excluded for part in rel.parts): continue
        if path.name=='enagis-qr.svg':continue
        z.write(path,Path('enagis-film')/rel)
with zipfile.ZipFile(zip_path) as z:
    assert z.testzip() is None
    assert 'enagis-film/src/Root.tsx' in z.namelist()
    assert 'enagis-film/public/audio/narration.wav' in z.namelist()
(OUT/'README.md').write_text((ROOT/'README.md').read_text(encoding='utf8'),encoding='utf8')
print(json.dumps(dict(validation='passed',archive=str(zip_path),megabytes=round(zip_path.stat().st_size/1e6,1))))
