import {AbsoluteFill,CanvasImage,Easing,Interactive,interpolate,staticFile,useCurrentFrame,useVideoConfig} from "remotion";
import {GuidedCapture} from "./GuidedCapture";
import {PurposeShowcase} from "./PurposeShowcase";
import excerpt from "../export-excerpt.json";
import "../design";

const ink="#031C2E",mint="#19E0B3",cream="#F7F6F0";
const ease=Easing.bezier(.22,1,.36,1);
const specs:Record<string,{n:string;title:string[];copy:string;tag:string}>={
 search:{n:"01",title:["Your place.","Your purpose."],copy:"From a location\nto a focused question.",tag:"CHOOSE YOUR STARTING POINT"},
 evidence:{n:"02",title:["A clearer","picture."],copy:"Agriculture.\nPeople. Places.",tag:"OPEN DATA, CONNECTED"},
 access:{n:"03",title:["Real roads.","Real reach."],copy:"Dry season ↔ Rainy season\nTravel-time catchments",tag:"ACCESS IN CONTEXT"},
 energy:{n:"04",title:["Energy.","In context."],copy:"Mapped infrastructure.\nSolar possibilities.",tag:"SEE THE SUPPLY PICTURE"},
 demand:{n:"05",title:["The need.","The range."],copy:"An estimate you can trace.",tag:"UNDERSTAND THE DEMAND"},
 confidence:{n:"06",title:["Confidence.","Made visible."],copy:"Assumptions challenged.\nEvidence made clear.",tag:"SEE WHAT HOLDS UP"},
 discover:{n:"07",title:["Look","beyond."],copy:"Predicted leads.\nEvidence to inspect.",tag:"FIND PLACES TO INVESTIGATE"},
 shortlist:{n:"08",title:["A shortlist.","A next step."],copy:"Ranked locations.\nEvidence and questions.",tag:"TAKE IT INTO THE FIELD"},
};

const Background=()=>{
 const f=useCurrentFrame();const {fps}=useVideoConfig();
 return <>
  <AbsoluteFill style={{background:ink}}/>
  <div style={{position:"absolute",left:1500,top:100,width:2500,height:2200,borderRadius:"50%",
    background:"radial-gradient(ellipse, #065B5D88 0%, #031C2E00 68%)",translate:`${interpolate(f,[0,15*fps],[0,-80],{extrapolateRight:"clamp"})}px 0px`}}/>
  <svg width={3840} height={2160} style={{position:"absolute",inset:0,opacity:.22}}>
    <defs><pattern id="ad-grid" width="96" height="96" patternUnits="userSpaceOnUse"><circle cx="1" cy="1" r="1.4" fill="#6DADAF"/></pattern></defs>
    <rect width="3840" height="2160" fill="url(#ad-grid)"/>
    <path d="M-80 1840C700 1650 670 2100 1520 1790S2400 2020 3970 1600" fill="none" stroke="#19E0B3" strokeWidth="2" opacity=".3"/>
  </svg>
 </>;
};

const Mark=({light=false}:{light?:boolean})=>{
 const {fps}=useVideoConfig();
 return <CanvasImage name="EnaGIS wordmark" src={staticFile("brand/enagis-wordmark.png")} premountFor={fps}
  style={{position:"absolute",left:144,top:90,width:370,height:"auto",filter:light?"brightness(0) invert(1)":undefined}}/>;
};

