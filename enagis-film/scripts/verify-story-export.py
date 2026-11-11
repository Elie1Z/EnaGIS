"""Check the actual two-minute demo MP4 and its complete rendered soundtrack."""
import hashlib,json,subprocess,wave
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT.parent/'outputs/user-story-demo'
FILE=OUT/'EnaGIS-User-Story-Demo-2min.mp4'
FFMPEG=ROOT/'node_modules/@remotion/compositor-win32-x64-msvc/ffmpeg.exe'
PROBE=FFMPEG.with_name('ffprobe.exe')

def run(exe,args):
    result=subprocess.run([str(exe),*map(str,args)],capture_output=True,text=True)
    if result.returncode:raise RuntimeError(result.stderr)
    assert not result.stderr.strip(),result.stderr
    return result.stdout

def boxes(path):
    found={}
    with path.open('rb') as f:
        while f.tell()<path.stat().st_size:
            at=f.tell();size=int.from_bytes(f.read(4),'big');kind=f.read(4).decode('ascii',errors='replace')
            header=8
            if size==1:size=int.from_bytes(f.read(8),'big');header=16
            if size==0:size=path.stat().st_size-at
            assert size>=header,(kind,size)
            found[kind]=at;f.seek(at+size)
    return found

atoms=boxes(FILE)
if atoms['moov']>atoms['mdat']:
    temp=OUT/'streaming-final.mp4'
    run(FFMPEG,['-hide_banner','-v','error','-y','-i',FILE,'-map','0','-c','copy','-movflags','+faststart',temp])
    temp.replace(FILE)
assert boxes(FILE)['moov']<boxes(FILE)['mdat']
info=json.loads(run(PROBE,['-v','error','-count_frames','-show_entries',
    'stream=codec_name,codec_type,width,height,avg_frame_rate,nb_read_frames,pix_fmt,sample_rate,channels,duration:format=duration,size',
    '-of','json',FILE]))
v=next(s for s in info['streams'] if s['codec_type']=='video')
a=next(s for s in info['streams'] if s['codec_type']=='audio')
assert v['codec_name']=='h264' and v['pix_fmt']=='yuv420p'
assert (v['width'],v['height'])==(1920,1080)
assert v['avg_frame_rate']=='30/1' and int(v['nb_read_frames'])==3600
assert abs(float(info['format']['duration'])-120)<.05
assert a['codec_name']=='aac' and a['channels']==2 and int(a['sample_rate'])==48000
for name,t in [('opening',3),('demand',63),('verification',102),('outro',118.5)]:
    run(FFMPEG,['-hide_banner','-v','error','-y','-ss',t,'-i',FILE,'-frames:v',1,ROOT/'review'/f'story-final-{name}.png'])

def pcm(source,name):
    target=ROOT/'review'/name
    run(FFMPEG,['-hide_banner','-v','error','-y','-i',source,'-vn','-ar','12000','-ac','1','-c:a','pcm_s16le',target])
    with wave.open(str(target),'rb') as f:return np.frombuffer(f.readframes(f.getnframes()),dtype='<i2').astype(np.float32)/32768
x=pcm(FILE,'story-export-audio-check.wav')
y=pcm(ROOT/'public/story/audio/final-mix.mp3','story-reference-audio-check.wav')
n=min(len(x),len(y))
def corr(shift):
    if shift>=0:a,b=x[shift:n],y[:n-shift]
    else:a,b=x[:n+shift],y[-shift:n]
    return float(np.dot(a,b)/np.sqrt(np.dot(a,a)*np.dot(b,b)))
shift=max(range(-400,401,12),key=corr)
shift=max(range(max(-400,shift-12),min(400,shift+12)+1),key=corr)
correlation=corr(shift)
assert correlation>.95,correlation
peak=float(np.max(np.abs(x)));assert peak<.999
assert len(x)/12000>=120
sha=hashlib.sha256(FILE.read_bytes()).hexdigest()
report=dict(status='passed',file=FILE.name,durationSeconds=120,resolution='1920x1080',fps=30,
    decodedVideoFrames=3600,videoCodec='H.264',audioCodec='AAC',audioChannels=2,audioSampleRate=48000,
    fastStart=True,soundtrackCorrelationToApprovedMix=round(correlation,6),
    soundtrackReferenceAlignmentMs=round(shift/12,3),decodedAudioPeakDbFS=round(20*float(np.log10(peak)),2),
    sizeMegabytes=round(FILE.stat().st_size/1e6,1),sha256=sha,outroStartsAt=110,outroEndsAt=120,
    reviewFrames=['story-final-opening.png','story-final-demand.png','story-final-verification.png','story-final-outro.png'])
(OUT/'final-video-check.json').write_text(json.dumps(report,indent=2),encoding='utf8')
(OUT/'Final-video.sha256.txt').write_text(f'{sha}  {FILE.name}\n',encoding='utf8')
print(json.dumps(report,indent=2))
