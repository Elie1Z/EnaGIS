import {Audio} from "@remotion/media";
import {staticFile,useVideoConfig} from "remotion";
import {BasicCaptions} from "../../components/basic-captions";
import {AdScene} from "../AdScene";
export const ShortlistV2 = ({captions}:{captions:boolean}) => {
 const {fps}=useVideoConfig();
 return <>
  <AdScene id="shortlist"/>
  <Audio name="Shortlist · neural female narration" from={0.35*fps} src={staticFile("v2/audio/shortlist-normalized.mp3")} premountFor={fps}/>
  {captions ? <div className="ad-captions"><BasicCaptions name="Shortlist · captions" premountFor={fps} width={3040}
    style={{position:"absolute",left:400,bottom:70}}
    captions={[
      {
            "text": "Take the next step.",
            "startMs": 436,
            "endMs": 1591,
            "timestampMs": null,
            "confidence": null,
            "pageBreakAfter": true
      },
      {
            "text": "Export a ranked shortlist, the evidence,",
            "startMs": 1796,
            "endMs": 4360,
            "timestampMs": null,
            "confidence": null,
            "pageBreakAfter": true
      },
      {
            "text": "and the questions that turn screening",
            "startMs": 4455,
            "endMs": 6411,
            "timestampMs": null,
            "confidence": null,
            "pageBreakAfter": true
      },
      {
            "text": "into investigation.",
            "startMs": 6441,
            "endMs": 7869,
            "timestampMs": null,
            "confidence": null,
            "pageBreakAfter": true
      }
]}/></div> : null}
 </>;
};