const LogoScene=({close}:{close:boolean})=>{
 const f=useCurrentFrame();const {fps}=useVideoConfig();
 return <AbsoluteFill style={{background:cream,color:ink,fontFamily:"Inter"}}>
  <svg width={3840} height={2160} style={{position:"absolute",inset:0,opacity:.17}}>
   <path d="M2700-200C2350 400 3300 600 2930 1200S3000 2020 4000 2100" fill="none" stroke="#00A982" strokeWidth={2}/>
   <circle cx="2930" cy="1200" r={90+interpolate(f,[0,7*fps],[0,90],{extrapolateRight:"clamp"})} fill="none" stroke="#00A982" strokeWidth={2}/>
  </svg>
  <CanvasImage name="EnaGIS identity" src={staticFile("brand/enagis-wordmark.png")} premountFor={fps}
   style={{position:"absolute",left:190,top:260,width:1730,height:"auto",
    translate:interpolate(f,[0,.8*fps],["0px 40px","0px 0px"],{extrapolateRight:"clamp",easing:ease}),
    opacity:interpolate(f,[0,.65*fps],[0,1],{extrapolateRight:"clamp"})}}/>
  <Interactive.Div name="Official EnaGIS motto" style={{position:"absolute",left:178,top:930,fontSize:242,fontWeight:600,
   letterSpacing:-10,lineHeight:1.08,opacity:interpolate(f,[.35*fps,1*fps],[0,1],{extrapolateLeft:"clamp",extrapolateRight:"clamp"}),
   translate:interpolate(f,[.35*fps,1.2*fps],["0px 60px","0px 0px"],{extrapolateLeft:"clamp",extrapolateRight:"clamp",easing:ease})}}>
    Mapping Energy.<br/><span style={{color:"#008C70"}}>Powering Agriculture.</span>
  </Interactive.Div>
  <div style={{position:"absolute",left:190,top:1540,height:6,width:interpolate(f,[.6*fps,1.8*fps],[0,750],{extrapolateLeft:"clamp",extrapolateRight:"clamp",easing:ease}),background:mint}}/>
  <div style={{position:"absolute",left:190,top:1675,fontSize:64,color:"#087B65",fontWeight:500,
    opacity:interpolate(f,[1.2*fps,1.8*fps],[0,1],{extrapolateLeft:"clamp",extrapolateRight:"clamp"})}}>
    {close?"enagis.netlify.app  ↗":"AGRICULTURE  ×  ENERGY  ×  GEOGRAPHY"}
  </div>
  {close?<div style={{position:"absolute",right:190,bottom:220,color:"#527273",fontSize:36,letterSpacing:4}}>TEAM DYNAMIS</div>:null}
  <div style={{position:"absolute",left:0,bottom:0,width:3840,height:24,background:"linear-gradient(90deg,#00816B,#19E0B3)"}}/>
 </AbsoluteFill>;
};

const Hook=()=>{
 const f=useCurrentFrame();const {fps}=useVideoConfig();
 return <AbsoluteFill style={{background:ink,fontFamily:"Inter",color:cream}}>
  <CanvasImage name="Agriculture and energy concept" src={staticFile("imagery/agriculture-energy-panorama.png")} premountFor={fps}
   style={{position:"absolute",inset:0,width:3840,height:2160,objectFit:"cover",scale:interpolate(f,[0,6*fps],[1.065,1],{extrapolateRight:"clamp",output:"perceptual-scale"})}}/>
  <AbsoluteFill style={{background:"linear-gradient(90deg,#031C2EF7 5%,#031C2EB5 48%,#031C2E18 100%),linear-gradient(0deg,#031C2ED9,transparent 60%)"}}/>
  <Mark light/>
  <div style={{position:"absolute",left:150,top:430,fontSize:34,letterSpacing:6,color:"#87E3CD"}}>AGRICULTURE HAS POTENTIAL.</div>
  <Interactive.Div name="Commercial opening" style={{position:"absolute",left:138,top:610,width:2700,fontSize:282,fontWeight:600,
   letterSpacing:-13,lineHeight:1.02,opacity:interpolate(f,[0,.5*fps],[0,1],{extrapolateRight:"clamp"}),
   translate:interpolate(f,[0,.9*fps],["0px 100px","0px 0px"],{extrapolateRight:"clamp",easing:ease})}}>
   Every harvest.<br/><span style={{color:mint}}>More potential.</span>
  </Interactive.Div>
  <div style={{position:"absolute",left:155,top:1370,fontSize:76,color:"#DAEBE4",
   opacity:interpolate(f,[2.2*fps,2.8*fps],[0,1],{extrapolateLeft:"clamp",extrapolateRight:"clamp"})}}>Energy helps unlock what comes next.</div>
  <svg width={1200} height={600} style={{position:"absolute",right:10,bottom:150}}>
   <path d="M80 380C360 380 300 110 620 200S820 500 1150 170" fill="none" stroke={mint} strokeWidth={4} strokeDasharray={1600}
    strokeDashoffset={interpolate(f,[1*fps,4.8*fps],[1600,0],{extrapolateLeft:"clamp",extrapolateRight:"clamp",easing:ease})}/>
   <circle cx={620} cy={200} r={20} fill={mint}/><circle cx={620} cy={200} r={64} fill="none" stroke={mint} strokeWidth={2}/>
  </svg>
  <div style={{position:"absolute",left:150,bottom:170,fontSize:24,color:"#99B6B5"}}>Concept illustration</div>
 </AbsoluteFill>;
};

