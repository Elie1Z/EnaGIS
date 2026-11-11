import {Audio} from "@remotion/media";
import {AbsoluteFill,Series,staticFile,useVideoConfig} from "remotion";
import {HookV2} from "./scenes/HookV2";
import {BrandV2} from "./scenes/BrandV2";
import {SearchV2} from "./scenes/SearchV2";
import {EvidenceV2} from "./scenes/EvidenceV2";
import {AccessV2} from "./scenes/AccessV2";
import {EnergyV2} from "./scenes/EnergyV2";
import {DemandV2} from "./scenes/DemandV2";
import {ConfidenceV2} from "./scenes/ConfidenceV2";
import {DiscoverV2} from "./scenes/DiscoverV2";
import {ShortlistV2} from "./scenes/ShortlistV2";
import {CloseV2} from "./scenes/CloseV2";

export const CommercialFilm=({captions}:{captions:boolean})=>{
 const {fps}=useVideoConfig();
 return <AbsoluteFill>
  <style>{`.ad-captions > div > div {background:rgba(2,21,33,.91) !important;border:1px solid #31505A;border-radius:18px;padding:14px 30px !important;font-family:Inter,sans-serif !important;font-size:54px !important;letter-spacing:-.5px;line-height:1.25 !important;box-shadow:0 5px 20px #0003;}`}</style>
  <Series>
   <Series.Sequence name="01 · Harvest potential" durationInFrames={6*fps} premountFor={fps}><HookV2 captions={captions}/></Series.Sequence>
   <Series.Sequence name="02 · Official brand promise" durationInFrames={5*fps} premountFor={fps}><BrandV2 captions={captions}/></Series.Sequence>
   <Series.Sequence name="03 · Place and purpose" durationInFrames={11*fps} premountFor={fps}><SearchV2 captions={captions}/></Series.Sequence>
   <Series.Sequence name="04 · Connected evidence" durationInFrames={9*fps} premountFor={fps}><EvidenceV2 captions={captions}/></Series.Sequence>
   <Series.Sequence name="05 · Roads and seasons" durationInFrames={10*fps} premountFor={fps}><AccessV2 captions={captions}/></Series.Sequence>
   <Series.Sequence name="06 · Energy and supply" durationInFrames={14*fps} premountFor={fps}><EnergyV2 captions={captions}/></Series.Sequence>
   <Series.Sequence name="07 · Demand and assumptions" durationInFrames={13*fps} premountFor={fps}><DemandV2 captions={captions}/></Series.Sequence>
   <Series.Sequence name="08 · Confidence and evidence gaps" durationInFrames={11*fps} premountFor={fps}><ConfidenceV2 captions={captions}/></Series.Sequence>
   <Series.Sequence name="09 · Predicted investigation leads" durationInFrames={9*fps} premountFor={fps}><DiscoverV2 captions={captions}/></Series.Sequence>
   <Series.Sequence name="10 · Export and next conversation" durationInFrames={9*fps} premountFor={fps}><ShortlistV2 captions={captions}/></Series.Sequence>
   <Series.Sequence name="11 · Creator outro and official motto" durationInFrames={10*fps} premountFor={fps}><CloseV2 captions={captions}/></Series.Sequence>
  </Series>
  <Audio name="Original commercial score" src={staticFile("v2/audio/score.mp3")} premountFor={fps}/>
  <Audio name="Clicks and transition accents" src={staticFile("v2/audio/effects.mp3")} premountFor={fps}/>
 </AbsoluteFill>;
};
