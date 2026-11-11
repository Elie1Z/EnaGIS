import {Audio} from "@remotion/media";
import {AbsoluteFill, Sequence, Series, staticFile, useVideoConfig} from "remotion";
import {missingShots} from "./capture";
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

export type FilmProps = {
  captions: boolean;
  deliveryMode: boolean;
  voiceover: string;
};

export const Film = ({captions,deliveryMode,voiceover}: FilmProps) => {
  const {fps} = useVideoConfig();
  const missing = missingShots();
  if (deliveryMode && (missing.length || !voiceover)) {
    throw new Error(
      `Submission blocked: ${missing.length} satellite shots await capture/review. ` +
      `${voiceover ? "Voiceover supplied." : "Voiceover is missing."} ` +
      "Keep deliveryMode=false for the working preview.",
    );
  }
  return <AbsoluteFill>
    <Series>
      <Series.Sequence name="01 · Harvest and energy" durationInFrames={6 * fps} premountFor={fps}>
        <Harvest captions={captions}/>
      </Series.Sequence>
      <Series.Sequence name="02 · Introduce EnaGIS" durationInFrames={6 * fps} premountFor={fps}>
        <Introduce captions={captions}/>
      </Series.Sequence>
      <Series.Sequence name="03 · Start with a place" durationInFrames={14 * fps} premountFor={fps}>
        <Search captions={captions}/>
      </Series.Sequence>
      <Series.Sequence name="04 · Connect the evidence" durationInFrames={12 * fps} premountFor={fps}>
        <Evidence captions={captions}/>
      </Series.Sequence>
      <Series.Sequence name="05 · Roads and seasons" durationInFrames={12 * fps} premountFor={fps}>
        <Access captions={captions}/>
      </Series.Sequence>
      <Series.Sequence name="06 · Energy and assumptions" durationInFrames={17 * fps} premountFor={fps}>
        <Demand captions={captions}/>
      </Series.Sequence>
      <Series.Sequence name="07 · Uncertainty and data gaps" durationInFrames={14 * fps} premountFor={fps}>
        <Uncertainty captions={captions}/>
      </Series.Sequence>
      <Series.Sequence name="08 · Predicted places to check" durationInFrames={11 * fps} premountFor={fps}>
        <Predictions captions={captions}/>
      </Series.Sequence>
      <Series.Sequence name="09 · The next investigation" durationInFrames={10 * fps} premountFor={fps}>
        <Shortlist captions={captions}/>
      </Series.Sequence>
      <Series.Sequence name="10 · Product invitation" durationInFrames={8 * fps} premountFor={fps}>
        <Close captions={captions}/>
      </Series.Sequence>
    </Series>
    {voiceover ? <Audio name="Product narration" src={staticFile(voiceover)} premountFor={fps}/> : null}
    <Audio name="Original instrumental score" src={staticFile("audio/original-score.wav")} premountFor={fps}/>
    <Audio name="Subtle interaction accents" src={staticFile("audio/interaction-sound.wav")} premountFor={fps}/>
  </AbsoluteFill>;
};

// Short visual-direction sample, retained alongside the complete product film.
export const EditorialPreview = () => {
  const {fps} = useVideoConfig();
  return <AbsoluteFill>
    <Sequence name="Opening image and statement" durationInFrames={6 * fps} premountFor={fps}>
      <Harvest captions={false}/>
    </Sequence>
    <Sequence name="Question and brand" from={6 * fps} durationInFrames={6 * fps} premountFor={fps}>
      <Introduce captions={false}/>
    </Sequence>
    <Sequence name="Closing identity and website" from={12 * fps} durationInFrames={8 * fps} premountFor={fps}>
      <Close captions={false}/>
    </Sequence>
    <Audio name="Opening music" src={staticFile("audio/original-score.wav")} premountFor={fps}/>
  </AbsoluteFill>;
};
