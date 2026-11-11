import {loadFont} from "@remotion/fonts";
import {staticFile} from "remotion";

export const palette = {
  cream: "#F7F6F0",
  ink: "#032536",
  green: "#087A64",
  mint: "#00BD94",
  muted: "#677F83",
};

void Promise.all([
  loadFont({family: "Inter", url: staticFile("brand/inter.ttf"), weight: "100 900"}),
  loadFont({family: "Fraunces", url: staticFile("brand/fraunces.ttf"), weight: "100 900"}),
]);

export type SceneProps = {
  captions: boolean;
};
