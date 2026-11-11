import {Audio} from "@remotion/media";
import {AbsoluteFill,Series,staticFile,useVideoConfig} from "remotion";
import {DecisionStory} from "./scenes/DecisionStory";
import {PlaceStory} from "./scenes/PlaceStory";
import {RankingStory} from "./scenes/RankingStory";
import {HarvestStory} from "./scenes/HarvestStory";
import {AccessStory} from "./scenes/AccessStory";
import {EnergyStory} from "./scenes/EnergyStory";
import {DemandStory} from "./scenes/DemandStory";
import {ConfidenceStory} from "./scenes/ConfidenceStory";
import {DiscoverStory} from "./scenes/DiscoverStory";
import {EvidenceStory} from "./scenes/EvidenceStory";
import {ExportStory} from "./scenes/ExportStory";
import {OutcomeStory} from "./scenes/OutcomeStory";
import {OutroStory} from "./scenes/OutroStory";

export const UserStoryFilm=({captions}:{captions:boolean})=>{
 const {fps}=useVideoConfig();
 return <AbsoluteFill style={{background:"#041E2D"}}>
  <style>{`.story-captions > div > div {font-family:Inter,sans-serif !important;font-size:28px !important;line-height:1.3 !important;letter-spacing:-.35px;background:rgba(3,22,32,.94) !important;border:1px solid #35545A;border-radius:9px;padding:8px 18px !important;box-shadow:0 3px 16px #00132040;}`}</style>
  <Series>
   <Series.Sequence name="01 · The cold-storage decision" durationInFrames={7*fps} premountFor={fps}><DecisionStory captions={captions}/></Series.Sequence>
   <Series.Sequence name="02 · Choose the area and purpose" durationInFrames={11*fps} premountFor={fps}><PlaceStory captions={captions}/></Series.Sequence>
   <Series.Sequence name="03 · Start with a ranked site" durationInFrames={8*fps} premountFor={fps}><RankingStory captions={captions}/></Series.Sequence>
   <Series.Sequence name="04 · Understand the harvest" durationInFrames={8*fps} premountFor={fps}><HarvestStory captions={captions}/></Series.Sequence>
   <Series.Sequence name="05 · Compare road access and seasons" durationInFrames={10*fps} premountFor={fps}><AccessStory captions={captions}/></Series.Sequence>
   <Series.Sequence name="06 · Check energy options" durationInFrames={12*fps} premountFor={fps}><EnergyStory captions={captions}/></Series.Sequence>
   <Series.Sequence name="07 · Read electricity need and uncertainty" durationInFrames={11*fps} premountFor={fps}><DemandStory captions={captions}/></Series.Sequence>
   <Series.Sequence name="08 · See whether the choice holds up" durationInFrames={11*fps} premountFor={fps}><ConfidenceStory captions={captions}/></Series.Sequence>
   <Series.Sequence name="09 · Investigate predicted places" durationInFrames={7*fps} premountFor={fps}><DiscoverStory captions={captions}/></Series.Sequence>
   <Series.Sequence name="10 · Inspect map gaps and sources" durationInFrames={9*fps} premountFor={fps}><EvidenceStory captions={captions}/></Series.Sequence>
   <Series.Sequence name="11 · Export save and verify" durationInFrames={10*fps} premountFor={fps}><ExportStory captions={captions}/></Series.Sequence>
   <Series.Sequence name="12 · A practical next step" durationInFrames={6*fps} premountFor={fps}><OutcomeStory captions={captions}/></Series.Sequence>
   <Series.Sequence name="13 · Creator outro and official motto" durationInFrames={10*fps} premountFor={fps}><OutroStory captions={captions}/></Series.Sequence>
  </Series>
  <Audio name="Original story score" src={staticFile("story/audio/score.mp3")} premountFor={fps}/>
  <Audio name="Measured interactions and soft accents" src={staticFile("story/audio/effects.mp3")} premountFor={fps}/>
 </AbsoluteFill>;
};
