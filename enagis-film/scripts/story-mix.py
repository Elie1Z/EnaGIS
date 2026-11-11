"""Mix the two-minute story: consistent speech, quiet original score, real click cues."""
import json,math,subprocess,wave
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
SR=48000;DURATION=120;N=SR*DURATION
ffmpeg=ROOT/'node_modules/@remotion/compositor-win32-x64-msvc/ffmpeg.exe'
plan=json.loads((ROOT/'src/story/timeline.json').read_text())
shots=json.loads((ROOT/'src/story/captures.json').read_text())['shots']
score=np.zeros((N,2),np.float32)
effects=np.zeros_like(score)
rng=np.random.default_rng(20261021)

def note(start,duration,midi,gain,pan=0,pad=False):
    a=round(start*SR);n=min(round(duration*SR),N-a)
    if n<=0:return
    t=np.arange(n,dtype=np.float32)/SR;freq=440*2**((midi-69)/12)
    if pad:
        env=np.minimum(t/.7,1)*np.maximum(0,np.minimum((duration-t)/1,1))
        sig=np.sin(2*np.pi*freq*t)+.12*np.sin(2*np.pi*freq*1.004*t)
    else:
        env=(1-np.exp(-t*120))*np.exp(-t/.7)*np.maximum(0,np.minimum((duration-t)/.1,1))
        sig=np.sin(2*np.pi*freq*t)+.2*np.sin(4*np.pi*freq*t)*np.exp(-t*5)
    sig*=env*gain
    score[a:a+n,0]+=sig*math.sqrt((1-pan)/2)
    score[a:a+n,1]+=sig*math.sqrt((1+pan)/2)

beat=60/96
chords=[[45,52,57,60],[41,48,53,57],[48,55,60,64],[43,50,55,59]]
for bar,start in enumerate(np.arange(0,DURATION,4*beat)):
    ch=chords[bar%4]
    for i,m in enumerate(ch):note(float(start),4*beat+.7,m,.016,(-.6+i*.4),True)
    if 7<=start<110:
        for k in range(4):note(float(start+(k+.5)*beat),1.8,ch[(k+bar)%4]+24,.011,-.35 if k%2 else .35)
        for k in [0,2]:
            a=round((start+k*beat)*SR);n=min(round(.18*SR),N-a);t=np.arange(n)/SR
            pulse=.017*np.sin(2*np.pi*(45*t+6*(1-np.exp(-30*t))))*np.exp(-t*25)
            score[a:a+n]+=pulse[:,None]
for t,m in [(0,76),(2.2,81),(5,84),(104,76),(106.1,81),(110,76),(112.2,81),(115,84)]:note(t,3,m,.035)

duck=np.ones(N,np.float32)
for s in plan['scenes']:
    a=int((s['startSeconds']+s['voiceStartSeconds']-.15)*SR)
    b=int((s['startSeconds']+s['voiceStartSeconds']+s['audioDurationSeconds']+.15)*SR)
    duck[max(0,a):min(N,b)]=.43
    if s['id'] in shots:
        for e in shots[s['id']]['events']:
            a=round((s['startSeconds']+e['seconds'])*SR);n=round(.065*SR);t=np.arange(n)/SR
            click=.031*np.sin(2*np.pi*(1450*t-4200*t*t))*np.exp(-t*65)
            effects[a:a+n]+=click[:,None]
    if s['id'] not in ['decision','outro']:
        a=round(s['startSeconds']*SR);n=round(.32*SR);t=np.arange(n)/SR
        sweep=.0025*rng.normal(0,1,n)*np.sin(np.pi*t/.32)**2
        effects[a:a+n]+=sweep[:,None]
running=np.insert(np.cumsum(np.pad(duck,(1200,1200),mode='edge'),dtype=np.float64),0,0)
duck=((running[2401:]-running[:-2401])/2401).astype(np.float32)
fade=np.minimum(np.arange(N)/SR/.8,1)*np.minimum((N-np.arange(N))/SR/2.3,1)
score*=duck[:,None]*fade[:,None]*2.1

def run(args):subprocess.run([str(ffmpeg),'-hide_banner','-v','error','-y',*map(str,args)],check=True)
def wav(path,x):
    with wave.open(str(path),'wb') as w:
        w.setnchannels(x.shape[1] if x.ndim==2 else 1);w.setsampwidth(2);w.setframerate(SR)
        w.writeframes((np.clip(x,-.98,.98)*32767).astype('<i2').tobytes())
for label,x in [('score',score),('effects',effects)]:
    temp=ROOT/'review'/f'story-{label}.wav';wav(temp,x)
    run(['-i',temp,'-c:a','libmp3lame','-b:a','192k',ROOT/'public/story/audio'/f'{label}.mp3'])
mix=score+effects
for s in plan['scenes']:
    src=ROOT/'public'/s['audio'];temp=ROOT/'review'/f'story-{s["id"]}-decoded.wav'
    run(['-i',src,'-ac','1','-ar',SR,'-c:a','pcm_s16le',temp])
    with wave.open(str(temp),'rb') as w:v=np.frombuffer(w.readframes(w.getnframes()),dtype='<i2').astype(np.float32)/32768
    active=v[np.abs(v)>.008];rms=float(np.sqrt(np.mean(active*active)))
    gain=min(.78/max(.001,float(np.max(np.abs(v)))),.12/max(.001,rms));v*=gain
    norm=ROOT/'review'/f'story-{s["id"]}-normalized.wav';wav(norm,v)
    run(['-i',norm,'-c:a','libmp3lame','-b:a','192k',src.with_name(s['id']+'-normalized.mp3')])
    a=round((s['startSeconds']+s['voiceStartSeconds'])*SR)
    assert a+len(v)<=N
    mix[a:a+len(v)]+=v[:,None]
wav(ROOT/'review/story-final-mix.wav',mix)
run(['-i',ROOT/'review/story-final-mix.wav','-c:a','libmp3lame','-b:a','256k',ROOT/'public/story/audio/final-mix.mp3'])
qa=dict(durationSeconds=120,sampleRate=SR,voice='en-US-AvaNeural (English-only)',
    clippedSamples=int(np.count_nonzero(np.abs(mix)>=1)),peakDbFS=round(float(20*np.log10(np.max(np.abs(mix)))),2),
    score='Original 96 BPM procedural composition; ducked under speech',effects='Measured actual control clicks and soft chapter accents')
assert qa['clippedSamples']==0
(ROOT/'review/story-audio-qa.json').write_text(json.dumps(qa,indent=2),encoding='utf8')
print(json.dumps(qa))
