"""Prepare phrase-aligned narration from the film's visible captions."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
def cap(text, start, end):
    return dict(text=text, startMs=start, endMs=end, timestampMs=None, confidence=None, pageBreakAfter=True)
scenes = [
    dict(id='harvest', startSeconds=0, captions=[cap('A harvest is only the beginning.',200,2700),cap('What happens next depends on energy.',3000,5800)]),
    dict(id='introduce', startSeconds=6, captions=[cap('But where should agricultural energy investment begin?',100,3400),cap('Meet EnaGIS.',3700,5700)]),
    *json.loads((ROOT/'caption-timing.json').read_text()),
    dict(id='close', startSeconds=102, captions=[cap('EnaGIS. From open maps to your next move.',200,4500)]),
]
plan=[]
for scene in scenes:
    for i,c in enumerate(scene['captions']):
        plan.append(dict(id=f"{scene['id']}-{i}", text=c['text'], spokenText=c['text'].replace('EnaGIS','Enna Jiss'),
                         start=scene['startSeconds']+c['startMs']/1000, end=scene['startSeconds']+c['endMs']/1000))
(ROOT/'public/audio/phrases').mkdir(parents=True,exist_ok=True)
(ROOT/'speech-plan.json').write_text(json.dumps(plan,indent=2),encoding='utf8')
print(f'{len(plan)} phrases ready; 110 second timeline.')
