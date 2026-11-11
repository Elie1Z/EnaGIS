"""Replace only motto clips with English-only Ava; retain the approved main narration."""
import asyncio
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '.tts-tools'))
import edge_tts


async def main():
    plan = json.loads((ROOT / 'v2-timeline.json').read_text())
    for scene in plan['scenes']:
        if scene['id'] == 'close':
            scene['durationSeconds'] = 10
        if scene['id'] not in ['brand', 'close']:
            continue
        scene['voice'] = 'en-US-AvaNeural'
        output = ROOT / 'public' / scene['audio']
        words = []
        speech = edge_tts.Communicate(scene['text'], voice=scene['voice'],
                                     rate='+2%', pitch='+0Hz', boundary='WordBoundary')
        with output.open('wb') as f:
            async for item in speech.stream():
                if item['type'] == 'audio':
                    f.write(item['data'])
                elif item['type'] == 'WordBoundary':
                    words.append(dict(text=item['text'], startMs=item['offset']/10000,
                                      endMs=(item['offset']+item['duration'])/10000,
                                      timestampMs=None, confidence=None))
        assert len(words) == len(scene['text'].split()), (scene['id'], words)
        output.with_name(scene['id']+'-words.json').write_text(json.dumps(words, indent=2))
        print(scene['id'], scene['voice'], words[-1]['endMs']/1000, flush=True)
    plan['durationSeconds'] = sum(s['durationSeconds'] for s in plan['scenes'])
    plan['mottoVoice'] = 'en-US-AvaNeural (English-only)'
    (ROOT / 'v2-timeline.json').write_text(json.dumps(plan, indent=2), encoding='utf8')


if __name__ == '__main__':
    asyncio.run(main())
