import {useVideoConfig} from "remotion";
import type {SceneProps} from "../design";
import {ProductShot} from "../components/ProductShot";
import {BasicCaptions} from "../components/basic-captions";

export const Demand = ({captions}: SceneProps) => {
  const {fps} = useVideoConfig();
  return <>
    <ProductShot id="demand" number="04"
      title="Estimate the need." subtitle="An energy estimate, its range, and the assumptions behind it."/>
    {captions ? <BasicCaptions name="Demand narration" premountFor={fps} width={2800}
      style={{position:"absolute",left:520,bottom:56}}
      captions={[
        {
                "text": "Open a promising site.",
                "startMs": 400,
                "endMs": 3900,
                "timestampMs": null,
                "confidence": null,
                "pageBreakAfter": true
        },
        {
                "text": "See estimated energy demand",
                "startMs": 4100,
                "endMs": 8000,
                "timestampMs": null,
                "confidence": null,
                "pageBreakAfter": true
        },
        {
                "text": "with a range around it,",
                "startMs": 8200,
                "endMs": 11900,
                "timestampMs": null,
                "confidence": null,
                "pageBreakAfter": true
        },
        {
                "text": "and the assumptions behind the number.",
                "startMs": 12100,
                "endMs": 16400,
                "timestampMs": null,
                "confidence": null,
                "pageBreakAfter": true
        }
]}/> : null}
  </>;
};
