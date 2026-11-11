import {Composition, Folder} from "remotion";
import {EditorialPreview, Film} from "./Film";
import {Harvest} from "./scenes/Harvest";
import {Introduce} from "./scenes/Introduce";
import {Search} from "./scenes/Search";
import {Evidence} from "./scenes/Evidence";
import {Access} from "./scenes/Access";
import {Demand} from "./scenes/Demand";
import {Uncertainty} from "./scenes/Uncertainty";
import {Predictions} from "./scenes/Predictions";
import {Shortlist} from "./scenes/Shortlist";
import {Close} from "./scenes/Close";
import {CommercialFilm} from "./v2/CommercialFilm";
import {HookV2} from "./v2/scenes/HookV2";
import {BrandV2} from "./v2/scenes/BrandV2";
import {SearchV2} from "./v2/scenes/SearchV2";
import {EvidenceV2} from "./v2/scenes/EvidenceV2";
import {AccessV2} from "./v2/scenes/AccessV2";
import {EnergyV2} from "./v2/scenes/EnergyV2";
import {DemandV2} from "./v2/scenes/DemandV2";
import {ConfidenceV2} from "./v2/scenes/ConfidenceV2";
import {DiscoverV2} from "./v2/scenes/DiscoverV2";
import {ShortlistV2} from "./v2/scenes/ShortlistV2";
import {CloseV2} from "./v2/scenes/CloseV2";
import {UserStoryFilm} from "./story/UserStoryFilm";
import {DecisionStory} from "./story/scenes/DecisionStory";
import {PlaceStory} from "./story/scenes/PlaceStory";
import {RankingStory} from "./story/scenes/RankingStory";
import {HarvestStory} from "./story/scenes/HarvestStory";
import {AccessStory} from "./story/scenes/AccessStory";
import {EnergyStory} from "./story/scenes/EnergyStory";
import {DemandStory} from "./story/scenes/DemandStory";
import {ConfidenceStory} from "./story/scenes/ConfidenceStory";
import {DiscoverStory} from "./story/scenes/DiscoverStory";
import {EvidenceStory} from "./story/scenes/EvidenceStory";
import {ExportStory} from "./story/scenes/ExportStory";
import {OutcomeStory} from "./story/scenes/OutcomeStory";
import {OutroStory} from "./story/scenes/OutroStory";

