import {Audio} from "@remotion/media";
import {staticFile,useVideoConfig} from "remotion";
import {BasicCaptions} from "../../components/basic-captions";
import {AdScene} from "../AdScene";
export const BrandV2 = ({captions}:{captions:boolean}) => {
 const {fps}=useVideoConfig();
 return <>
  <AdScene id="brand"/>
  <Audio name="Brand · neural female narration" from={0.35*fps} src={staticFile("v2/audio/brand-normalized.mp3")} premountFor={fps}/>
  {captions ? <div className="ad-captions"><BasicCaptions name="Brand · captions" premountFor={fps} width={3040}
    style={{position:"absolute",left:400,bottom:70}}
    captions={[
      {
            "text": "Meet EnaGIS.",
            "startMs": 450,
            "endMs": 1862,
            "timestampMs": null,
            "confidence": null,
            "pageBreakAfter": true
      },
      {
            "text": "Mapping Energy.",
            "startMs": 2067,
            "endMs": 3148,
            "timestampMs": null,
            "confidence": null,
            "pageBreakAfter": true
      },
      {
            "text": "Powering Agriculture.",
            "startMs": 3353,
            "endMs": 4850,
            "timestampMs": null,
            "confidence": null,
            "pageBreakAfter": true
      }
]}/></div> : null}
 </>;
};
