import {useVideoConfig} from "remotion";
import type {SceneProps} from "../design";
import {ProductShot} from "../components/ProductShot";
import {BasicCaptions} from "../components/basic-captions";

export const Evidence = ({captions}: SceneProps) => {
  const {fps} = useVideoConfig();
  return <>
    <ProductShot id="evidence" number="02"
      title="Connect the evidence." subtitle="Mapped activity and the areas each candidate can reach."/>
    {captions ? <BasicCaptions name="Evidence narration" premountFor={fps} width={2800}
      style={{position:"absolute",left:520,bottom:56}}
      captions={[
        {
                "text": "EnaGIS brings open maps and agricultural evidence together,",
                "startMs": 400,
                "endMs": 4600,
                "timestampMs": null,
                "confidence": null,
                "pageBreakAfter": true
        },
        {
                "text": "revealing mapped activity",
                "startMs": 4800,
                "endMs": 8100,
                "timestampMs": null,
                "confidence": null,
                "pageBreakAfter": true
        },
        {
                "text": "and the areas each candidate can reach.",
                "startMs": 8300,
                "endMs": 11600,
                "timestampMs": null,
                "confidence": null,
                "pageBreakAfter": true
        }
]}/> : null}
  </>;
};
