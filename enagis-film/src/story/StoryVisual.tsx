import {AbsoluteFill,CanvasImage,Easing,Interactive,interpolate,staticFile,useCurrentFrame,useVideoConfig} from "remotion";
import {StoryCapture} from "./StoryCapture";
import timeline from "./timeline.json";
import "../design";

const ink="#041E2D",mint="#17DDB0",cream="#F7F6EF",ease=Easing.bezier(.2,1,.3,1);
const specs:Record<string,{step:string;title:string[];copy:string;question:string}>={
 place:{step:"01",title:["One place.","One purpose."],copy:"Potato cold storage",question:"CHOOSE YOUR AREA"},
 ranking:{step:"02",title:["Start with","Kora Market."],copy:"A shortlist gives you somewhere to begin.",question:"WHERE FIRST"},
 harvest:{step:"03",title:["Follow","the harvest."],copy:"Where might the crops come from?",question:"HARVEST"},
 access:{step:"04",title:["Can people","reach it?"],copy:"Follow roads. Compare seasons.",question:"ACCESS"},
 energy:{step:"05",title:["Is power","within reach?"],copy:"Mapped supply. Possible options.",question:"ENERGY"},
 demand:{step:"06",title:["What could","it need?"],copy:"Electricity for a busy harvest day.",question:"THE SITE CARD"},
 confidence:{step:"07",title:["Does the","choice hold up?"],copy:"Repeat the comparison under different assumptions.",question:"HOW SURE"},
 discover:{step:"08",title:["What might","be missing?"],copy:"Places worth investigating.",question:"LIKELY SITES"},
 evidence:{step:"09",title:["Know what","you know."],copy:"Inspect the sources. See the gaps.",question:"MAP DATA + SOURCES"},
 export:{step:"10",title:["Take it","into the field."],copy:"Keep the evidence with the decision.",question:"EXPORT + VERIFICATION"},
};

const Mark=({dark=false}:{dark?:boolean})=>{
 const {fps}=useVideoConfig();
 return <CanvasImage name="EnaGIS identity" src={staticFile("brand/enagis-wordmark.png")} premountFor={fps}
  style={{position:"absolute",left:74,top:56,width:214,height:"auto",filter:dark?undefined:"brightness(0) invert(1)"}}/>;
};

const Opening=()=>{
 const f=useCurrentFrame();const {fps}=useVideoConfig();
 return <AbsoluteFill style={{background:ink,fontFamily:"Inter",color:cream}}>
  <CanvasImage name="Real satellite case · opening" src={staticFile("story/footage/harvest.png")} premountFor={fps}
   style={{position:"absolute",inset:0,width:1920,height:1080,objectFit:"cover",scale:interpolate(f,[0,7*fps],[1.04,1],{extrapolateRight:"clamp",output:"perceptual-scale"})}}/>
  <AbsoluteFill style={{background:"linear-gradient(90deg,#041E2DFF 8%,#041E2DF2 35%,#041E2D40 100%),linear-gradient(0deg,#041E2DCC,transparent 70%)"}}/>
  <Mark/>
  <div style={{position:"absolute",left:76,top:169,fontSize:21,color:mint,letterSpacing:4}}>ONE PLANNING DECISION</div>
  <Interactive.Div name="The user's question" style={{position:"absolute",left:68,top:264,fontSize:132,fontWeight:600,letterSpacing:-7,lineHeight:1.03,
   opacity:interpolate(f,[0,.55*fps],[0,1],{extrapolateRight:"clamp"}),
   translate:interpolate(f,[0,.8*fps],["0px 45px","0px 0px"],{extrapolateRight:"clamp",easing:ease})}}>
   Where would<br/><span style={{color:mint}}>you start?</span>
  </Interactive.Div>
  <div style={{position:"absolute",left:78,top:590,fontSize:43,color:"#DAECE5",
   opacity:interpolate(f,[.8*fps,1.5*fps],[0,1],{extrapolateLeft:"clamp",extrapolateRight:"clamp"})}}>A cold store for potato growers.</div>
  <div style={{position:"absolute",left:78,top:765,display:"flex",gap:55,alignItems:"center"}}>
   {["Choose an area","Compare sites","Plan a visit"].map((s,i)=><div key={s} style={{display:"flex",gap:18,alignItems:"center",
    opacity:interpolate(f,[(1.4+i*.65)*fps,(2.1+i*.65)*fps],[0,1],{extrapolateLeft:"clamp",extrapolateRight:"clamp"}),
    translate:interpolate(f,[(1.4+i*.65)*fps,(2.1+i*.65)*fps],["0px 20px","0px 0px"],{extrapolateLeft:"clamp",extrapolateRight:"clamp",easing:ease})}}>
     <span style={{width:38,height:38,border:"1px solid #17DDB0",borderRadius:19,display:"grid",placeItems:"center",fontSize:17,color:mint}}>{i+1}</span><span style={{fontSize:26}}>{s}</span>{i<2?<span style={{color:mint,marginLeft:15}}>→</span>:null}
    </div>)}
  </div>
  <div style={{position:"absolute",left:80,top:915,fontSize:17,color:"#7BA4A4"}}>Illustrative planning task · actual saved analysis · field checks remain necessary</div>
 </AbsoluteFill>;
};

