import {Audio,Video} from "@remotion/media";
import {staticFile,useVideoConfig} from "remotion";
import {BasicCaptions} from "../../components/basic-captions";

export const OutroStory=({captions}:{captions:boolean})=>{
 const {fps}=useVideoConfig();
 return <>
  <Video name="Creator outro · full ten seconds" src={staticFile("v2/video/enagis-outro.mp4")} muted premountFor={fps} objectFit="contain" style={{position:"absolute",inset:0,width:"100%",height:"100%"}}/>
  <Audio name="outro · English Ava narration" src={staticFile("story/audio/outro-normalized.mp3")} from={3.2*fps} premountFor={fps}/>
  {captions?<div className="story-captions"><BasicCaptions name="outro · timed captions" width={1640} premountFor={fps} style={{position:"absolute",left:140,bottom:34}} captions={[
    {
        "text": "EnaGIS.",
        "startMs": 3300,
        "endMs": 4399,
        "timestampMs": null,
        "confidence": null,
        "pageBreakAfter": true
    },
    {
        "text": "Mapping Energy.",
        "startMs": 4574,
        "endMs": 5685,
        "timestampMs": null,
        "confidence": null,
        "pageBreakAfter": true
    },
    {
        "text": "Powering Agriculture.",
        "startMs": 5860,
        "endMs": 7540,
        "timestampMs": null,
        "confidence": null,
        "pageBreakAfter": true
    }
]}/></div>:null}
 </>;
};
