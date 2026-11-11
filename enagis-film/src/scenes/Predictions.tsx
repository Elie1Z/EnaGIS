import {useVideoConfig} from "remotion";
import type {SceneProps} from "../design";
import {ProductShot} from "../components/ProductShot";
import {BasicCaptions} from "../components/basic-captions";

export const Predictions = ({captions}: SceneProps) => {
  const {fps} = useVideoConfig();
  return <>
    <ProductShot id="predictions" number="06"
      title="Find places to check." subtitle="Predicted opportunities alongside mapped locations."/>
    {captions ? <BasicCaptions name="Predictions narration" premountFor={fps} width={2800}
      style={{position:"absolute",left:520,bottom:56}}
      captions={[
        {
                "text": "Explore predicted places to check,",
                "startMs": 400,
                "endMs": 4800,
                "timestampMs": null,
                "confidence": null,
                "pageBreakAfter": true
        },
        {
                "text": "alongside the locations already recorded on the map.",
                "startMs": 5000,
                "endMs": 10400,
                "timestampMs": null,
                "confidence": null,
                "pageBreakAfter": true
        }
]}/> : null}
  </>;
};
