"""Normalize neural narration and compose an original restrained commercial score."""
import json,math,subprocess,wave
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
SR=48000
ffmpeg=ROOT/'node_modules/@remotion/compositor-win32-x64-msvc/ffmpeg.exe'
timeline=json.loads((ROOT/'src/v2/timeline.json').read_text())
DURATION=timeline['durationSeconds'];N=DURATION*SR
score=np.zeros((N,2),np.float32)
def note(start,duration,midi,gain,pan=0,kind='bell'):
    a=round(start*SR);n=min(round(duration*SR),N-a)
    if n<=0:return
    t=np.arange(n,dtype=np.float32)/SR;f=440*2**((midi-69)/12)
    if kind=='pad':
        env=np.minimum(t/.8,1)*np.minimum((duration-t)/1.3,1)
        sig=np.sin(2*np.pi*f*t)+.14*np.sin(2*np.pi*f*1.003*t)+.1*np.sin(4*np.pi*f*t)
    else:
        env=(1-np.exp(-t*140))*np.exp(-t/(1 if kind=='bell' else .28))*np.minimum((duration-t)/.1,1)
        sig=np.sin(2*np.pi*f*t)+.3*np.sin(4*np.pi*f*t)*np.exp(-t*4)+.07*np.sin(8*np.pi*f*t)*np.exp(-t*8)
    sig*=np.maximum(env,0)*gain
    score[a:a+n,0]+=sig*math.sqrt((1-pan)/2);score[a:a+n,1]+=sig*math.sqrt((1+pan)/2)
rng=np.random.default_rng(20261021)
beat=60/104
chords=[[45,52,57,60],[41,48,53,57],[48,55,60,64],[43,50,55,59]]
for bar,start in enumerate(np.arange(0,DURATION,beat*4)):
    ch=chords[bar%4]
    for i,m in enumerate(ch):note(float(start),beat*4+.9,m,.011,(-.6+i*.4),'pad')
    if 11<=start<97:
        for k in range(8):note(float(start+k*beat/2),1.6,ch[(k+bar)%4]+24,.012,(-.4 if k%2 else .4),'bell')
        for k in range(4):
            a=round((start+k*beat)*SR);n=min(round(.22*SR),N-a);t=np.arange(n)/SR
            kick=.028*np.sin(2*np.pi*(48*t+7*(1-np.exp(-t*28))))*np.exp(-t*26)
            score[a:a+n]+=kick[:,None]
            if k%2:
                a+=round(beat*.01*SR);n=min(round(.1*SR),N-a);t=np.arange(n)/SR
                snap=.005*rng.normal(0,1,n)*np.exp(-t*45)
                score[a:a+n]+=snap[:,None]
        for k in range(8):
            a=round((start+(k+.5)*beat/2)*SR);n=min(round(.045*SR),N-a);t=np.arange(n)/SR
            hat=.0018*rng.normal(0,1,n)*np.exp(-t*80)
            score[a:a+n]+=hat[:,None]
for start,n in [(0,76),(2.4,81),(6,76),(7.2,81),(9,84),(97,76),(98.5,81),(100.2,84)]:note(start,3,n,.028,0,'bell')
# Smooth ducking around the actual narration spans.
duck=np.ones(N,np.float32)
for s in timeline['scenes']:
    offset=s.get('voiceStartSeconds',.35)
    a=int((s['startSeconds']+offset-.2)*SR);b=int((s['startSeconds']+offset+s['audioDurationSeconds']+.15)*SR)
    duck[a:min(N,b)]=.45
