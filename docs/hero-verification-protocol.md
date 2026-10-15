# Nyabihu hero verification protocol v1

Frozen on 10 October 2026 before any call. This is separate from the registered Phase 4R experiment.
Elie approved the activity-only success rule in the task conversation on 10 October 2026.
The accompanying SHA-256 identifies these exact bytes. Protocol creation time and hash are also
stored in `data/rwanda/hero/verification-protocol.json`; a completed log entry must postdate that time.

## Target and sample

The frozen snapshot's dry-season top 10 and look-alikes ?1–?5 form the call and desk-check list.
Site IDs and EPSG:4326 longitude/latitude are retained. A look-alike is a predicted cell, not a
documented facility; the caller must establish the exact site. Report attempts, completed calls,
confirmed, rejected and inconclusive separately, with the full denominator and all misses.
This convenience sample does not estimate district-wide recall or population prevalence.

## Single question and success rule

“At this exact location, did your organisation aggregate or store potatoes during the most recent
completed potato season, and how many tonnes did it handle in that season?”

CONFIRMED_ACTIVITY requires consent, a respondent with direct operational knowledge, the exact
site established, potato aggregation or storage reported for the most recent completed season,
and positive reported volume **greater than 0 tonnes**. Record the named season and original
quantity/unit; do not turn bags into tonnes without a reported bag mass. This is the threshold
Elie approved. It establishes reported activity only: not a cold room, energy demand, capacity,
commercial viability, power supply, or metered consumption.

REJECTED_ACTIVITY requires a knowledgeable respondent to explicitly report no potato aggregation
or storage at the exact site in that season, or explicitly report zero tonnes. An unknown volume,
uncertain location, uncertain knowledge, refusal or incomplete answer is INCONCLUSIVE. A wrong
number/no answer is an ATTEMPT, not a completed check or a rejection. Missing documentation does
not establish absence. Repeat calls do not increase the distinct-site denominator.

## Script — English

Hello. My name is [name], from Team Dynamis working on an agricultural energy screening study.
We are checking a map lead, not offering funding or promising equipment. May I ask one question
and record a brief, anonymised answer? Are you directly familiar with operations at [site name,
location]? [Ask the single question above.] Which season does that refer to? Thank you. Your
answer may show our map is wrong; that is useful too. We will keep personal details private.

## Script — Kinyarwanda (draft for Elie to review before use)

Muraho. Nitwa [izina], ndi mu itsinda Dynamis rikora ubushakashatsi ku mikoreshereze y'ingufu mu
buhinzi. Turagenzura amakuru ari ku ikarita; ntabwo dusezeranya inkunga cyangwa ibikoresho.
Mwatwemerera kubabaza ikibazo kimwe no kwandika igisubizo tutagaragaje amazina yanyu?
Muzi neza ibikorwa bikorerwa kuri [izina ry'ahantu, aho riherereye]?
Mu gihembwe giheruka kurangira, kuri aha hantu mwakusanyije cyangwa mwabitse ibirayi?
Byari toni zingahe muri icyo gihembwe? Ni ikihe gihembwe muvuga? Murakoze.

Translation is a draft, not a certified translation. Elie owns local phrasing and consent delivery.

## Desk check — Elie and a teammate

Open the imagery URL for each frozen target. Record reviewer alias, UTC observation time, imagery
provider/date (UNKNOWN if absent), building present (yes/no/unclear), approximate roof area m²
(blank if unknown), road access, visible power line and plausible collection/storage site
(yes/no/unclear). Record a short non-personal note. Do not infer refrigeration or grid connection
from a roof or a line. No image is downloaded by the form. A completed record earns DESK-CHECKED
even when the answer is no or unclear; report that answer. It is **not field validation**.

## Privacy, integrity and reporting

`data/rwanda/hero/desk-check.csv` and `phone-log.csv` start as empty schemas. Only non-personal
reviewer aliases and anonymised outcomes belong in a shareable copy. Phone numbers, respondent
identities, recordings and raw notes stay under ignored `data/validation_private/hero/`.
Do not commit local observations without privacy review. Browser forms keep local entries and
export CSV for review; they do not send data to a server or contact anyone.

Each phone row records the protocol SHA-256, observation time, attempt/completed status, consent,
direct knowledge, exact-site match, named completed season, potato activity, tonnes and outcome.
The verification checker rejects pre-protocol timestamps, a wrong hash and inconsistent outcomes.
Do not backdate records. Freeze a new version before changing a success criterion after calls.

Initial status: desk checks 0; phone attempts 0; completed calls 0; confirmed activity 0;
field visits 0. These are workflow counts, not scientific validation results.
