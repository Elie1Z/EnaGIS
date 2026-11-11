import {
  CanvasImage, Easing, Interactive, interpolate, staticFile,
  useCurrentFrame, useVideoConfig,
} from "remotion";
import {captureFor, isReady, type Capture} from "../capture";
import {Frame} from "./Frame";
import excerpt from "../export-excerpt.json";

const smooth = Easing.bezier(0.22, 1, 0.36, 1);

// Coordinates are in source pixels. Add only measured points from actual captures.
const GuidedFootage = ({capture}: {capture: Capture}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const seconds = frame / fps;
  const keys = capture.camera.length >= 2 ? capture.camera : [
    {seconds: 0, x:capture.width / 2, y:capture.height / 2, zoom:1},
    {seconds:capture.durationSeconds, x:capture.width / 2, y:capture.height / 2, zoom:1},
  ];
  const times = keys.map((key) => key.seconds);
  const options = {extrapolateLeft:"clamp",extrapolateRight:"clamp",easing:smooth} as const;
  const zoom = interpolate(seconds, times, keys.map((key) => key.zoom), options);
  const x = interpolate(seconds, times, keys.map((key) => key.x), options);
  const y = interpolate(seconds, times, keys.map((key) => key.y), options);
  const fit = Math.min(3560 / capture.width, 1560 / capture.height);
  const scale = fit * zoom;
  const selected = [...capture.states].reverse().find((state) => seconds >= state.seconds) ?? capture.states[0];
  // Keep the captured viewport inside the frame during close-ups.
  const left = capture.width * scale <= 3560 ? (3560-capture.width*scale)/2
    : Math.max(3560-capture.width*scale,Math.min(0,1780-x*scale));
  const top = capture.height * scale <= 1560 ? (1560-capture.height*scale)/2
    : Math.max(1560-capture.height*scale,Math.min(0,780-y*scale));
  const cursors = capture.cursor;
  const showCursor = !capture.containsCursor && cursors.length >= 2;
  const cursorX = showCursor
    ? interpolate(seconds,cursors.map((point) => point.seconds),cursors.map((point) => point.x),options) : 0;
  const cursorY = showCursor
    ? interpolate(seconds,cursors.map((point) => point.seconds),cursors.map((point) => point.y),options) : 0;
  const click = cursors.find((point) => point.click && seconds >= point.seconds && seconds < point.seconds + 0.18);

  return (
    <div style={{position:"absolute",left,top,
      width:capture.width,height:capture.height,scale,transformOrigin:"top left"}}>
      {capture.states.map((state) => <CanvasImage key={state.src}
        name="Actual captured product state" src={staticFile(state.src)}
        premountFor={fps} style={{position:"absolute",inset:0,width:"100%",height:"100%",
          opacity:state.src === selected.src ? 1 : 0}}/>)}
      {showCursor ? <svg width={28} height={34} viewBox="0 0 70 84"
        style={{position:"absolute",left:cursorX,top:cursorY,filter:"drop-shadow(0 2px 4px #03253666)"}}>
        <path d="M4 3 L4 60 L19 47 L31 76 L41 71 L28 44 L49 43 Z"
          fill="white" stroke="#032536" strokeWidth="3"/>
      </svg> : null}
      {showCursor && click ? <div style={{
        position:"absolute",left:click.x - 22,top:click.y - 22,width:44,height:44,
        border:"2px solid #00BD94",borderRadius:"50%",
        scale:interpolate(seconds,[click.seconds,click.seconds + 0.18],[0.5,1.8]),
        opacity:interpolate(seconds,[click.seconds,click.seconds + 0.18],[0.8,0]),
      }}/> : null}
    </div>
  );
};

export const ProductShot = ({id,number,title,subtitle}: {
  id:string; number:string; title:string; subtitle:string;
}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const capture = captureFor(id);
  const ready = isReady(capture);
  if (!ready) throw new Error(`Missing reviewed Satellite capture for ${id}: ${subtitle}`);
  return (
    <Frame>
      <Interactive.Div name="Section number" style={{
        position:"absolute",left:150,top:100,color:"#087A64",fontSize:36,
        fontWeight:600,letterSpacing:5,
      }}>{number} / ENAGIS</Interactive.Div>
      <Interactive.Div name="Scene headline" style={{
        position:"absolute",left:144,top:174,fontSize:116,fontWeight:550,
        letterSpacing:-5,lineHeight:1.05,
        translate:interpolate(frame,[0,0.7 * fps],["0px 30px","0px 0px"],
          {extrapolateLeft:"clamp",extrapolateRight:"clamp",easing:smooth}),
        opacity:interpolate(frame,[0,0.5 * fps],[0,1],{extrapolateRight:"clamp"}),
      }}>{title}</Interactive.Div>
      <div style={{
        position:"absolute",left:140,top:330,width:3560,height:1560,
        overflow:"hidden",borderRadius:36,backgroundColor:"#F7F6F0",
        border:"2px solid #0325361A",boxShadow:"0 22px 70px #03253616",
      }}>
        <GuidedFootage capture={capture}/>
        {id === "search" && frame >= 11.5 * fps ? <div style={{
          position:"absolute",inset:0,background:"#032536ED",display:"flex",
          flexDirection:"column",justifyContent:"center",alignItems:"center",color:"#F7F6F0",
          opacity:interpolate(frame,[11.5*fps,12*fps],[0,1],{extrapolateRight:"clamp"}),
        }}>
          <div style={{fontSize:38,letterSpacing:5,color:"#75DDC1"}}>FOLLOW ONE ANALYSIS</div>
          <div style={{fontSize:128,letterSpacing:-4,marginTop:32}}>From a place to a shortlist.</div>
          <div style={{fontSize:40,color:"#BCD3CC",marginTop:46}}>Saved example · 10 October 2026</div>
        </div> : null}
        {id === "shortlist" && frame >= 2.65*fps && frame < 5.8*fps ? <div style={{
          position:"absolute",right:150,top:230,width:1660,padding:76,background:"#F7F6F0",
          border:"2px solid #00BD94",borderRadius:32,boxShadow:"0 22px 90px #03253640",
          opacity:interpolate(frame,[2.65*fps,3*fps],[0,1],{extrapolateRight:"clamp"}),
        }}>
          <div style={{fontSize:32,letterSpacing:4,color:"#087A64"}}>ACTUAL CSV EXPORT · DRY SEASON EXCERPT</div>
          <div style={{fontSize:80,fontWeight:550,marginTop:28,marginBottom:38}}>A shortlist you can use.</div>
          {excerpt.rows.map(row=><div key={row.rank} style={{display:"flex",gap:32,
            padding:"24px 0",borderTop:"2px solid #03253618",fontSize:44,alignItems:"baseline"}}>
            <span style={{color:"#087A64",width:60}}>{row.rank}</span>
            <span style={{flex:1}}>{row.name}</span>
            <span>{row.central} <span style={{fontSize:28}}>kWh/day</span></span>
          </div>)}
          <div style={{fontSize:30,color:"#677F83",marginTop:30}}>ESTIMATED · ranges and site questions included in the export</div>
        </div> : null}
      </div>
      {capture.savedAnalysis && ready ? <div style={{
        position:"absolute",right:160,top:120,fontSize:30,color:"#677F83",
      }}>Saved analysis · 10 October 2026</div> : null}
      <div style={{position:"absolute",left:150,top:1914,fontSize:23,color:"#677F83"}}>
        Imagery © Esri, Maxar, Earthstar Geographics · Map data © OpenStreetMap contributors, Overture Maps · WorldPop · Open-Meteo
      </div>
    </Frame>
  );
};
