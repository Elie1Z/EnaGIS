import {Audio} from "@remotion/media";
import {staticFile,useVideoConfig} from "remotion";
import {BasicCaptions} from "../../components/basic-captions";
import {StoryVisual} from "../StoryVisual";
export const DiscoverStory=({captions}:{captions:boolean})=>{
 const {fps}=useVideoConfig();
 return <>
  <StoryVisual id="discover"/>
  <Audio name="discover · English Ava narration" src={staticFile("story/audio/discover-normalized.mp3")} from={0.2*fps} premountFor={fps}/>
  {captions?<div className="story-captions"><BasicCaptions name="discover · timed captions" width={1640} premountFor={fps} style={{position:"absolute",left:140,bottom:34}} captions={[
    {
        "text": "Likely sites finds places resembling known facilities.",
        "startMs": 300,
        "endMs": 3768,
        "timestampMs": null,
        "confidence": null,
        "pageBreakAfter": true
    },
    {
        "text": "These are leads to check, not confirmed",
        "startMs": 3950,
        "endMs": 5875,
        "timestampMs": null,
        "confidence": null,
        "pageBreakAfter": true
    },
    {
        "text": "businesses.",
        "startMs": 5900,
        "endMs": 6950,
        "timestampMs": null,
        "confidence": null,
        "pageBreakAfter": true
    }
]}/></div>:null}
 </>;
};
