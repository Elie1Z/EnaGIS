import {CanvasImage,Easing,interpolate,staticFile,useCurrentFrame,useVideoConfig} from "remotion";
import manifest from "./captures.json";

type Event={seconds:number;x:number;y:number;rect:{x:number;y:number;w:number;h:number};label:string};
type Shot={states:{seconds:number;image:string}[];events:Event[]};
type Point={t:number;x:number;y:number;z:number};
const shots=manifest.shots as Record<string,Shot>;
const images=manifest.files as Record<string,{src:string;width:number;height:number}>;
const W=2624,H=1392;
const ease=Easing.bezier(.65,0,.35,1);
const clamp=(v:number,a:number,b:number)=>Math.min(b,Math.max(a,v));
const interpolateKeys=(t:number,keys:number[],values:number[])=>interpolate(t,keys,values,{easing:ease,extrapolateLeft:"clamp",extrapolateRight:"clamp"});

const cameraFor=(id:string):Point[]=>{
 const full={x:640,y:336,z:1};
 if(id==="search")return [{t:0,...full},{t:1,x:620,y:180,z:1.18},{t:7.4,x:620,y:180,z:1.18},{t:8.6,...full},{t:11,...full}];
 if(id==="energy")return [{t:0,...full},{t:1,x:500,y:300,z:1.12},{t:8.8,x:500,y:300,z:1.12},{t:10.2,x:850,y:330,z:1.16},{t:14,x:850,y:330,z:1.16}];
 if(id==="demand")return [{t:0,...full},{t:1,x:500,y:300,z:1.1},{t:2.8,x:500,y:300,z:1.1},{t:4.1,x:850,y:300,z:1.16},{t:13,x:850,y:300,z:1.16}];
 if(id==="discover")return [{t:0,...full},{t:1,x:500,y:320,z:1.1},{t:3,x:500,y:320,z:1.1},{t:4.3,x:850,y:336,z:1.14},{t:9,x:850,y:336,z:1.14}];
 const focus=id==="access"?{x:900,y:200,z:1.12}:id==="shortlist"?{x:500,y:430,z:1.1}:{x:500,y:336,z:1.12};
 return [{t:0,...full},{t:1,...focus},{t:3.6,...focus},{t:4.9,...full},{t:14,...full}];
};

export const GuidedCapture=({id}:{id:string})=>{
 const frame=useCurrentFrame();const {fps}=useVideoConfig();const t=frame/fps;
 const shot=shots[id];
 const current=[...shot.states].reverse().find(s=>s.seconds<=t)??shot.states[0];
 const camera=cameraFor(id).map(k=>{
   const scale=(W/1280)*k.z;
   return {t:k.t,scale,left:clamp(W/2-k.x*scale,W-1280*scale,0),top:clamp(H/2-k.y*scale,H-672*scale,0)};
 });
 const keys=camera.map(k=>k.t);
 const scale=interpolateKeys(t,keys,camera.map(k=>k.scale));
 const left=interpolateKeys(t,keys,camera.map(k=>k.left));
 const top=interpolateKeys(t,keys,camera.map(k=>k.top));
 const e=shot.events.find(e=>t>=e.seconds-.95&&t<=e.seconds+.8);
 const progress=e?clamp((t-(e.seconds-.9))/.55,0,1):0;
 const p=ease(progress);
 const cx=e?e.x+(1-p)*Math.min(110,1250-e.x):0;
 const cy=e?e.y+(1-p)*Math.min(85,640-e.y):0;
 const fade=e?interpolate(t,[e.seconds-.95,e.seconds-.8,e.seconds+.45,e.seconds+.8],[0,1,1,0],{extrapolateLeft:"clamp",extrapolateRight:"clamp"}):0;
 const click=e?clamp((t-e.seconds)/.42,0,1):0;
 const pressed=e&&t>=e.seconds&&t<e.seconds+.2;
 return <div style={{position:"absolute",left,top,width:1280,height:672,scale,transformOrigin:"top left"}}>
  {shot.states.map(s=><CanvasImage key={s.image} name="Authentic Satellite capture" src={staticFile(images[s.image].src)} premountFor={fps}
   style={{position:"absolute",inset:0,width:1280,height:672,opacity:current.image===s.image?1:0}}/>)}
  {e?<>
   <svg width={1280} height={672} style={{position:"absolute",inset:0,pointerEvents:"none",opacity:fade}}>
    <defs><mask id={`focus-${id}`}><rect width={1280} height={672} fill="white"/><rect x={e.rect.x-8} y={e.rect.y-8} width={e.rect.w+16} height={e.rect.h+16} rx={12} fill="black"/></mask></defs>
    <rect width={1280} height={672} fill="#021A2B" opacity={.22} mask={`url(#focus-${id})`}/>
    <rect x={e.rect.x-5} y={e.rect.y-5} width={e.rect.w+10} height={e.rect.h+10} rx={10} fill="none" stroke="#00D8AC" strokeWidth={1.6}/>
    {click>0&&click<1?<circle cx={e.x} cy={e.y} r={10+click*24} fill="none" stroke="#00D8AC" strokeWidth={2} opacity={1-click}/>:null}
   </svg>
   <svg width={25} height={31} viewBox="0 0 50 62" style={{position:"absolute",left:cx-2,top:cy-2,opacity:fade,
     scale:pressed?.86:1,transformOrigin:"top left",filter:"drop-shadow(0 2px 3px #021A2B80)"}}>
    <path d="M4 3L4 45L15 35L25 57L33 53L23 32L39 32Z" fill="white" stroke="#032536" strokeWidth={2.8}/>
   </svg>
  </>:null}
 </div>;
};
