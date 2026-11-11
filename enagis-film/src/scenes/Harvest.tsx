import {CanvasImage, Easing, Interactive, interpolate, staticFile, useCurrentFrame, useVideoConfig} from "remotion";
import type {SceneProps} from "../design";
import {Frame} from "../components/Frame";
import {BasicCaptions} from "../components/basic-captions";

export const Harvest = ({captions}: SceneProps) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  return (
    <Frame dark>
      <CanvasImage name="Agriculture and solar editorial illustration" src={staticFile("imagery/agriculture-energy-panorama.png")}
        premountFor={fps} style={{
          position:"absolute",left:0,top:0,width:3840,height:2160,objectFit:"cover",
          scale:interpolate(frame,[0,6 * fps],[1.08,1],{
            extrapolateRight:"clamp",output:"perceptual-scale"}),
        }}/>
      <div style={{position:"absolute",inset:0,background:
        "linear-gradient(90deg,rgba(3,37,54,.9),rgba(3,37,54,.27) 70%),linear-gradient(0deg,rgba(3,37,54,.65),transparent 45%)"}}/>
      <Interactive.Div name="Opening identity" style={{
        position:"absolute",left:192,top:144,fontSize:34,letterSpacing:6,fontWeight:600,color:"#B2DBCF",
      }}>AGRICULTURE. ENERGY. OPPORTUNITY.</Interactive.Div>
      <Interactive.Div name="Harvest title" style={{
        position:"absolute",left:180,top:440,fontSize:290,fontWeight:500,lineHeight:1,
        letterSpacing:-14,
        opacity:interpolate(frame,[0,0.7 * fps,2.7 * fps,3.2 * fps],[0,1,1,0],
          {extrapolateLeft:"clamp",extrapolateRight:"clamp"}),
        translate:interpolate(frame,[0,0.9 * fps],["0px 100px","0px 0px"],
          {extrapolateRight:"clamp",easing:Easing.bezier(.16,1,.3,1)}),
      }}>A harvest is<br/>only the beginning.</Interactive.Div>
      <Interactive.Div name="Energy title" style={{
        position:"absolute",left:180,top:540,fontSize:300,fontWeight:500,lineHeight:1,
        letterSpacing:-14,
        opacity:interpolate(frame,[3 * fps,3.5 * fps],[0,1],
          {extrapolateLeft:"clamp",extrapolateRight:"clamp"}),
        translate:interpolate(frame,[3 * fps,3.9 * fps],["0px 80px","0px 0px"],
          {extrapolateLeft:"clamp",extrapolateRight:"clamp",easing:Easing.bezier(.16,1,.3,1)}),
      }}>What comes next<br/>needs <span style={{color:"#6FE6BC"}}>energy.</span></Interactive.Div>
      <Interactive.Div name="Opening rule" style={{
        position:"absolute",left:192,top:1380,width:180,height:5,backgroundColor:"#00BD94",
        scale:interpolate(frame,[0.5 * fps,1.5 * fps],[0,1],{extrapolateLeft:"clamp",extrapolateRight:"clamp"}),
        transformOrigin:"left",
      }}/>
      <div style={{position:"absolute",left:192,bottom:150,color:"#B6CFCD",fontSize:26}}>
        Concept illustration
      </div>
      {captions ? <BasicCaptions name="Opening narration" premountFor={fps} width={2800}
        style={{position:"absolute",left:520,bottom:56}} captions={[
          {text:"A harvest is only the beginning.",startMs:200,endMs:2700,timestampMs:null,confidence:null,pageBreakAfter:true},
          {text:"What happens next depends on energy.",startMs:3000,endMs:5800,timestampMs:null,confidence:null,pageBreakAfter:true},
        ]}/> : null}
    </Frame>
  );
};
