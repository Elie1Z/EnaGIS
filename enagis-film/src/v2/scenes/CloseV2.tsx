import {Audio,Video} from "@remotion/media";
import {staticFile,useVideoConfig} from "remotion";
import {BasicCaptions} from "../../components/basic-captions";

export const CloseV2 = ({captions}:{captions:boolean}) => {
 const {fps}=useVideoConfig();
 return <>
  <Video name="Creator-supplied EnaGIS outro" src={staticFile("v2/video/enagis-outro.mp4")} muted premountFor={fps} style={{position:"absolute",inset:0,width:"100%",height:"100%"}} objectFit="contain"/>
  <Audio name="Close · neural female narration" from={3.2*fps} src={staticFile("v2/audio/close-normalized.mp3")} premountFor={fps}/>
  {captions ? <div className="ad-captions"><BasicCaptions name="Close · captions" premountFor={fps} width={3040}
    style={{position:"absolute",left:400,bottom:70}}
    captions={[
      {
            "text": "EnaGIS.",
            "startMs": 3300,
            "endMs": 4369,
            "timestampMs": null,
            "confidence": null,
            "pageBreakAfter": true
      },
      {
            "text": "Mapping Energy.",
            "startMs": 4574,
            "endMs": 5655,
            "timestampMs": null,
            "confidence": null,
            "pageBreakAfter": true
      },
      {
            "text": "Powering Agriculture.",
            "startMs": 5860,
            "endMs": 7460,
            "timestampMs": null,
            "confidence": null,
            "pageBreakAfter": true
      }
]}/></div> : null}
 </>;
};
