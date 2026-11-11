import {Audio} from "@remotion/media";
import {staticFile,useVideoConfig} from "remotion";
import {BasicCaptions} from "../../components/basic-captions";
import {AdScene} from "../AdScene";
export const EnergyV2 = ({captions}:{captions:boolean}) => {
 const {fps}=useVideoConfig();
 return <>
  <AdScene id="energy"/>
  <Audio name="Energy · neural female narration" from={0.35*fps} src={staticFile("v2/audio/energy-normalized.mp3")} premountFor={fps}/>
  {captions ? <div className="ad-captions"><BasicCaptions name="Energy · captions" premountFor={fps} width={3040}
    style={{position:"absolute",left:400,bottom:70}}
    captions={[
      {
            "text": "Open Energy.",
            "startMs": 448,
            "endMs": 1395,
            "timestampMs": null,
            "confidence": null,
            "pageBreakAfter": true
      },
      {
            "text": "See mapped power lines, nearby infrastructure,",
            "startMs": 1637,
            "endMs": 4777,
            "timestampMs": null,
            "confidence": null,
            "pageBreakAfter": true
      },
      {
            "text": "and an indicative solar option.",
            "startMs": 4823,
            "endMs": 6652,
            "timestampMs": null,
            "confidence": null,
            "pageBreakAfter": true
      },
      {
            "text": "A mapped line is a lead.",
            "startMs": 6870,
            "endMs": 8466,
            "timestampMs": null,
            "confidence": null,
            "pageBreakAfter": true
      },
      {
            "text": "Connection and capacity still need checking.",
            "startMs": 8683,
            "endMs": 11656,
            "timestampMs": null,
            "confidence": null,
            "pageBreakAfter": true
      }
]}/></div> : null}
 </>;
};
