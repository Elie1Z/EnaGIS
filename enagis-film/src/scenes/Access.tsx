import {useVideoConfig} from "remotion";
import type {SceneProps} from "../design";
import {ProductShot} from "../components/ProductShot";
import {BasicCaptions} from "../components/basic-captions";

export const Access = ({captions}: SceneProps) => {
  const {fps} = useVideoConfig();
  return <>
    <ProductShot id="access" number="03"
      title="Understand what is in reach." subtitle="The same place. Two seasons. Different access."/>
    {captions ? <BasicCaptions name="Access narration" premountFor={fps} width={2800}
      style={{position:"absolute",left:520,bottom:56}}
      captions={[
        {
                "text": "Follow the roads.",
                "startMs": 400,
                "endMs": 3200,
                "timestampMs": null,
                "confidence": null,
                "pageBreakAfter": true
        },
        {
                "text": "Compare the seasons.",
                "startMs": 3400,
                "endMs": 6400,
                "timestampMs": null,
                "confidence": null,
                "pageBreakAfter": true
        },
        {
                "text": "See how access changes when conditions do.",
                "startMs": 6600,
                "endMs": 11400,
                "timestampMs": null,
                "confidence": null,
                "pageBreakAfter": true
        }
]}/> : null}
  </>;
};