export const RemotionRoot = () => (
  <>
    <Composition id="EnaGIS-UserStory-2min" component={UserStoryFilm} width={1920} height={1080} fps={30} durationInFrames={3600} defaultProps={{captions:true}}/>
    <Composition id="EnaGIS-UserStory-Clean" component={UserStoryFilm} width={1920} height={1080} fps={30} durationInFrames={3600} defaultProps={{captions:false}}/>
    <Folder name="User-Story-Scenes">
      <Composition id="DecisionStory" component={DecisionStory} width={1920} height={1080} fps={30} durationInFrames={210} defaultProps={{captions:true}}/>
      <Composition id="PlaceStory" component={PlaceStory} width={1920} height={1080} fps={30} durationInFrames={330} defaultProps={{captions:true}}/>
      <Composition id="RankingStory" component={RankingStory} width={1920} height={1080} fps={30} durationInFrames={240} defaultProps={{captions:true}}/>
      <Composition id="HarvestStory" component={HarvestStory} width={1920} height={1080} fps={30} durationInFrames={240} defaultProps={{captions:true}}/>
      <Composition id="AccessStory" component={AccessStory} width={1920} height={1080} fps={30} durationInFrames={300} defaultProps={{captions:true}}/>
      <Composition id="EnergyStory" component={EnergyStory} width={1920} height={1080} fps={30} durationInFrames={360} defaultProps={{captions:true}}/>
      <Composition id="DemandStory" component={DemandStory} width={1920} height={1080} fps={30} durationInFrames={330} defaultProps={{captions:true}}/>
      <Composition id="ConfidenceStory" component={ConfidenceStory} width={1920} height={1080} fps={30} durationInFrames={330} defaultProps={{captions:true}}/>
      <Composition id="DiscoverStory" component={DiscoverStory} width={1920} height={1080} fps={30} durationInFrames={210} defaultProps={{captions:true}}/>
      <Composition id="EvidenceStory" component={EvidenceStory} width={1920} height={1080} fps={30} durationInFrames={270} defaultProps={{captions:true}}/>
      <Composition id="ExportStory" component={ExportStory} width={1920} height={1080} fps={30} durationInFrames={300} defaultProps={{captions:true}}/>
      <Composition id="OutcomeStory" component={OutcomeStory} width={1920} height={1080} fps={30} durationInFrames={180} defaultProps={{captions:true}}/>
      <Composition id="OutroStory" component={OutroStory} width={1920} height={1080} fps={30} durationInFrames={300} defaultProps={{captions:true}}/>
    </Folder>
    <Composition id="EnaGIS-Commercial-V2" component={CommercialFilm}
      width={3840} height={2160} fps={30} durationInFrames={3210}
      defaultProps={{captions:true}}/>
    <Composition id="EnaGIS-Commercial-V2-Clean" component={CommercialFilm}
      width={3840} height={2160} fps={30} durationInFrames={3210}
      defaultProps={{captions:false}}/>
    <Composition id="EnaGIS-ProductFilm" component={Film}
      width={3840} height={2160} fps={30} durationInFrames={3300}
      defaultProps={{captions:true,deliveryMode:true,voiceover:"audio/narration.wav"}}/>
    <Composition id="EnaGIS-CleanFilm" component={Film}
      width={3840} height={2160} fps={30} durationInFrames={3300}
      defaultProps={{captions:false,deliveryMode:true,voiceover:"audio/narration.wav"}}/>
    <Composition id="EnaGIS-EditorialPreview" component={EditorialPreview}
      width={3840} height={2160} fps={30} durationInFrames={600}/>
    <Folder name="Commercial-V2-Scenes">
      <Composition id="HookV2" component={HookV2} width={3840} height={2160} fps={30} durationInFrames={180} defaultProps={{captions:true}}/>
      <Composition id="BrandV2" component={BrandV2} width={3840} height={2160} fps={30} durationInFrames={150} defaultProps={{captions:true}}/>
      <Composition id="SearchV2" component={SearchV2} width={3840} height={2160} fps={30} durationInFrames={330} defaultProps={{captions:true}}/>
      <Composition id="EvidenceV2" component={EvidenceV2} width={3840} height={2160} fps={30} durationInFrames={270} defaultProps={{captions:true}}/>
      <Composition id="AccessV2" component={AccessV2} width={3840} height={2160} fps={30} durationInFrames={300} defaultProps={{captions:true}}/>
      <Composition id="EnergyV2" component={EnergyV2} width={3840} height={2160} fps={30} durationInFrames={420} defaultProps={{captions:true}}/>
      <Composition id="DemandV2" component={DemandV2} width={3840} height={2160} fps={30} durationInFrames={390} defaultProps={{captions:true}}/>
      <Composition id="ConfidenceV2" component={ConfidenceV2} width={3840} height={2160} fps={30} durationInFrames={330} defaultProps={{captions:true}}/>
      <Composition id="DiscoverV2" component={DiscoverV2} width={3840} height={2160} fps={30} durationInFrames={270} defaultProps={{captions:true}}/>
      <Composition id="ShortlistV2" component={ShortlistV2} width={3840} height={2160} fps={30} durationInFrames={270} defaultProps={{captions:true}}/>
      <Composition id="CloseV2" component={CloseV2} width={3840} height={2160} fps={30} durationInFrames={300} defaultProps={{captions:true}}/>
    </Folder>
    <Folder name="Scenes">
      <Composition id="Harvest" component={Harvest} width={3840} height={2160}
        fps={30} durationInFrames={180} defaultProps={{captions:true}}/>
      <Composition id="Introduce" component={Introduce} width={3840} height={2160}
        fps={30} durationInFrames={180} defaultProps={{captions:true}}/>
      <Composition id="Search" component={Search} width={3840} height={2160}
        fps={30} durationInFrames={420} defaultProps={{captions:true}}/>
      <Composition id="Evidence" component={Evidence} width={3840} height={2160}
        fps={30} durationInFrames={360} defaultProps={{captions:true}}/>
      <Composition id="Access" component={Access} width={3840} height={2160}
        fps={30} durationInFrames={360} defaultProps={{captions:true}}/>
      <Composition id="Demand" component={Demand} width={3840} height={2160}
        fps={30} durationInFrames={510} defaultProps={{captions:true}}/>
      <Composition id="Uncertainty" component={Uncertainty} width={3840} height={2160}
        fps={30} durationInFrames={420} defaultProps={{captions:true}}/>
      <Composition id="Predictions" component={Predictions} width={3840} height={2160}
        fps={30} durationInFrames={330} defaultProps={{captions:true}}/>
      <Composition id="Shortlist" component={Shortlist} width={3840} height={2160}
        fps={30} durationInFrames={300} defaultProps={{captions:true}}/>
      <Composition id="Close" component={Close} width={3840} height={2160}
        fps={30} durationInFrames={240} defaultProps={{captions:true}}/>
    </Folder>
  </>
);
