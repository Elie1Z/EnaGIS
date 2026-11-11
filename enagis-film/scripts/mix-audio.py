"""Original restrained instrumental score and phrase-aligned Windows speech.

No third-party music or cloned voice. Produces separate editable stems.
"""
import json, wave, math
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
SR=48000
N=110*SR
plan=json.loads((ROOT/'speech-plan.json').read_text())
voice=np.zeros(N,dtype=np.float32)
report=[]
for p in plan:
    with wave.open(str(ROOT/'public/audio/phrases'/f"{p['id']}.wav"),'rb') as w:
        rate=w.getframerate()
        x=np.frombuffer(w.readframes(w.getnframes()),dtype='<i2').astype(np.float32)/32768
    active=np.where(np.abs(x)>0.002)[0]
    if len(active): x=x[max(0,active[0]-int(.025*rate)):min(len(x),active[-1]+int(.075*rate))]
    if rate!=SR: x=np.interp(np.arange(round(len(x)*SR/rate))*rate/SR,np.arange(len(x)),x)
    available=round((p['end']-p['start'])*SR)
    if len(x)>available: raise ValueError(f"Narration exceeds caption: {p['id']}, {len(x)/SR:.2f}s > {available/SR:.2f}s")
    peak=float(np.max(np.abs(x)))
    x=x*(.67/max(peak,.001))
    fade=min(400,len(x)//2)
    x[:fade]*=np.linspace(0,1,fade);x[-fade:]*=np.linspace(1,0,fade)
    start=round(p['start']*SR)
    voice[start:start+len(x)]+=x
    report.append(dict(id=p['id'],start=p['start'],duration=round(len(x)/SR,3),peak=round(float(np.max(np.abs(x))),4)))

music=np.zeros((N,2),dtype=np.float32)
def tone(start,duration,midi,gain=.01,pan=0,pluck=False):
    begin=round(start*SR); length=min(round(duration*SR),N-begin)
    if length<=0:return
    t=np.arange(length,dtype=np.float32)/SR
    hz=440*2**((midi-69)/12)
    if pluck:
        env=(1-np.exp(-t*100))*np.exp(-t/1.0)*np.minimum(1,(duration-t)/.3)
        signal=np.sin(2*np.pi*hz*t)+.23*np.sin(2*np.pi*hz*2*t)*np.exp(-t*2)
    else:
        env=np.minimum(t/1.8,1)*np.minimum((duration-t)/2.2,1)
        signal=(np.sin(2*np.pi*hz*t)+.22*np.sin(2*np.pi*hz*1.002*t)+.12*np.sin(2*np.pi*hz*2*t))
    signal*=np.maximum(0,env)*gain
    music[begin:begin+length,0]+=signal*math.sqrt((1-pan)/2)
    music[begin:begin+length,1]+=signal*math.sqrt((1+pan)/2)

# Original D major / B minor / G / A progression, soft sustained pads and sparse bells.
chords=[[50,57,61,66],[47,54,59,62],[43,55,59,62],[45,57,61,64]]
for bar,start in enumerate(np.arange(0,108,6)):
    chord=chords[bar%4]
    for j,note in enumerate(chord): tone(float(start),8,note,.008,(-.5+j/3),False)
    if 12<=start<102:
        for k in range(4):tone(float(start+.5+1.5*k),3,chord[(bar+k)%4]+24,.012,(-.3 if k%2 else .3),True)
for s,note in [(0,74),(3,78),(6,81),(9,78),(102,74),(104,78),(106,81)]:tone(s,4,note,.022,0,True)
duck=np.ones(N,dtype=np.float32)
for p in plan:
    a=max(0,int((p['start']-.15)*SR));b=min(N,int((p['end']+.2)*SR))
    duck[a:b]=.52
music*=duck[:,None]
fade=np.minimum(np.arange(N)/SR/2,1)*np.minimum((N-np.arange(N))/SR/3.2,1)
music*=fade[:,None]
effects=np.zeros((N,2),dtype=np.float32)
# Subtle editorial click accents corresponding to actual UI actions.
for s in [13.5,18.4,31.5,42.3,51.8,62.1,76.2,94.1]:
    length=int(.065*SR);t=np.arange(length)/SR
    click=.035*np.sin(2*np.pi*(1250*t-2400*t*t))*np.exp(-t*65)
    a=int(s*SR);effects[a:a+length]+=click[:,None]
def save(name,a):
    a=np.asarray(a,dtype=np.float32)
    channels=1 if a.ndim==1 else a.shape[1]
    with wave.open(str(ROOT/'public/audio'/name),'wb') as w:
        w.setnchannels(channels);w.setsampwidth(2);w.setframerate(SR)
        w.writeframes((np.clip(a,-1,1)*32767).astype('<i2').tobytes())
save('narration.wav',voice)
save('original-score.wav',music)
save('interaction-sound.wav',effects)
mix=voice[:,None]+music+effects
save('preview-mix.wav',mix)
(ROOT/'review/audio-qa.json').write_text(json.dumps(dict(duration=110,sampleRate=SR,voice='Microsoft Mark, synthesized',music='Original generated composition',mixPeakDb=round(20*np.log10(float(np.max(np.abs(mix)))),2),clippedSamples=int(np.count_nonzero(abs(mix)>=1)),phrases=report),indent=2))
print(f'110s mix complete. Peak {20*np.log10(np.max(np.abs(mix))):.2f} dBFS; {len(report)} aligned phrases.')
