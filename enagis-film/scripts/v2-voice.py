"""Generate the revision's neural female narration and native word timings."""
import asyncio, json, sys, inspect
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'.tts-tools'))
import edge_tts

SCENES=[
 ('hook',6,'Every harvest has potential. Energy helps unlock what comes next.'),
 ('brand',5,'Meet EnaGIS. Mapping Energy. Powering Agriculture.'),
 ('search',11,'Choose your place. Choose your purpose. Cooling. Storage. Milling. Drying. Your next investigation starts on the map.'),
 ('evidence',9,'Turn open maps into a clearer picture of agriculture, people, and the places that connect them.'),
 ('access',10,'Follow real roads. Compare dry and rainy seasons. Understand what each location can reach.'),
 ('energy',14,'Open Energy. See mapped power lines, nearby infrastructure, and an indicative solar option. A mapped line is a lead. Connection and capacity still need checking.'),
 ('demand',13,'Now explore the need. See estimated daily electricity demand, a range of possibilities, and the assumptions behind every number.'),
 ('confidence',11,'Challenge those assumptions across 300 scenarios. See which sites hold their place, and where the evidence needs work.'),
 ('discover',9,'Look beyond recorded locations. Find predicted places worth investigating, with the evidence behind each suggestion.'),
 ('shortlist',9,'Take the next step. Export a ranked shortlist, the evidence, and the questions that turn screening into investigation.'),
 ('close',10,'EnaGIS. Mapping Energy. Powering Agriculture.'),
]

async def main():
    out=ROOT/'public/v2/audio'
    out.mkdir(parents=True,exist_ok=True)
    semaphore=asyncio.Semaphore(2)
    voice='en-US-AvaMultilingualNeural'
    timeline=[];start=0
    for key,duration,text in SCENES:
        timeline.append(dict(id=key,startSeconds=start,durationSeconds=duration,text=text,voice='en-US-AvaNeural' if key in ['brand','close'] else voice,audio=f'v2/audio/{key}.mp3',voiceStartSeconds=3.2 if key=='close' else .35))
        start+=duration
    async def generate(scene):
        async with semaphore:
            path=out/f"{scene['id']}.mp3"
            meta=out/f"{scene['id']}-words.json"
            if path.exists() and path.stat().st_size>1000 and meta.exists():
                print(f"Retained {scene['id']}",flush=True);return
            kwargs=dict(text=scene['text'],voice=scene['voice'],rate='+2%',pitch='+0Hz')
            if 'boundary' in inspect.signature(edge_tts.Communicate).parameters:kwargs['boundary']='WordBoundary'
            communicate=edge_tts.Communicate(**kwargs)
            words=[]
            with path.open('wb') as f:
                async for chunk in communicate.stream():
                    if chunk['type']=='audio':f.write(chunk['data'])
                    elif chunk['type']=='WordBoundary':words.append(dict(text=chunk['text'],startMs=chunk['offset']/10000,endMs=(chunk['offset']+chunk['duration'])/10000,timestampMs=None,confidence=None))
            if path.stat().st_size<1000 or not words:raise RuntimeError(f'Empty narration/timings: {scene["id"]}')
            meta.write_text(json.dumps(words,indent=2),encoding='utf8')
            print(f"Generated {scene['id']}: {len(words)} words, {words[-1]['endMs']/1000:.2f}s",flush=True)
    await asyncio.gather(*(generate(s) for s in timeline))
    (ROOT/'v2-timeline.json').write_text(json.dumps(dict(durationSeconds=start,voice=voice,provider='Microsoft online neural speech via edge-tts 7.3.1',scenes=timeline),indent=2),encoding='utf8')
    print(f'Neural narration complete: {start}s timeline.',flush=True)

if __name__=='__main__':asyncio.run(main())
