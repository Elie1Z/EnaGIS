import {CanvasImage,Easing,interpolate,staticFile,useCurrentFrame,useVideoConfig} from "remotion";
import data from "./captures.json";

type Event={seconds:number;x:number;y:number;rect:{x:number;y:number;w:number;h:number};label:string};
type Shot={states:{seconds:number;image:string}[];events:Event[];camera:string};
const shots=data.shots as Record<string,Shot>;
const files=data.files as Record<string,{src:string}>;
const W=1260,H=661.5;
const ease=Easing.bezier(.65,0,.35,1);
const clamp=(x:number,a:number,b:number)=>Math.min(b,Math.max(a,x));
const cameras=(id:string)=>{
 const full={x:640,y:336,z:1};
 if(id==="place")return [{t:0,x:640,y:260,z:1.04},{t:6.1,x:640,y:260,z:1.04},{t:7.3,...full},{t:11,...full}];
 if(id==="ranking")return [{t:0,...full},{t:5.2,...full},{t:6.5,x:860,y:330,z:1.08},{t:8,x:860,y:330,z:1.08}];
 if(id==="energy")return [{t:0,...full},{t:6.2,...full},{t:7.5,x:880,y:380,z:1.08},{t:12,x:880,y:380,z:1.08}];
 if(id==="demand")return [{t:0,...full},{t:2.2,...full},{t:3.5,x:880,y:330,z:1.08},{t:11,x:880,y:330,z:1.08}];
 if(id==="discover")return [{t:0,...full},{t:5,...full},{t:6.2,x:880,y:330,z:1.06},{t:7,x:880,y:330,z:1.06}];
 return [{t:0,...full},{t:15,...full}];
};

export const StoryCapture=({id}:{id:string})=>{
 const f=useCurrentFrame();const {fps}=useVideoConfig();const t=f/fps;
 const shot=shots[id];
 const current=[...shot.states].reverse().find(s=>s.seconds<=t)??shot.states[0];
 const camera=cameras(id).map(k=>{
  const scale=W/1280*k.z;
  return {t:k.t,scale,left:clamp(W/2-k.x*scale,W-1280*scale,0),top:clamp(H/2-k.y*scale,H-672*scale,0)};
 });
 const times=camera.map(k=>k.t);
 const settings={easing:ease,extrapolateLeft:"clamp" as const,extrapolateRight:"clamp" as const};
 const scale=interpolate(t,times,camera.map(k=>k.scale),settings);
 const left=interpolate(t,times,camera.map(k=>k.left),settings);
 const top=interpolate(t,times,camera.map(k=>k.top),settings);
 const e=shot.events.find(e=>t>=e.seconds-.85&&t<=e.seconds+.75);
 const p=e?ease(clamp((t-(e.seconds-.75))/.42,0,1)):0;
 const x=e?e.x+(1-p)*Math.min(90,1250-e.x):0;
 const y=e?e.y+(1-p)*Math.min(65,640-e.y):0;
 const opacity=e?interpolate(t,[e.seconds-.85,e.seconds-.7,e.seconds+.42,e.seconds+.75],[0,1,1,0],settings):0;
 const click=e?clamp((t-e.seconds)/.4,0,1):0;
 return <div style={{position:"absolute",left,top,width:1280,height:672,scale,transformOrigin:"top left"}}>
  {shot.states.map(s=><CanvasImage name={`Real app · ${s.image}`} key={s.image} src={staticFile(files[s.image].src)} premountFor={fps}
   style={{position:"absolute",inset:0,width:1280,height:672,opacity:current.image===s.image?1:0}}/>)}
  {e?<>
   <svg width={1280} height={672} style={{position:"absolute",inset:0,opacity,pointerEvents:"none"}}>
    <defs><mask id={`story-focus-${id}`}><rect width={1280} height={672} fill="white"/><rect x={e.rect.x-7} y={e.rect.y-7} width={e.rect.w+14} height={e.rect.h+14} rx={9} fill="black"/></mask></defs>
    <rect width={1280} height={672} fill="#031C2E" opacity={.16} mask={`url(#story-focus-${id})`}/>
    <rect x={e.rect.x-4} y={e.rect.y-4} width={e.rect.w+8} height={e.rect.h+8} rx={8} fill="none" stroke="#06E0B0" strokeWidth={1.7}/>
    {click>0&&click<1?<circle cx={e.x} cy={e.y} r={8+24*click} fill="none" stroke="#06E0B0" strokeWidth={2} opacity={1-click}/>:null}
   </svg>
   <svg width={23} height={29} viewBox="0 0 50 62" style={{position:"absolute",left:x-2,top:y-2,opacity,
    scale:e&&t>=e.seconds&&t<e.seconds+.16?.86:1,transformOrigin:"top left",filter:"drop-shadow(0 2px 2px #031C2E70)"}}>
    <path d="M4 3L4 45L15 35L25 57L33 53L23 32L39 32Z" fill="white" stroke="#032536" strokeWidth={2.8}/>
   </svg>
  </>:null}
 </div>;
};
