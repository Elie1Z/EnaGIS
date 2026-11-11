"""Inspect the actual share MP4, including decoded frames and its rendered soundtrack."""
import hashlib
import json
import subprocess
import wave
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT.parent / 'outputs/product-film-v2'
FILE = OUT / 'EnaGIS-Final-1080p.mp4'
FFMPEG = ROOT / 'node_modules/@remotion/compositor-win32-x64-msvc/ffmpeg.exe'
FFPROBE = FFMPEG.with_name('ffprobe.exe')


def run(exe, args):
    result = subprocess.run([str(exe), *map(str, args)], capture_output=True, text=True)
    if result.returncode:
        raise RuntimeError(result.stderr)
    assert not result.stderr.strip(), result.stderr
    return result.stdout


info = json.loads(run(FFPROBE, ['-v', 'error', '-count_frames', '-show_entries',
    'stream=codec_name,codec_type,width,height,avg_frame_rate,nb_read_frames,pix_fmt,sample_rate,channels,duration:format=duration,size',
    '-of', 'json', FILE]))
video = next(s for s in info['streams'] if s['codec_type'] == 'video')
audio = next(s for s in info['streams'] if s['codec_type'] == 'audio')
assert video['codec_name'] == 'h264' and video['pix_fmt'] == 'yuv420p'
assert (video['width'], video['height']) == (1920, 1080)
assert video['avg_frame_rate'] == '30/1' and int(video['nb_read_frames']) == 3210
assert abs(float(info['format']['duration']) - 107) < .05
assert audio['codec_name'] == 'aac' and audio['channels'] == 2
assert int(audio['sample_rate']) == 48000

# Review frames are extracted from the encoded movie, not the editable source.
for name, second in [('purpose', 18.2), ('energy', 50.5), ('outro', 105.5)]:
    run(FFMPEG, ['-hide_banner', '-v', 'error', '-y', '-ss', second,
        '-i', FILE, '-frames:v', 1, ROOT / 'review' / f'final-export-{name}.png'])


def pcm(source, name):
    target = ROOT / 'review' / name
    run(FFMPEG, ['-hide_banner', '-v', 'error', '-y', '-i', source,
        '-vn', '-ar', 12000, '-ac', 1, '-c:a', 'pcm_s16le', target])
    with wave.open(str(target), 'rb') as w:
        return np.frombuffer(w.readframes(w.getnframes()), dtype='<i2').astype(np.float32)/32768


rendered = pcm(FILE, 'final-export-audio-check.wav')
reference = pcm(ROOT / 'public/v2/audio/final-mix.mp3', 'final-reference-audio-check.wav')
n = min(len(rendered), len(reference))
def correlation_at(shift):
    if shift >= 0:
        a, b = rendered[shift:n], reference[:n-shift]
    else:
        a, b = rendered[:n+shift], reference[-shift:n]
    return float(np.dot(a,b) / np.sqrt(np.dot(a,a)*np.dot(b,b)))
# Frame timing may round a half-frame audio start. Permit at most one frame
# when comparing this decoded AAC track with the separately encoded reference.
best_shift = max(range(-400, 401, 12), key=correlation_at)
best_shift = max(range(max(-400,best_shift-12),min(400,best_shift+12)+1), key=correlation_at)
correlation = correlation_at(best_shift)
assert correlation > .95, ('Rendered soundtrack differs from the approved mix', correlation)
peak = float(np.max(np.abs(rendered)))
assert peak < .999, ('Decoded soundtrack clips', peak)
assert len(rendered) / 12000 >= 107

report = dict(status='passed', file=FILE.name, durationSeconds=107,
    resolution='1920x1080', fps=30, decodedVideoFrames=3210, videoCodec='H.264',
    pixelFormat='yuv420p', audioCodec='AAC', audioChannels=2, audioSampleRate=48000,
    soundtrackCorrelationToApprovedMix=round(correlation, 6),
    soundtrackReferenceAlignmentMs=round(best_shift/12, 3),
    decodedAudioPeakDbFS=round(20*float(np.log10(peak)), 2),
    sizeMegabytes=round(FILE.stat().st_size/1e6, 1),
    sha256=hashlib.sha256(FILE.read_bytes()).hexdigest(),
    reviewFrames=['final-export-purpose.png', 'final-export-energy.png', 'final-export-outro.png'])
(OUT / 'final-video-check.json').write_text(json.dumps(report, indent=2), encoding='utf8')
(OUT / 'EnaGIS-Final-1080p.sha256.txt').write_text(f"{report['sha256']}  {FILE.name}\n", encoding='utf8')
print(json.dumps(report, indent=2))