const Outcome=()=>{
 const f=useCurrentFrame();const {fps}=useVideoConfig();
 return <AbsoluteFill style={{background:cream,color:ink,fontFamily:"Inter"}}>
  <Mark dark/>
  <div style={{position:"absolute",left:80,top:178,fontSize:20,letterSpacing:4,color:"#087A64"}}>THE RESULT OF THE WORKFLOW</div>
  <Interactive.Div name="A practical outcome" style={{position:"absolute",left:70,top:278,fontSize:113,lineHeight:1.08,fontWeight:600,letterSpacing:-5,
   opacity:interpolate(f,[0,.55*fps],[0,1],{extrapolateRight:"clamp"}),translate:interpolate(f,[0,.8*fps],["0px 35px","0px 0px"],{extrapolateRight:"clamp",easing:ease})}}>
   A clearer shortlist.<br/><span style={{color:"#008B6D"}}>A practical next step.</span>
  </Interactive.Div>
  <div style={{position:"absolute",left:82,top:648,width:1745,height:2,background:"#ADC9BE"}}/>
  {["Where to look","Why it ranks","What to verify"].map((s,i)=><div key={s} style={{position:"absolute",left:82+i*585,top:710,
   opacity:interpolate(f,[(.6+i*.45)*fps,(1.1+i*.45)*fps],[0,1],{extrapolateLeft:"clamp",extrapolateRight:"clamp"}),
   translate:interpolate(f,[(.6+i*.45)*fps,(1.3+i*.45)*fps],["0px 28px","0px 0px"],{extrapolateLeft:"clamp",extrapolateRight:"clamp",easing:ease})}}>
   <div style={{fontSize:22,color:"#008B6D",marginBottom:20}}>0{i+1}</div><div style={{fontSize:43,fontWeight:500,letterSpacing:-1}}>{s}</div>
  </div>)}
  <div style={{position:"absolute",left:82,bottom:127,fontSize:21,color:"#587871"}}>Screening supports an investigation. It does not replace a feasibility study.</div>
 </AbsoluteFill>;
};

