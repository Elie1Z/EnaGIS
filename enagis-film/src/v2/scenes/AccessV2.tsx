import {Audio} from "@remotion/media";
import {staticFile,useVideoConfig} from "remotion";
import {BasicCaptions} from "../../components/basic-captions";
import {AdScene} from "../AdScene";
export const AccessV2 = ({captions}:{captions:boolean}) => {
 const {fps}=useVideoConfig();
 return <>
  <AdScene id="access"/>
  <Audio name="Access · neural female narration" from={0.35*fps} src={staticFile("v2/audio/access-normalized.mp3")} premountFor={fps}/>
  {captions ? <div className="ad-captions"><BasicCaptions name="Access · captions" premountFor={fps} width={3040}
    style={{position:"absolute",left:400,bottom:70}}
    captions={[
      {
            "text": "Follow real roads.",
            "startMs": 473,
            "endMs": 1750,
            "timestampMs": null,
            "confidence": null,
            "pageBreakAfter": true
      },
      {
            "text": "Compare dry and rainy seasons.",
            "startMs": 1955,
            "endMs": 4630,
            "timestampMs": null,
            "confidence": null,
            "pageBreakAfter": true
      },
      {
            "text": "Understand what each location can reach.",
            "startMs": 4872,
            "endMs": 7673,
            "timestampMs": null,
            "confidence": null,
            "pageBreakAfter": true
      }
]}/></div> : null}
 </>;
};
