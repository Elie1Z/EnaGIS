import {Audio} from "@remotion/media";
import {staticFile,useVideoConfig} from "remotion";
import {BasicCaptions} from "../../components/basic-captions";
import {AdScene} from "../AdScene";
export const ConfidenceV2 = ({captions}:{captions:boolean}) => {
 const {fps}=useVideoConfig();
 return <>
  <AdScene id="confidence"/>
  <Audio name="Confidence · neural female narration" from={0.35*fps} src={staticFile("v2/audio/confidence-normalized.mp3")} premountFor={fps}/>
  {captions ? <div className="ad-captions"><BasicCaptions name="Confidence · captions" premountFor={fps} width={3040}
    style={{position:"absolute",left:400,bottom:70}}
    captions={[
      {
            "text": "Challenge those assumptions across 300 scenarios.",
            "startMs": 448,
            "endMs": 3772,
            "timestampMs": null,
            "confidence": null,
            "pageBreakAfter": true
      },
      {
            "text": "See which sites hold their place,",
            "startMs": 4026,
            "endMs": 5847,
            "timestampMs": null,
            "confidence": null,
            "pageBreakAfter": true
      },
      {
            "text": "and where the evidence needs work.",
            "startMs": 5877,
            "endMs": 7869,
            "timestampMs": null,
            "confidence": null,
            "pageBreakAfter": true
      }
]}/></div> : null}
 </>;
};
