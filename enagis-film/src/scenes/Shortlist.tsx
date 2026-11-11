import {useVideoConfig} from "remotion";
import type {SceneProps} from "../design";
import {ProductShot} from "../components/ProductShot";
import {BasicCaptions} from "../components/basic-captions";

export const Shortlist = ({captions}: SceneProps) => {
  const {fps} = useVideoConfig();
  return <>
    <ProductShot id="shortlist" number="07"
      title="Leave with a shortlist." subtitle="Ranked places, supporting evidence, and the next question."/>
    {captions ? <BasicCaptions name="Shortlist narration" premountFor={fps} width={2800}
      style={{position:"absolute",left:520,bottom:56}}
      captions={[
        {
                "text": "Export a ranked shortlist,",
                "startMs": 400,
                "endMs": 3400,
                "timestampMs": null,
                "confidence": null,
                "pageBreakAfter": true
        },
        {
                "text": "the supporting evidence,",
                "startMs": 3600,
                "endMs": 6000,
                "timestampMs": null,
                "confidence": null,
                "pageBreakAfter": true
        },
        {
                "text": "and the question to ask at each site.",
                "startMs": 6200,
                "endMs": 9400,
                "timestampMs": null,
                "confidence": null,
                "pageBreakAfter": true
        }
]}/> : null}
  </>;
};
