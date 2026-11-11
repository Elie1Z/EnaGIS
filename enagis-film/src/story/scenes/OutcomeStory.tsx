import {Audio} from "@remotion/media";
import {staticFile,useVideoConfig} from "remotion";
import {BasicCaptions} from "../../components/basic-captions";
import {StoryVisual} from "../StoryVisual";
export const OutcomeStory=({captions}:{captions:boolean})=>{
 const {fps}=useVideoConfig();
 return <>
  <StoryVisual id="outcome"/>
  <Audio name="outcome · English Ava narration" src={staticFile("story/audio/outcome-normalized.mp3")} from={0.25*fps} premountFor={fps}/>
  {captions?<div className="story-captions"><BasicCaptions name="outcome · timed captions" width={1640} premountFor={fps} style={{position:"absolute",left:140,bottom:34}} captions={[
    {
        "text": "A clearer shortlist.",
        "startMs": 350,
        "endMs": 1879,
        "timestampMs": null,
        "confidence": null,
        "pageBreakAfter": true
    },
    {
        "text": "Reasons you can inspect.",
        "startMs": 2057,
        "endMs": 3586,
        "timestampMs": null,
        "confidence": null,
        "pageBreakAfter": true
    },
    {
        "text": "A practical next step.",
        "startMs": 3765,
        "endMs": 5507,
        "timestampMs": null,
        "confidence": null,
        "pageBreakAfter": true
    }
]}/></div>:null}
 </>;
};