const FeatureFacts=({id}:{id:string})=>{
 const f=useCurrentFrame();const {fps}=useVideoConfig();const t=f/fps;
 if(id==="search")return <PurposeShowcase/>;
 const show=t>2.2;
 const style={opacity:interpolate(f,[2.2*fps,2.8*fps],[0,1],{extrapolateLeft:"clamp",extrapolateRight:"clamp"}),
  translate:interpolate(f,[2.2*fps,3*fps],["0px 34px","0px 0px"],{extrapolateLeft:"clamp",extrapolateRight:"clamp",easing:ease})};
 if(!show)return null;
 if(id==="demand")return <div style={{position:"absolute",left:144,top:1190,width:800,...style}}>
   <div style={{fontSize:250,fontWeight:550,letterSpacing:-14,lineHeight:1,color:mint,fontVariantNumeric:"tabular-nums"}}>{Math.round(interpolate(f,[2.2*fps,3.15*fps],[0,142],{extrapolateLeft:"clamp",extrapolateRight:"clamp",easing:ease}))}</div>
   <div style={{fontSize:40,color:"#C3DBD6",marginTop:20}}>kWh/day · ESTIMATED</div>
   <div style={{marginTop:65,height:6,width:710,background:"#1D444B",position:"relative"}}>
    <div style={{height:6,width:interpolate(f,[2.7*fps,3.5*fps],[0,710],{extrapolateLeft:"clamp",extrapolateRight:"clamp",easing:ease}),background:mint}}/>
    <div style={{position:"absolute",left:180,top:-14,width:32,height:32,borderRadius:16,background:cream}}/>
   </div><div style={{display:"flex",justifyContent:"space-between",width:710,fontSize:43,marginTop:25,color:"#BFD6D4"}}><span>56</span><span>388 kWh/day</span></div>
   <div style={{fontSize:27,color:"#709A9C",marginTop:35}}>Saved-case estimate · range from assumptions</div>
  </div>;
 if(id==="confidence")return <div style={{position:"absolute",left:144,top:1180,width:800,...style}}>
   <div style={{fontSize:246,lineHeight:1,fontWeight:550,letterSpacing:-14,color:mint,fontVariantNumeric:"tabular-nums"}}>{Math.round(interpolate(f,[2.2*fps,3.15*fps],[0,300],{extrapolateLeft:"clamp",extrapolateRight:"clamp",easing:ease}))}</div>
   <div style={{fontSize:42,color:"#BDD8D3",marginTop:25}}>assumption scenarios</div>
   <div style={{display:"flex",gap:14,marginTop:65}}>{Array.from({length:10},(_,i)=><div key={i} style={{width:56,height:90,borderRadius:9,background:i<8?mint:"#E7BB6B",
    scale:interpolate(f,[(2.5+i*.045)*fps,(2.9+i*.045)*fps],[.2,1],{extrapolateLeft:"clamp",extrapolateRight:"clamp",easing:ease}),transformOrigin:"bottom"}}/>)}</div>
   <div style={{fontSize:32,color:"#BBD3D0",marginTop:28}}>8 robust · 2 contested in this top ten</div>
  </div>;
 if(id==="energy")return <div style={{position:"absolute",left:144,top:1220,width:800,...style}}>
   <div style={{fontSize:42,color:"#BDD8D3"}}>Mapped lines ≠ a confirmed connection</div>
   <div style={{width:710,height:2,background:"#2A5257",margin:"48px 0"}}/>
   {t>=8.2?<><div style={{fontSize:170,color:mint,fontWeight:550,letterSpacing:-8}}>40 <span style={{fontSize:65,letterSpacing:-2}}>kWp</span></div>
    <div style={{fontSize:36,color:"#BED8D2",marginTop:15}}>Illustrative PV · Kora Market</div>
    <div style={{fontSize:29,color:"#7BA4A4",marginTop:22}}>Peak day · batteries excluded</div></>:
    <div style={{fontSize:66,lineHeight:1.25,color:mint}}>Trace the grid.<br/>Explore the sun.</div>}
  </div>;
 const chips=id==="discover"?["PREDICTED","VERIFY ON SITE"]:id==="evidence"?["BUILDINGS","ROADS","POPULATION"]:id==="access"?["DRY SEASON","RAINY SEASON"]:["RANKED","EXPORTABLE"];
 return <div style={{position:"absolute",left:144,top:1250,width:820,...style}}>
   {chips.map((c,i)=><div key={c} style={{height:110,display:"flex",alignItems:"center",gap:30,fontSize:35,letterSpacing:3,color:i===0?mint:"#B5D0CD",borderTop:"1px solid #31585B",
     opacity:interpolate(f,[(2.3+i*.22)*fps,(2.8+i*.22)*fps],[0,1],{extrapolateLeft:"clamp",extrapolateRight:"clamp"}),
     translate:interpolate(f,[(2.3+i*.22)*fps,(3+i*.22)*fps],["-35px 0px","0px 0px"],{extrapolateLeft:"clamp",extrapolateRight:"clamp",easing:ease})}}><span style={{fontSize:22,color:"#648D8E"}}>0{i+1}</span>{c}</div>)}
  </div>;
};