running=np.cumsum(np.pad(duck,(1200,1200),mode='edge'),dtype=np.float64)
running=np.insert(running,0,0)
duck=((running[2401:]-running[:-2401])/2401).astype(np.float32)
score*=duck[:,None]
fade=np.minimum(np.arange(N)/SR/1.2,1)*np.minimum((N-np.arange(N))/SR/2.5,1)
score*=fade[:,None]
score*=3.2
effects=np.zeros((N,2),np.float32)
shots=json.loads((ROOT/'src/v2/captures.json').read_text())['shots']
for s in timeline['scenes']:
    if s['id'] in shots:
        for e in shots[s['id']]['events']:
            a=round((s['startSeconds']+e['seconds'])*SR);n=round(.075*SR);t=np.arange(n)/SR
            click=.037*np.sin(2*np.pi*(1450*t-4200*t*t))*np.exp(-t*65)
            effects[a:a+n]+=click[:,None]
    if s['id'] not in ['hook','close']:
        a=round(s['startSeconds']*SR);n=round(.34*SR);t=np.arange(n)/SR
        sweep=.003*rng.normal(0,1,n)*np.sin(np.pi*t/.34)**2
        effects[a:a+n]+=sweep[:,None]
# Four restrained tonal accents follow the purpose words rather than UI clicks.
for seconds,freq in [(14.279,660),(15.174,740),(16.178,831),(17.024,988)]:
    a=round(seconds*SR);n=round(.18*SR);t=np.arange(n)/SR
    bloom=.009*np.sin(2*np.pi*freq*t)*(1-np.exp(-t*130))*np.exp(-t*28)
    effects[a:a+n]+=bloom[:,None]
def save_wav(path,x):
    with wave.open(str(path),'wb') as w:
        w.setnchannels(2);w.setsampwidth(2);w.setframerate(SR);w.writeframes((np.clip(x,-.98,.98)*32767).astype('<i2').tobytes())
def run(args):subprocess.run([str(ffmpeg),'-hide_banner','-loglevel','error','-y',*args],check=True)
for label,audio in [('score',score),('effects',effects)]:
    wav=ROOT/'review'/f'v2-{label}.wav';save_wav(wav,audio)
    run(['-i',str(wav),'-c:a','libmp3lame','-b:a','192k',str(ROOT/'public/v2/audio'/f'{label}.mp3')])
mix=score+effects
for s in timeline['scenes']:
    original=ROOT/'public'/s['audio'];target=original.with_name(s['id']+'-normalized.mp3')
    decoded=ROOT/'review'/f'v2-{s["id"]}-decoded.wav'
    run(['-i',str(original),'-ar',str(SR),'-ac','1','-c:a','pcm_s16le',str(decoded)])
    with wave.open(str(decoded),'rb') as w:
        v=np.frombuffer(w.readframes(w.getnframes()),dtype='<i2').astype(np.float32)/32768
    active=v[np.abs(v)>.008]
    rms=float(np.sqrt(np.mean(active*active)))
    gain=min(.78/max(.001,float(np.max(np.abs(v)))),.12/max(.001,rms))
    v*=gain
    wav=ROOT/'review'/f'v2-{s["id"]}-normalized.wav'
    with wave.open(str(wav),'wb') as w:
        w.setnchannels(1);w.setsampwidth(2);w.setframerate(SR);w.writeframes((v*32767).astype('<i2').tobytes())
    run(['-i',str(wav),'-c:a','libmp3lame','-b:a','192k',str(target)])
    a=round((s['startSeconds']+s.get('voiceStartSeconds',.35))*SR)
    mix[a:a+len(v)]+=v[:,None]
save_wav(ROOT/'review/v2-final-mix.wav',mix)
run(['-i',str(ROOT/'review/v2-final-mix.wav'),'-c:a','libmp3lame','-b:a','256k',str(ROOT/'public/v2/audio/final-mix.mp3')])
qa=dict(durationSeconds=DURATION,sampleRate=SR,voice=timeline['voice'],mottoVoice='en-US-AvaNeural (English-only)',clippedSamples=int(np.count_nonzero(np.abs(mix)>=1)),mixPeakDb=round(float(20*np.log10(np.max(np.abs(mix)))),2),music='Original 104 BPM procedural commercial score',speech='Neural female voice, normalized per scene')
assert qa['clippedSamples']==0,qa
(ROOT/'review/v2-audio-qa.json').write_text(json.dumps(qa,indent=2),encoding='utf8')
print(json.dumps(qa))
