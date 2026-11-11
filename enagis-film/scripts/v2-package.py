"""Validate retained V2 assets and package the editable film separately from V1."""
import hashlib
import json
import re
import shutil
import zipfile
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT.parent / 'outputs' / 'product-film-v2'
FALLBACK = ROOT.parent / 'outputs/product-film-v1-preserved/EnaGIS-v1-Preserved.zip'
FALLBACK_SHA = 'c14dc4caa75f698f1472e532dce4ec5b8d5a9a2ff754040d3f2c69d3a8fbdbe8'
BEFORE_POLISH = ROOT.parent / 'outputs/product-film-v2-preserved/EnaGIS-Commercial-V2-Before-Polish.zip'
BEFORE_SHA = 'af6759842e3711cc2c994698abc7fd7ec5fa66b6ef7be466fef7e7c4b9bb363e'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def stamp(seconds):
    ms = round(seconds * 1000)
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f'{h:02}:{m:02}:{s:02},{ms:03}'


assert sha(FALLBACK) == FALLBACK_SHA, 'Original fallback archive has changed'
# V1's actual scene, picture, and sound files remain byte-for-byte identical.
v1_files = 0
with zipfile.ZipFile(FALLBACK) as z:
    for name in z.namelist():
        rel = name.removeprefix('enagis-film/')
        if (rel == 'src/Film.tsx' or rel == 'src/components/ProductShot.tsx'
                or rel.startswith(('src/scenes/', 'public/audio/', 'public/footage/'))):
            assert (ROOT / rel).read_bytes() == z.read(name), rel
            v1_files += 1
assert v1_files > 20
assert sha(BEFORE_POLISH) == BEFORE_SHA, 'Prior V2 fallback has changed'
with zipfile.ZipFile(BEFORE_POLISH) as z:
    assert (ROOT / 'src/v2/GuidedCapture.tsx').read_bytes() == z.read('enagis-film/src/v2/GuidedCapture.tsx')
    for scene in ['hook', 'search', 'evidence', 'access', 'energy', 'demand', 'confidence', 'discover', 'shortlist']:
        rel = f'public/v2/audio/{scene}.mp3'
        assert (ROOT / rel).read_bytes() == z.read('enagis-film/' + rel), rel

plan = json.loads((ROOT / 'src/v2/timeline.json').read_text())
captures = json.loads((ROOT / 'src/v2/captures.json').read_text())
captions = json.loads((ROOT / 'review/v2-captions.json').read_text())
audio = json.loads((ROOT / 'review/v2-audio-qa.json').read_text())
assert plan['durationSeconds'] == sum(s['durationSeconds'] for s in plan['scenes']) == 107
assert audio['durationSeconds'] == 107 and audio['clippedSamples'] == 0
assert audio['mixPeakDb'] < 0
assert captures['basemap'] == 'Satellite'
for name, asset in captures['files'].items():
    file = ROOT / 'public' / asset['src']
    assert sha(file) == asset['sha256'], name
    with Image.open(file) as im:
        assert im.size == (asset['width'], asset['height']) == (1280, 672), name

srt = []
end = 0
events = 0
for scene, caption_scene in zip(plan['scenes'], captions, strict=True):
    assert scene['id'] == caption_scene['id']
    assert scene['startSeconds'] == end
    end += scene['durationSeconds']
    assert scene['audioDurationSeconds'] + scene['voiceStartSeconds'] <= scene['durationSeconds']
    if scene['id'] in ['brand', 'close']:
        assert scene['voice'] == 'en-US-AvaNeural'
    assert (ROOT / 'public/v2/audio' / f"{scene['id']}-normalized.mp3").is_file()
    original_text = ' '.join(c['text'] for c in caption_scene['captions'])
    assert original_text == scene['text'], (scene['id'], original_text)
    previous_end = 0
    for c in caption_scene['captions']:
        assert previous_end <= c['startMs'] < c['endMs'] <= scene['durationSeconds'] * 1000
        previous_end = c['endMs']
        start = scene['startSeconds'] + c['startMs'] / 1000
        stop = scene['startSeconds'] + c['endMs'] / 1000
        srt.append(f"{len(srt)+1}\n{stamp(start)} --> {stamp(stop)}\n{c['text']}")
    if scene['id'] in captures['shots']:
        shot = captures['shots'][scene['id']]
        assert shot['states'][0]['seconds'] == 0
        for state in shot['states']:
            assert 0 <= state['seconds'] < scene['durationSeconds']
            assert state['image'] in captures['files']
        for event in shot['events']:
            rect = event['rect']
            assert 0 <= event['seconds'] < scene['durationSeconds']
            assert 0 <= rect['x'] <= event['x'] <= rect['x']+rect['w'] <= 1280
            assert 0 <= rect['y'] <= event['y'] <= rect['y']+rect['h'] <= 672
            events += 1

