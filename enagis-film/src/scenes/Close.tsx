import {CanvasImage, Easing, Interactive, interpolate, staticFile, useCurrentFrame, useVideoConfig} from "remotion";
import type {SceneProps} from "../design";
import {Frame} from "../components/Frame";
import {BasicCaptions} from "../components/basic-captions";

export const Close = ({captions}: SceneProps) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  return <Frame>
    <div style={{position:"absolute",left:0,top:0,width:36,height:2160,backgroundColor:"#00BD94"}}/>
    <CanvasImage name="EnaGIS closing wordmark" src={staticFile("brand/enagis-wordmark.png")}
      premountFor={fps} style={{position:"absolute",left:192,top:260,width:1410,height:"auto",
        opacity:interpolate(frame,[0,0.7 * fps],[0,1],{extrapolateRight:"clamp"})}}/>
    <Interactive.Div name="Closing statement" style={{
      position:"absolute",left:180,top:810,width:3440,fontSize:264,fontWeight:500,
      letterSpacing:-9,lineHeight:1.08,
      translate:interpolate(frame,[0,0.9 * fps],["0px 60px","0px 0px"],
        {extrapolateRight:"clamp",easing:Easing.bezier(.16,1,.3,1)}),
      opacity:interpolate(frame,[0,0.6 * fps],[0,1],{extrapolateRight:"clamp"}),
    }}>From open maps<br/>to your <span style={{color:"#087A64"}}>next move.</span></Interactive.Div>
    <Interactive.Div name="Public product address" style={{
      position:"absolute",left:192,top:1510,fontSize:76,fontWeight:500,color:"#087A64",
      opacity:interpolate(frame,[0.6 * fps,1.2 * fps],[0,1],{extrapolateLeft:"clamp",extrapolateRight:"clamp"}),
    }}>enagis.netlify.app <span style={{marginLeft:28}}>↗</span></Interactive.Div>
    <Interactive.Div name="Team credit" style={{
      position:"absolute",left:192,bottom:230,fontSize:40,letterSpacing:2,color:"#677F83",
    }}>TEAM DYNAMIS</Interactive.Div>
    {captions ? <BasicCaptions name="Closing narration" premountFor={fps} width={2800}
      style={{position:"absolute",left:520,bottom:56}} captions={[
        {text:"EnaGIS. From open maps to your next move.",startMs:200,endMs:4500,timestampMs:null,confidence:null,pageBreakAfter:true},
      ]}/> : null}
  </Frame>;
};
