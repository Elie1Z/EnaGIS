"""Author and voice the separate, exactly two-minute user-story film."""
import asyncio
import inspect
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '.tts-tools'))
import edge_tts

SCENES = [
 ('decision',7,"You're planning a cold store for potato growers. Where should you investigate first?",'-1%'),
 ('place',11,'Search your area and choose cold storage. Here, we open a saved analysis, so every step follows the same example.','+0%'),
 ('ranking',8,'Where first gives you a shortlist. Start with Kora Market, then ask why it deserves attention.','+0%'),
 ('harvest',8,'Harvest shows where crops may come from. These are estimates, built from production statistics and mapped homes.','+0%'),
 ('access',10,'Access follows roads and paths, not straight lines. Switch seasons to see how rain changes who can reach a site.','+0%'),
 ('energy',12,'Energy shows mapped power lines and a possible solar option. Nearby power does not confirm a working connection. That still needs checking.','-1%'),
 ('demand',11,'Open the site card. This example estimates electricity needed on a busy harvest day. The range shows how much that estimate could change.','+0%'),
 ('confidence',11,'How sure repeats the comparison with 300 sets of assumptions. See which sites stay near the top, and which need closer attention.','+0%'),
 ('discover',7,'Likely sites finds places resembling known facilities. These are leads to check, not confirmed businesses.','+0%'),
 ('evidence',9,'Map data reveals gaps. Sources shows where information came from. Unknown does not mean nothing is there.','-1%'),
 ('export',10,'Export the shortlist. Save the analysis. Before investing, check crop volumes, power supply, and local conditions.','-1%'),
 ('outcome',6,'A clearer shortlist. Reasons you can inspect. A practical next step.','+1%'),
 ('outro',10,'EnaGIS. Mapping Energy. Powering Agriculture.','+2%'),
]


async def main():
    out = ROOT / 'public/story/audio'
    out.mkdir(parents=True, exist_ok=True)
    plan = []; start = 0
    for key,duration,text,rate in SCENES:
        plan.append(dict(id=key,startSeconds=start,durationSeconds=duration,text=text,
            rate=rate,voice='en-US-AvaNeural',voiceStartSeconds=3.2 if key=='outro' else .2 if key=='discover' else .25,
            audio=f'story/audio/{key}.mp3'))
        start += duration
    assert start == 120
    semaphore = asyncio.Semaphore(2)

    async def generate(scene):
        async with semaphore:
            file = out / f"{scene['id']}.mp3"
            meta = out / f"{scene['id']}-words.json"
            if scene['id'] == 'outro':
                if (ROOT/'public/v2/audio/close.mp3').exists():
                    shutil.copy2(ROOT/'public/v2/audio/close.mp3', file)
                    shutil.copy2(ROOT/'public/v2/audio/close-words.json', meta)
                assert file.exists() and meta.exists(), 'Keep the approved English-only outro recording with the project'
                print('outro: retained approved English-only Ava motto', flush=True)
                return
            if file.exists() and meta.exists() and scene['id'] not in sys.argv[1:]:
                print('retained', scene['id'], flush=True)
                return
            kwargs = dict(text=scene['text'],voice=scene['voice'],rate=scene['rate'],pitch='+0Hz')
            if 'boundary' in inspect.signature(edge_tts.Communicate).parameters:
                kwargs['boundary']='WordBoundary'
            speech = edge_tts.Communicate(**kwargs)
            words = []
            with file.open('wb') as f:
                async for item in speech.stream():
                    if item['type']=='audio': f.write(item['data'])
                    elif item['type']=='WordBoundary':
                        words.append(dict(text=item['text'],startMs=item['offset']/10000,
                            endMs=(item['offset']+item['duration'])/10000,timestampMs=None,confidence=None))
            assert words and file.stat().st_size>1000
            assert words[-1]['endMs']/1000+scene['voiceStartSeconds'] < scene['durationSeconds'], (scene['id'],words[-1])
            meta.write_text(json.dumps(words,indent=2),encoding='utf8')
            print(f"{scene['id']}: {len(words)} words, final word {words[-1]['endMs']/1000:.2f}s / {scene['durationSeconds']}s",flush=True)

    await asyncio.gather(*(generate(s) for s in plan))
    (ROOT/'story-plan.json').write_text(json.dumps(dict(durationSeconds=120,voice='en-US-AvaNeural',
        provider='Microsoft online neural speech via edge-tts 7.3.1',scenes=plan),indent=2),encoding='utf8')


if __name__=='__main__':
    asyncio.run(main())