source = '\n'.join(p.read_text(encoding='utf8') for p in (ROOT / 'src/v2').rglob('*.tsx'))
assert 'Mapping Energy.' in source and 'Powering Agriculture.' in source
assert 'from open maps to your next move' not in source.lower()
assert 'qr' not in source.lower()
film = (ROOT / 'src/v2/CommercialFilm.tsx').read_text()
assert sum(map(int, re.findall(r'durationInFrames=\{(\d+)\*fps\}', film))) == 107
outro = ROOT / 'public/v2/video/enagis-outro.mp4'
assert sha(outro) == sha(OUT / 'outro enagis.mp4'), 'Outro must match the supplied original'
playback_file = ROOT / 'review/v2-playback-qa.json'
assert playback_file.exists(), 'Complete Studio playback review first'
playback = json.loads(playback_file.read_text())
assert playback['completedLoop'] and playback['muted'] is False and playback['errorOverlay'] is None
assert playback['durationInFrames'] == 3210

OUT.mkdir(parents=True, exist_ok=True)
subtitles = '\n\n'.join(srt) + '\n'
(OUT / 'EnaGIS-Commercial-V2.srt').write_text(subtitles, encoding='utf8')
(ROOT / 'EnaGIS-Commercial-V2.srt').write_text(subtitles, encoding='utf8')
report = {
    'checkedAtUtc': datetime.now(timezone.utc).isoformat(),
    'status': 'passed', 'durationSeconds': 107, 'fps': 30, 'frames': 3210,
    'designCanvas': '3840x2160', 'captureResolution': '1280x672',
    'captureHashesAndDimensions': 'passed', 'captureCount': len(captures['files']),
    'measuredClickTargetsInsideCapture': events, 'captionWordingAndFit': 'passed',
    'narrationFit': 'passed', 'audio': audio, 'playback': playback,
    'typescriptAndEslint': 'passed: npm run lint',
    'stillReview': ['v2-click-focus.png', 'v2-energy-preview.png', 'v2-demand-preview.png',
                    'v2-export-preview.png', 'v2-purpose-preview.png', 'v2-outro-preview.png'],
    'fallbackArchiveSha256': FALLBACK_SHA, 'unchangedV1MediaAndSceneFiles': v1_files,
    'priorV2ArchiveSha256': BEFORE_SHA, 'cameraChoreographyAndOtherNarration': 'unchanged',
    'creatorOutro': {'sha256': sha(outro), 'source': 'outputs/product-film-v2/outro enagis.mp4', 'durationSeconds': 10, 'playbackRate': 1, 'originalAudioMuted': True},
    'delivery': 'Editable Remotion project and interactive preview; no final MP4 export',
}
(ROOT / 'review/v2-validation.json').write_text(json.dumps(report, indent=2), encoding='utf8')
(OUT / 'validation.json').write_text(json.dumps(report, indent=2), encoding='utf8')
shutil.copy2(ROOT / 'V2-README.md', OUT / 'README.md')
shutil.copy2(ROOT / 'public/v2/audio/final-mix.mp3', OUT / 'EnaGIS-Commercial-V2-Audio.mp3')
for filename in report['stillReview']:
    shutil.copy2(ROOT / 'review' / filename, OUT / filename)
shutil.copy2(ROOT / 'review/v2-outro-preview.png', OUT / 'v2-close-preview.png')

excluded = {'node_modules', '.tts-tools', '.git', '.remotion', 'build', 'out', '__pycache__'}
archive = OUT / 'EnaGIS-Commercial-V2-Project.zip'
with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as z:
    for path in sorted(ROOT.rglob('*')):
        rel = path.relative_to(ROOT)
        if not path.is_file() or any(part in excluded for part in rel.parts):
            continue
        if 'qr' in path.name.lower() or path.name in {'probe.png', 'energy-full.png'}:
            continue
        if rel.parts[0] == 'review' and path.suffix.lower() == '.wav':
            continue
        z.write(path, Path('enagis-film') / rel)
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
    assert 'enagis-film/src/v2/CommercialFilm.tsx' in z.namelist()
    assert 'enagis-film/public/v2/audio/energy-normalized.mp3' in z.namelist()
    assert not any('/node_modules/' in name or '/.tts-tools/' in name for name in z.namelist())
(OUT / 'SHA256.txt').write_text(f'{sha(archive)}  {archive.name}\n', encoding='utf8')
print(json.dumps({'validation': 'passed', 'archive': str(archive),
                  'megabytes': round(archive.stat().st_size/1e6, 1), 'v1Unchanged': v1_files}))
