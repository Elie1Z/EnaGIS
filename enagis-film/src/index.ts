import { getRemotionEnvironment, prefetch, registerRoot, staticFile } from "remotion";
import { RemotionRoot } from "./Root";
import {captures} from "./capture";
import v2Captures from "./v2/captures.json";

// Warm the local image cache during the opening, before the product walkthrough.
const imagePaths = new Set(captures.flatMap((shot) => shot.states.map((state) => state.src)));
for (const asset of Object.values(v2Captures.files)) imagePaths.add(asset.src);
// Studio benefits from eager preloading; the exporter already waits for each
// required image and should not load unused V1 footage into every render page.
if (!getRemotionEnvironment().isRendering) {
  for (const path of imagePaths) {
    prefetch(staticFile(path)).waitUntilDone().catch((error) => console.error("Image preload failed",path,error));
  }
}

registerRoot(RemotionRoot);
