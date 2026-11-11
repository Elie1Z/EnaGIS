import {CanvasImage, Easing, Interactive, interpolate, staticFile, useCurrentFrame, useVideoConfig} from "remotion";
import type {SceneProps} from "../design";
import {Frame} from "../components/Frame";
import {BasicCaptions} from "../components/basic-captions";

export const Introduce = ({captions}: SceneProps) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  return <Frame>
    <Interactive.Div name="Investment question" style={{
      position:"absolute",left:192,top:560,width:3400,fontFamily:"Fraunces",
      fontSize:248,fontWeight:500,letterSpacing:-2,lineHeight:1.12,
      opacity:interpolate(frame,[0,0.5 * fps,3.2 * fps,3.7 * fps],[0,1,1,0],{extrapolateRight:"clamp"}),
      translate:interpolate(frame,[0,0.8 * fps],["0px 60px","0px 0px"],
        {extrapolateRight:"clamp",easing:Easing.bezier(.16,1,.3,1)}),
    }}>Where should agricultural<br/><span style={{color:"#087A64"}}>energy investment</span> begin?</Interactive.Div>
    <CanvasImage name="Authentic EnaGIS wordmark" src={staticFile("brand/enagis-wordmark.png")}
      premountFor={fps} style={{position:"absolute",left:600,top:690,width:2640,height:"auto",
        opacity:interpolate(frame,[3.5 * fps,4.2 * fps],[0,1],{extrapolateLeft:"clamp",extrapolateRight:"clamp"}),
        scale:interpolate(frame,[3.5 * fps,4.6 * fps],[0.94,1],{
          extrapolateLeft:"clamp",extrapolateRight:"clamp",output:"perceptual-scale",
          easing:Easing.bezier(.16,1,.3,1)}),
      }}/>
    <Interactive.Div name="Brand purpose" style={{
      position:"absolute",left:600,top:1430,width:2640,textAlign:"center",fontSize:66,color:"#677F83",
      opacity:interpolate(frame,[4.1 * fps,4.6 * fps],[0,1],{extrapolateLeft:"clamp",extrapolateRight:"clamp"}),
    }}>From open maps to your next move.</Interactive.Div>
    {captions ? <BasicCaptions name="Introduction narration" premountFor={fps} width={2800}
      style={{position:"absolute",left:520,bottom:56}} captions={[
        {text:"But where should agricultural energy investment begin?",startMs:100,endMs:3400,timestampMs:null,confidence:null,pageBreakAfter:true},
        {text:"Meet EnaGIS.",startMs:3700,endMs:5700,timestampMs:null,confidence:null,pageBreakAfter:true},
      ]}/> : null}
  </Frame>;
};
