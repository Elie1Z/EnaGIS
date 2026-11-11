import {Audio} from "@remotion/media";
import {staticFile,useVideoConfig} from "remotion";
import {BasicCaptions} from "../../components/basic-captions";
import {StoryVisual} from "../StoryVisual";
export const PlaceStory=({captions}:{captions:boolean})=>{
 const {fps}=useVideoConfig();
 return <>
  <StoryVisual id="place"/>
  <Audio name="place · English Ava narration" src={staticFile("story/audio/place-normalized.mp3")} from={0.25*fps} premountFor={fps}/>
  {captions?<div className="story-captions"><BasicCaptions name="place · timed captions" width={1640} premountFor={fps} style={{position:"absolute",left:140,bottom:34}} captions={[
    {
        "text": "Search your area and choose cold storage.",
        "startMs": 350,
        "endMs": 2980,
        "timestampMs": null,
        "confidence": null,
        "pageBreakAfter": true
    },
    {
        "text": "Here, we open a saved analysis, so",
        "startMs": 3162,
        "endMs": 5613,
        "timestampMs": null,
        "confidence": null,
        "pageBreakAfter": true
    },
    {
        "text": "every step follows the same example.",
        "startMs": 5638,
        "endMs": 8305,
        "timestampMs": null,
        "confidence": null,
        "pageBreakAfter": true
    }
]}/></div>:null}
 </>;
};
