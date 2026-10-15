# 0013: Overture Maps and WorldPop in EnaGIS Live

Status: **implemented**, 9 October 2026, after a live search of Gasabo District returned no ranking.

## Context

A real search of Gasabo District (434 km²) found 21 facilities but ranked none. The cause, reproduced in a
browser in Kigali:

- **Overpass timed out.** The public server answered the buildings and roads requests with HTTP 504.
- **Two mirrors failed.** They refused browser requests (CORS).

Without buildings there are no people, and without people there is no demand to rank. Rural Rwanda
also has a second problem: OpenStreetMap is missing most homes there. In one rural Gasabo map tile,
OpenStreetMap had 29 buildings and Google Open Buildings about 2,000.

## Decision

Read the heavy layers from Overture Maps instead of Overpass. Calibrate people per building to WorldPop.

| Layer | Source now | Fallback |
|---|---|---|
| Buildings | Overture buildings (OpenStreetMap, Google Open Buildings, Microsoft ML footprints, merged) | Overpass |
| Roads and paths | Overture transportation (from OpenStreetMap), pieces rejoined across tile edges | Overpass |
| Power lines, pylons, substations, generators | Overture base, infrastructure (from OpenStreetMap) | Overpass |
| Facilities and settlements | Overpass (a small query that public servers answer) | none |
| More facilities | Overture places (Meta, Microsoft), agricultural categories only, look-alikes filtered | none |
| Population | WorldPop 2020 (wpgppop), summed over the boundary by WorldPop's API | assumption range |
| Climate | Open-Meteo (unchanged) | assumption |

How it is read:

- **Tiles.** Overture is read as PMTiles over HTTP range requests, at zoom 14 (zoom 13 for power). Only tiles
  that touch the boundary are fetched.
- **Release.** The latest release comes from Overture's STAC catalog, with a pinned fallback.
- **Speed.** Four equivalent addresses of the same public bucket are used in parallel.
- **Cache.** Each tile's converted result is stored in the browser.
- **Calibration.** People per building is WorldPop population ÷ buildings in the boundary, with a ±20% range.
  The simulation samples that range.

## Evidence (live run, Gasabo, 9 Oct 2026, first search with an empty cache)

| Step | Result |
|---|---|
| Sources | WorldPop 889,650 people (census 2022: 879,505); 709 power features; 14 Overture agricultural places; 75 OSM places |
| Buildings | 484,286 footprints in 102 tiles, 338,902 inside the boundary (Google 53%, OSM 40%, Microsoft 6%) |
| Roads | 28,362 segments |
| Time | 74 s to gather, 1.7 s to analyze |
| Calibration | 2.6 people per building |
| Result | 29 candidate sites ranked; 8 of the top 10 Robust |

The test also exposed look-alikes, which are now filtered and covered by tests:

- a church named "Isoko …" (*isoko* also means "spring" in Kinyarwanda);
- stores filed under warehouse;
- a broadcaster tagged `man_made=works`;
- a tax office called "Collection Centre".

## Consequences

- **Ranking works without Overpass.** Buildings no longer depend on it, and rural homes come from
  satellite-detected footprints.
- **First searches download more.** A district can transfer tens of MB. Repeat searches use the cache, and
  "Save analysis" keeps a replayable copy for demos.
- **Footprints are years old.** They come from 2020–2023 imagery. The Map data lens shows each footprint's
  source.
- **New licences.** Overture places are CDLA-Permissive-2.0; WorldPop is CC BY 4.0. Both are listed in
  Sources and exports.
