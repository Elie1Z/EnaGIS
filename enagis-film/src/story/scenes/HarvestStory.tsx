import {Audio} from "@remotion/media";
import {staticFile,useVideoConfig} from "remotion";
import {BasicCaptions} from "../../components/basic-captions";
import {StoryVisual} from "../StoryVisual";
export const HarvestStory=({captions}:{captions:boolean})=>{
 const {fps}=useVideoConfig();
 return <>
  <StoryVisual id="harvest"/>
  <Audio name="harvest · English Ava narration" src={staticFile("story/audio/harvest-normalized.mp3")} from={0.25*fps} premountFor={fps}/>
  {captions?<div className="story-captions"><BasicCaptions name="harvest · timed captions" width={1640} premountFor={fps} style={{position:"absolute",left:140,bottom:34}} captions={[
    {
        "text": "Harvest shows where crops may come from.",
        "startMs": 350,
        "endMs": 2830,
        "timestampMs": null,
        "confidence": null,
        "pageBreakAfter": true
    },
    {
        "text": "These are estimates, built from production statistics",
        "startMs": 3012,
        "endMs": 5837,
        "timestampMs": null,
        "confidence": null,
        "pageBreakAfter": true
    },
    {
        "text": "and mapped homes.",
        "startMs": 5862,
        "endMs": 7530,
        "timestampMs": null,
        "confidence": null,
        "pageBreakAfter": true
    }
]}/></div>:null}
 </>;
};