const Facts=({id}:{id:string})=>{
 const f=useCurrentFrame();const {fps}=useVideoConfig();const t=f/fps;
 const style={position:"absolute" as const,left:76,top:588,width:440,
  opacity:interpolate(f,[1.65*fps,2.25*fps],[0,1],{extrapolateLeft:"clamp" as const,extrapolateRight:"clamp" as const}),
  translate:interpolate(f,[1.65*fps,2.5*fps],["0px 24px","0px 0px"],{extrapolateLeft:"clamp" as const,extrapolateRight:"clamp" as const,easing:ease})};
 if(id==="ranking")return <div style={style}>
   <div style={{fontSize:108,color:mint,fontWeight:550,letterSpacing:-6}}>310 <span style={{fontSize:24,letterSpacing:0,color:"#B1CFCA"}}>candidates</span></div>
   <div style={{height:1,background:"#31585C",width:390,margin:"25px 0"}}/>
   <div style={{fontSize:83,fontWeight:550,letterSpacing:-4}}>10 <span style={{fontSize:26,letterSpacing:0,color:"#B1CFCA"}}>to check first</span></div>
   <div style={{fontSize:17,color:"#6D999A",marginTop:20}}>Saved case · ranked for investigation</div>
  </div>;
 if(id==="demand")return <div style={style}>
   <div style={{fontSize:112,color:mint,fontWeight:550,letterSpacing:-6,fontVariantNumeric:"tabular-nums"}}>{Math.round(interpolate(f,[1.65*fps,2.45*fps],[0,142],{extrapolateLeft:"clamp",extrapolateRight:"clamp",easing:ease}))}</div>
   <div style={{fontSize:27,color:"#B1CFCA"}}>kWh per peak day · estimated</div>
   <div style={{position:"relative",width:380,height:4,marginTop:47,background:"#31585C"}}>
    <div style={{width:interpolate(f,[2.3*fps,3.1*fps],[0,380],{extrapolateLeft:"clamp",extrapolateRight:"clamp",easing:ease}),height:4,background:mint}}/>
    <div style={{position:"absolute",left:98,top:-7,width:18,height:18,borderRadius:9,background:cream}}/>
   </div><div style={{display:"flex",justifyContent:"space-between",width:380,fontSize:22,marginTop:17,color:"#B1CFCA"}}><span>56</span><span>388 kWh/day</span></div>
   <div style={{fontSize:18,color:"#739C9B",marginTop:24}}>A range, with assumptions you can inspect.</div>
  </div>;
 if(id==="confidence")return <div style={style}>
   <div style={{fontSize:110,color:mint,fontWeight:550,letterSpacing:-6,fontVariantNumeric:"tabular-nums"}}>{Math.round(interpolate(f,[1.65*fps,2.45*fps],[0,300],{extrapolateLeft:"clamp",extrapolateRight:"clamp",easing:ease}))}</div>
   <div style={{fontSize:27,color:"#B1CFCA"}}>sets of assumptions</div>
   <div style={{display:"flex",gap:9,marginTop:35}}>{Array.from({length:10},(_,i)=><div key={i} style={{width:28,height:66,borderRadius:4,background:i<8?mint:"#E6B76E",transformOrigin:"bottom",
    scale:interpolate(f,[(2.2+i*.06)*fps,(2.7+i*.06)*fps],[.1,1],{extrapolateLeft:"clamp",extrapolateRight:"clamp",easing:ease})}}/>)}</div>
   <div style={{fontSize:20,color:"#B1CFCA",marginTop:22}}>8 robust · 2 contested in this top ten</div>
  </div>;
 if(id==="access")return <div style={style}>
   <svg width={395} height={120} viewBox="0 0 395 120" fill="none">
    <path d="M15 95C70 95 60 20 143 32S205 105 285 52L375 20" stroke="#3F7775" strokeWidth={3}/>
    <path d="M15 95C70 95 60 20 143 32S205 105 285 52L375 20" stroke={mint} strokeWidth={3} strokeDasharray={500} strokeDashoffset={interpolate(f,[1.8*fps,3.5*fps],[500,0],{extrapolateLeft:"clamp",extrapolateRight:"clamp",easing:ease})}/>
    <circle cx={15} cy={95} r={7} fill={cream}/><circle cx={375} cy={20} r={10} fill={mint}/>
   </svg>
   <div style={{fontSize:34,color:t>=4.3?"#789E9D":cream,marginTop:22}}>Dry season</div>
   <div style={{fontSize:34,color:t>=4.3?mint:"#789E9D",marginTop:15}}>Rainy season</div>
   <div style={{fontSize:20,color:"#9EBFBA",marginTop:30}}>Road travel shapes the catchment.</div>
  </div>;
 const lines=id==="place"?["Search your area","Choose a value chain","Follow this saved example"]:
  id==="harvest"?["Production statistics","Mapped homes","Estimated crop supply"]:
  id==="energy"?["Mapped power lines","A possible solar option","Connection still needs checking"]:
  id==="discover"?["Predicted lead","Check whether it exists","Verify what it does"]:
  id==="evidence"?["Sources","Assumptions","Visible information gaps"]:
  ["Crop volumes","Power connection","Local conditions"];
 return <div style={style}>
   {id==="export"?<div style={{fontSize:19,letterSpacing:3,color:mint,marginBottom:25}}>{t<3.2?"SHORTLIST EXPORTED":t<5.5?"ANALYSIS SAVED":"CHECK BEFORE INVESTING"}</div>:null}
   {lines.map((line,i)=><div key={line} style={{padding:"22px 0",borderTop:"1px solid #31585C",fontSize:25,lineHeight:1.25,color:i===0?mint:"#B8D1CA",
     opacity:interpolate(f,[(1.8+i*.2)*fps,(2.3+i*.2)*fps],[0,1],{extrapolateLeft:"clamp",extrapolateRight:"clamp"}),
     translate:interpolate(f,[(1.8+i*.2)*fps,(2.5+i*.2)*fps],["-20px 0px","0px 0px"],{extrapolateLeft:"clamp",extrapolateRight:"clamp",easing:ease})}}>{line}</div>)}
   {id==="energy"?<div style={{fontSize:19,color:"#D8BC86",marginTop:22}}>A mapped line is a lead, not a confirmed supply.</div>:null}
   {id==="discover"?<div style={{fontSize:19,color:"#D8BC86",marginTop:22}}>A prediction is not a confirmed business.</div>:null}
   {id==="export"?<div style={{fontSize:18,color:"#D8BC86",marginTop:22}}>Field checks remain to be done.</div>:null}
  </div>;
};

