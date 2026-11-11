import {Audio} from "@remotion/media";
import {staticFile,useVideoConfig} from "remotion";
import {BasicCaptions} from "../../components/basic-captions";
import {StoryVisual} from "../StoryVisual";
export const DecisionStory=({captions}:{captions:boolean})=>{
 const {fps}=useVideoConfig();
 return <>
  <StoryVisual id="decision"/>
  <Audio name="decision · English Ava narration" src={staticFile("story/audio/decision-normalized.mp3")} from={0.25*fps} premountFor={fps}/>
  {captions?<div className="story-captions"><BasicCaptions name="decision · timed captions" width={1640} premountFor={fps} style={{position:"absolute",left:140,bottom:34}} captions={[
    {
        "text": "You're planning a cold store for potato",
        "startMs": 350,
        "endMs": 2194,
        "timestampMs": null,
        "confidence": null,
        "pageBreakAfter": true
    },
    {
        "text": "growers.",
        "startMs": 2219,
        "endMs": 2954,
        "timestampMs": null,
        "confidence": null,
        "pageBreakAfter": true
    },
    {
        "text": "Where should you investigate first?",
        "startMs": 3141,
        "endMs": 5187,
        "timestampMs": null,
        "confidence": null,
        "pageBreakAfter": true
    }
]}/></div>:null}
 </>;
};
