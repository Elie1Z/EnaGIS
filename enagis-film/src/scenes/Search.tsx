import {useVideoConfig} from "remotion";
import type {SceneProps} from "../design";
import {ProductShot} from "../components/ProductShot";
import {BasicCaptions} from "../components/basic-captions";

export const Search = ({captions}: SceneProps) => {
  const {fps} = useVideoConfig();
  return <>
    <ProductShot id="search" number="01"
      title="Start with a place." subtitle="A place. A value chain. A question worth investigating."/>
    {captions ? <BasicCaptions name="Search narration" premountFor={fps} width={2800}
      style={{position:"absolute",left:520,bottom:56}}
      captions={[
        {
                "text": "Start with a place.",
                "startMs": 400,
                "endMs": 3000,
                "timestampMs": null,
                "confidence": null,
                "pageBreakAfter": true
        },
        {
                "text": "Search the map, then choose what you want to study:",
                "startMs": 3200,
                "endMs": 6100,
                "timestampMs": null,
                "confidence": null,
                "pageBreakAfter": true
        },
        {
                "text": "cooling, storage, milling, or drying.",
                "startMs": 6300,
                "endMs": 12700,
                "timestampMs": null,
                "confidence": null,
                "pageBreakAfter": true
        }
]}/> : null}
  </>;
};