export const StoryVisual=({id}:{id:string})=>{
 const f=useCurrentFrame();const {fps}=useVideoConfig();
 if(id==="decision")return <Opening/>;
 if(id==="outcome")return <Outcome/>;
 const spec=specs[id];const scene=timeline.scenes.find(s=>s.id===id)!;
 return <AbsoluteFill style={{fontFamily:"Inter",color:cream,background:ink}}>
  <div style={{position:"absolute",inset:0,background:"radial-gradient(ellipse at 72% 50%,#075B5D66,transparent 64%)"}}/>
  <Mark/>
  <div style={{position:"absolute",right:77,top:73,fontSize:18,letterSpacing:3,color:"#8AB0AD"}}>ONE DECISION. CONNECTED EVIDENCE.</div>
  <div style={{position:"absolute",left:77,top:165,fontSize:18,letterSpacing:3,color:mint}}>{spec.step} / {spec.question}</div>
  <Interactive.Div name={`${spec.question} · question`} style={{position:"absolute",left:70,top:248,width:500,fontSize:68,fontWeight:600,letterSpacing:-3.4,lineHeight:1.08,
   opacity:interpolate(f,[0,.5*fps],[0,1],{extrapolateRight:"clamp"}),translate:interpolate(f,[0,.75*fps],["0px 27px","0px 0px"],{extrapolateRight:"clamp",easing:ease})}}>
    {spec.title.map((s,i)=><div key={s} style={{color:i===1?mint:cream}}>{s}</div>)}
  </Interactive.Div>
  <div style={{position:"absolute",left:77,top:455,width:445,fontSize:28,lineHeight:1.4,color:"#BDD3CB",
   opacity:interpolate(f,[.45*fps,1.05*fps],[0,1],{extrapolateLeft:"clamp",extrapolateRight:"clamp"})}}>{spec.copy}</div>
  <Facts id={id}/>
  <div style={{position:"absolute",left:584,top:202,width:1260,height:697.5,borderRadius:18,overflow:"hidden",border:"1px solid #356064",boxShadow:"0 16px 50px #00172180"}}>
   <div style={{height:36,background:"#103440",display:"flex",alignItems:"center",gap:10,padding:"0 20px",fontSize:14,color:"#AFCCC7"}}>
    <span style={{width:7,height:7,borderRadius:4,background:mint}}/>ENAGIS WORKSPACE
    <span style={{marginLeft:"auto",color:"#86ABA8"}}>Satellite · saved case</span>
   </div>
   <div style={{position:"absolute",left:0,top:36,width:1260,height:661.5,overflow:"hidden",background:cream}}><StoryCapture id={id}/></div>
  </div>
  <div style={{position:"absolute",left:591,top:919,fontSize:12,color:"#6F9697"}}>Imagery © Esri, Maxar, Earthstar Geographics · © OpenStreetMap contributors · Overture Maps · WorldPop · Open-Meteo</div>
  <div style={{position:"absolute",left:591,top:946,fontSize:15,color:"#9ABEB6"}}>Actual saved analysis · 10 October 2026 · edited walkthrough</div>
  <div style={{position:"absolute",left:77,top:928,width:420,height:2,background:"#305259"}}><div style={{height:2,background:mint,width:interpolate(f,[0,scene.durationSeconds*fps],[0,420],{extrapolateRight:"clamp"})}}/></div>
 </AbsoluteFill>;
};
