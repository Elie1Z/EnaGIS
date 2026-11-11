import {useVideoConfig} from "remotion";
import type {SceneProps} from "../design";
import {ProductShot} from "../components/ProductShot";
import {BasicCaptions} from "../components/basic-captions";

export const Uncertainty = ({captions}: SceneProps) => {
  const {fps} = useVideoConfig();
  return <>
    <ProductShot id="uncertainty" number="05"
      title="See how sure." subtitle="300 scenarios. Ranking stability. Visible information gaps."/>
    {captions ? <BasicCaptions name="Uncertainty narration" premountFor={fps} width={2800}
      style={{position:"absolute",left:520,bottom:56}}
      captions={[
        {
                "text": "Stress-test the assumptions across 300 scenarios.",
                "startMs": 400,
                "endMs": 5000,
                "timestampMs": null,
                "confidence": null,
                "pageBreakAfter": true
        },
        {
                "text": "See what stays near the top,",
                "startMs": 5200,
                "endMs": 9000,
                "timestampMs": null,
                "confidence": null,
                "pageBreakAfter": true
        },
        {
                "text": "and where information is still missing.",
                "startMs": 9200,
                "endMs": 13400,
                "timestampMs": null,
                "confidence": null,
                "pageBreakAfter": true
        }
]}/> : null}
  </>;
};
