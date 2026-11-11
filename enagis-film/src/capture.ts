import manifest from "./capture-manifest.json";

export type CameraKey = {seconds: number; x: number; y: number; zoom: number};
export type CursorKey = {seconds: number; x: number; y: number; click?: boolean};
export type Capture = {
  id: string;
  src: string | null;
  states: {seconds: number; src: string}[];
  width: number;
  height: number;
  durationSeconds: number;
  satelliteVerified: boolean;
  reviewed: boolean;
  containsCursor: boolean;
  savedAnalysis: boolean;
  camera: CameraKey[];
  cursor: CursorKey[];
  notes: string;
};

export const captures = manifest.shots as Capture[];
export const captureFor = (id: string): Capture => {
  const capture = captures.find((shot) => shot.id === id);
  if (!capture) throw new Error(`Unknown film shot: ${id}`);
  return capture;
};

export const isReady = (shot: Capture) =>
  Boolean(shot.src && shot.states.length && shot.satelliteVerified && shot.reviewed);

export const missingShots = () => captures.filter((shot) => !isReady(shot));
