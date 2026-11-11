import {Audio} from "@remotion/media";
import {staticFile,useVideoConfig} from "remotion";
import {BasicCaptions} from "../../components/basic-captions";
import {StoryVisual} from "../StoryVisual";
export const DemandStory=({captions}:{captions:boolean})=>{
 const {fps}=useVideoConfig();
 return <>
  <StoryVisual id="demand"/>
  <Audio name="demand · English Ava narration" src={staticFile("story/audio/demand-normalized.mp3")} from={0.25*fps} premountFor={fps}/>
  {captions?<div className="story-captions"><BasicCaptions name="demand · timed captions" width={1640} premountFor={fps} style={{position:"absolute",left:140,bottom:34}} captions={[
    {
        "text": "Open the site card.",
        "startMs": 350,
        "endMs": 1592,
        "timestampMs": null,
        "confidence": null,
        "pageBreakAfter": true
    },
    {
        "text": "This example estimates electricity needed on a",
        "startMs": 1775,
        "endMs": 4437,
        "timestampMs": null,
        "confidence": null,
        "pageBreakAfter": true
    },
    {
        "text": "busy harvest day.",
        "startMs": 4462,
        "endMs": 5780,
        "timestampMs": null,
        "confidence": null,
        "pageBreakAfter": true
    },
    {
        "text": "The range shows how much that estimate",
        "startMs": 5962,
        "endMs": 7937,
        "timestampMs": null,
        "confidence": null,
        "pageBreakAfter": true
    },
    {
        "text": "could change.",
        "startMs": 7962,
        "endMs": 9155,
        "timestampMs": null,
        "confidence": null,
        "pageBreakAfter": true
    }
]}/></div>:null}
 </>;
};
