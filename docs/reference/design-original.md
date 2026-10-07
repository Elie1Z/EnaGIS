# EnaGIS: The "Limitless" UX/UI Architecture Specification
**Deliverable:** UI/UX Master Plan & Component Blueprint
**Target Event:** OSEAS 2026, Kigali[cite: 1]

## 1. The Core Paradigm: The Decisive Lens
EnaGIS replaces the standard continuous energy map[cite: 1] with a high-contrast, zero-distraction environment optimized for immediate triage.

*   **The 2.5D Canvas:** A deep obsidian MapLibre basemap[cite: 1]. Administrative boundaries and roads are rendered as ultra-thin vectors. 
*   **The Empty Room Principle:** The interface loads with a stark, minimal view showing only the decisive top-10 shortlist[cite: 1]. Unnecessary layers are suppressed to force focus on the primary screening task[cite: 1].
*   **Topographic Isochrones:** Wet and dry travel scenarios[cite: 1] are rendered as animated contour lines rippling outward from candidate aggregation nodes[cite: 1], visually simulating terrain friction and impassable roads[cite: 1].

## 2. Volumetric Node Architecture
Traditional map pins are discarded. Aggregation nodes[cite: 1] are visualized as WebGL-rendered volumetric pillars, instantly communicating both scale and uncertainty.

*   **Height as Value:** Pillar height correlates directly to the energy gap and value-at-stake[cite: 1].
*   **Kinetic Tiers (Uncertainty Visualization)[cite: 1]:**
    *   **Robust:** Solid, illuminated hexagonal pillars with a stable visual signature (top-10 in most Monte Carlo draws)[cite: 1].
    *   **Contested:** Fractured geometric forms with a high-frequency visual pulse to signal data volatility[cite: 1].
    *   **Verify-First:** Holographic, dashed wireframe cylinders indicating unknown capacity[cite: 1].

## 3. The Evidence Barcode
Text-heavy legends are replaced by a 5-segment micro-component attached to every node, detailing exact data provenance[cite: 1].

*   **OBSERVED:** Solid cyan block (reported by a named source, with date and licence)[cite: 1].
*   **PREDICTED:** Glowing amber block (model output)[cite: 1].
*   **ESTIMATED:** Striped block (calculated from assumptions)[cite: 1].
*   **INFERRED:** Dual-tone split block (combined evidence)[cite: 1].
*   **UNKNOWN:** Empty/transparent block[cite: 1].
*   **Interaction:** Hovering expands the barcode into a tooltip revealing the precise source and validation data.

## 4. The Holographic Node Card
The node card acts as an executive dossier, projecting directly from the selected node via a glassmorphic overlay.

*   **The Single Question:** The single question required to resolve the node's uncertainty[cite: 1] is presented in high-contrast typography at the very top.
*   **Energy State Rings:** The three supply states (Undocumented supply, Undersized, Verify first)[cite: 1] are visualized as circular progress meters.
*   **Pre-Visit Checklist:** A clean, actionable checklist anchored at the bottom of the card for direct field deployment[cite: 1].
*   **Energy Context Axis:** Grid proximity and planned-extension flags[cite: 1] are displayed as secondary visual warning tags.

## 5. Prototyping & Technical Implementation
To maintain the strict requirement of no server and no framework web app[cite: 1], the cinematic UI is prototyped and pre-compiled.

*   **Prototyping:** High-fidelity interactive layouts and component states are designed in Figma.
*   **Styling:** Utility-based CSS (Tailwind) is used during development to quickly build the glassmorphic overlays, evidence barcodes, and typography hierarchy.
*   **Final Export:** The Tailwind classes are compiled down to a minimal, static CSS file. 
*   **Rendering:** The map relies strictly on MapLibre and plain GeoJSON for nodes and catchments[cite: 1], ensuring the final product remains a highly performant, one-command rebuild[cite: 1].

## 6. The OSEAS Defense Pitch Strategy
During the defense on October 26–27 in Kigali[cite: 1], the UI directly answers the judges' anticipated questions[cite: 1]:

*   **"So what?"[cite: 1]:** The immediate visual contrast between the glowing top-10 nodes[cite: 1] and the dark map instantly demonstrates the tool's triage capability.
*   **"How do you know?"[cite: 1]:** Hovering over any node's Evidence Barcode instantly surfaces the validation intervals and dataset manifests[cite: 1] on screen.
*   **"Why not QGIS?"[cite: 1]:** The fluid transitions between the Monte Carlo tiers[cite: 1] and the capacity-constrained allocation models[cite: 1] demonstrate a dynamic application that static QGIS dashboards cannot replicate.