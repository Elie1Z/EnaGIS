import {Easing,Interactive,interpolate,useCurrentFrame,useVideoConfig} from "remotion";

const mint="#19E0B3";
const out=Easing.bezier(.16,1,.3,1);
const iconPaths={
 cooling:<><path d="M40 7V73M11 23L69 57M11 57L69 23M31 15L40 24L49 15M31 65L40 56L49 65M13 34L26 32L24 19M56 61L54 48L67 46M13 46L26 48L24 61M56 19L54 32L67 34"/></>,
 storage:<><path d="M9 34L40 12L71 34V70H9ZM25 70V40H55V70M25 50H55M25 60H55M17 31L40 15L63 31"/></>,
 milling:<><path d="M13 22H67L58 40H22ZM28 40V69H52V40M21 69H59M32 53H48M40 9V17M23 9L27 17M57 9L53 17"/><circle cx="40" cy="53" r="10"/></>,
 drying:<><circle cx="49" cy="28" r="13"/><path d="M49 4V9M49 47V52M25 28H30M68 28H74M32 11L36 15M63 41L67 45M32 45L36 41M63 15L67 11M11 72C1 58 27 56 17 42M31 72C21 58 47 56 37 42M51 72C45 63 57 59 59 53"/></>,
};

const PurposeCue=({label,kind,index,at}:{label:string;kind:keyof typeof iconPaths;index:string;at:number})=>{
 const f=useCurrentFrame();const {fps}=useVideoConfig();
 return <Interactive.Div name={`${label} · voice-timed reveal`} style={{position:"relative",height:145,width:800,
  opacity:interpolate(f,[at*fps,(at+.15)*fps],[0,1],{extrapolateLeft:"clamp",extrapolateRight:"clamp"}),
  translate:interpolate(f,[at*fps,(at+.52)*fps],["0px 52px","0px 0px"],{extrapolateLeft:"clamp",extrapolateRight:"clamp",easing:out}),
  scale:interpolate(f,[at*fps,(at+.28)*fps,(at+.52)*fps],[.92,1.025,1],{extrapolateLeft:"clamp",extrapolateRight:"clamp"}),transformOrigin:"left center"}}>
   <div style={{position:"absolute",left:0,top:4,width:790,height:1,background:"#497375",
    opacity:interpolate(f,[at*fps,(at+.45)*fps],[0,.45],{extrapolateLeft:"clamp",extrapolateRight:"clamp"}),
    scale:interpolate(f,[at*fps,(at+.5)*fps],[.01,1],{extrapolateLeft:"clamp",extrapolateRight:"clamp",easing:out}),transformOrigin:"left"}}/>
   <div style={{position:"absolute",left:0,top:55,color:"#6C9998",fontSize:23,letterSpacing:2}}>{index}</div>
   <svg width={78} height={78} viewBox="0 0 80 80" style={{position:"absolute",left:69,top:33,color:mint}} fill="none" stroke="currentColor" strokeWidth={2.4} strokeLinecap="round" strokeLinejoin="round">
    <g strokeDasharray={500} strokeDashoffset={interpolate(f,[at*fps,(at+.65)*fps],[500,0],{extrapolateLeft:"clamp",extrapolateRight:"clamp",easing:out})}>{iconPaths[kind]}</g>
   </svg>
   <div style={{position:"absolute",left:180,top:29,height:98,overflow:"hidden",width:570}}>
    <div style={{fontSize:79,fontWeight:550,letterSpacing:-3,lineHeight:1.15,color:"#F7F6F0",
      translate:interpolate(f,[at*fps,(at+.5)*fps],["0px 98px","0px 0px"],{extrapolateLeft:"clamp",extrapolateRight:"clamp",easing:out})}}>{label}</div>
   </div>
 </Interactive.Div>;
};

export const PurposeShowcase=()=>{
 const f=useCurrentFrame();const {fps}=useVideoConfig();
 return <div style={{position:"absolute",left:145,top:1120,width:820,fontFamily:"Inter"}}>
  <div style={{fontSize:25,letterSpacing:5,color:mint,marginBottom:30,
   opacity:interpolate(f,[2.75*fps,3.15*fps],[0,1],{extrapolateLeft:"clamp",extrapolateRight:"clamp"})}}>CHOOSE THE PURPOSE</div>
  <PurposeCue label="Cooling" kind="cooling" index="01" at={3.279}/>
  <PurposeCue label="Storage" kind="storage" index="02" at={4.174}/>
  <PurposeCue label="Milling" kind="milling" index="03" at={5.178}/>
  <PurposeCue label="Drying" kind="drying" index="04" at={6.024}/>
 </div>;
};