const ExportCard=()=>{
 const f=useCurrentFrame();const {fps}=useVideoConfig();const t=f/fps;
 if(t<2.55)return null;
 return <div style={{position:"absolute",left:1310,top:615,width:2130,padding:95,borderRadius:36,background:cream,color:ink,
   boxShadow:"0 40px 100px #001522A0",border:"2px solid #19E0B3",opacity:interpolate(f,[2.55*fps,3*fps],[0,1],{extrapolateRight:"clamp"}),
   translate:interpolate(f,[2.55*fps,3.2*fps],["0px 60px","0px 0px"],{extrapolateRight:"clamp",easing:ease})}}>
   <div style={{fontSize:29,letterSpacing:4,color:"#087B65"}}>{t<5.8?"EXPORTED SHORTLIST · DRY-SEASON EXCERPT":"THE NEXT CONVERSATION"}</div>
   {t<5.8?<><div style={{fontSize:95,fontWeight:550,letterSpacing:-4,marginTop:35,marginBottom:40}}>Ready for your next step.</div>
    {excerpt.rows.map(r=><div key={r.rank} style={{display:"flex",alignItems:"baseline",gap:35,padding:"30px 0",borderTop:"2px solid #0325361A",fontSize:53}}>
     <span style={{width:80,color:"#087B65"}}>{r.rank}</span><span style={{flex:1}}>{r.name}</span><span>{r.central} <span style={{fontSize:32}}>kWh/day</span></span>
    </div>)}<div style={{fontSize:30,color:"#617C7C",marginTop:35}}>ESTIMATED · supporting ranges and questions included</div></>:
    <><div style={{fontFamily:"Fraunces",fontSize:105,lineHeight:1.18,letterSpacing:-3,marginTop:55}}>“{excerpt.rows[0].question}”</div>
     <div style={{fontSize:34,color:"#587576",marginTop:45}}>Investigation question from the selected candidate's record</div></>}
  </div>;
};

export const AdScene=({id}:{id:string})=>{
 const f=useCurrentFrame();const {fps}=useVideoConfig();
 if(id==="hook")return <Hook/>;
 if(id==="brand"||id==="close")return <LogoScene close={id==="close"}/>;
 const spec=specs[id];
 return <AbsoluteFill style={{fontFamily:"Inter",color:cream}}>
  <Background/><Mark light/>
  <div style={{position:"absolute",right:145,top:112,fontSize:29,color:"#8FB8B6",letterSpacing:4}}>AGRICULTURAL ENERGY SCREENING</div>
  <div style={{position:"absolute",left:145,top:330,fontSize:28,letterSpacing:4,color:mint}}>{spec.n} / {spec.tag}</div>
  <Interactive.Div name="Commercial feature headline" style={{position:"absolute",left:134,top:465,width:900,fontSize:142,fontWeight:600,letterSpacing:-7,lineHeight:1.08,
    opacity:interpolate(f,[0,.55*fps],[0,1],{extrapolateRight:"clamp"}),translate:interpolate(f,[0,.9*fps],["0px 55px","0px 0px"],{extrapolateRight:"clamp",easing:ease})}}>
    {spec.title.map((line,i)=><div key={line} style={{color:i===1?mint:cream,
      opacity:id==="search"?interpolate(f,[(i===0?.35:1.78)*fps,(i===0?.8:2.23)*fps],[0,1],{extrapolateLeft:"clamp",extrapolateRight:"clamp"}):1,
      translate:id==="search"?interpolate(f,[(i===0?.35:1.78)*fps,(i===0?1:2.43)*fps],["0px 55px","0px 0px"],{extrapolateLeft:"clamp",extrapolateRight:"clamp",easing:ease}):undefined}}>{line}</div>)}
  </Interactive.Div>
  <div style={{position:"absolute",left:145,top:880,width:800,fontSize:49,lineHeight:1.4,color:"#BAD4CF",whiteSpace:"pre-line",
    opacity:interpolate(f,[.4*fps,1*fps],[0,1],{extrapolateLeft:"clamp",extrapolateRight:"clamp"})}}>{spec.copy}</div>
  <FeatureFacts id={id}/>
  <div style={{position:"absolute",left:1072,top:320,width:2624,height:1472,borderRadius:32,overflow:"hidden",boxShadow:"0 50px 150px #00121DB0",border:"2px solid #28565D"}}>
   <div style={{height:80,background:"#0A2C3D",display:"flex",alignItems:"center",padding:"0 40px",gap:16}}>
    <div style={{width:14,height:14,borderRadius:7,background:mint}}/><div style={{fontSize:27,color:"#B6D2D0",letterSpacing:2}}>ENAGIS WORKSPACE</div>
    <div style={{marginLeft:"auto",fontSize:23,color:"#88AEAD"}}>Satellite view</div>
   </div>
   <div style={{position:"absolute",left:0,top:80,width:2624,height:1392,overflow:"hidden",background:cream}}><GuidedCapture id={id}/></div>
  </div>
  <div style={{position:"absolute",left:1090,top:1828,fontSize:24,color:"#749B9E"}}>
   Imagery © Esri, Maxar, Earthstar Geographics · © OpenStreetMap contributors · Overture Maps · WorldPop · Open-Meteo
  </div>
  {id!=="search"?<div style={{position:"absolute",left:1090,top:1880,fontSize:28,color:"#A2C3BE"}}>Saved analysis · 10 October 2026</div>:null}
  {id==="search"&&f>=9.15*fps?<div style={{position:"absolute",left:1072,top:320,width:2624,height:1472,borderRadius:32,background:"#032536F2",
    display:"flex",flexDirection:"column",alignItems:"center",justifyContent:"center",
    opacity:interpolate(f,[9.15*fps,9.55*fps],[0,1],{extrapolateRight:"clamp"})}}>
    <div style={{fontSize:32,letterSpacing:5,color:mint}}>FOLLOW ONE ANALYSIS</div>
    <div style={{fontSize:110,fontWeight:550,letterSpacing:-4,marginTop:40,width:2320,textAlign:"center"}}>A place. A purpose. A clearer picture.</div>
    <div style={{fontSize:42,color:"#A2C3BE",marginTop:50}}>Saved example · 10 October 2026</div>
  </div>:null}
  {id==="shortlist"?<ExportCard/>:null}
  <div style={{position:"absolute",left:145,top:1840,width:740,height:3,background:"#21434D"}}>
   <div style={{height:3,background:mint,width:interpolate(f,[0,10*fps],[0,740],{extrapolateRight:"clamp"})}}/>
  </div>
 </AbsoluteFill>;
};
