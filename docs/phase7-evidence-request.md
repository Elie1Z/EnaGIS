# Phase 7 evidence and participation requests

Status: **drafts prepared; neither sent nor accepted**. Prepared 8 October 2026;
handoff reviewed 9 October 2026.
No applicable operating report or committed verification participant has been supplied.
The existing code, protocol proposal and synthetic rehearsal remain available; these requests
address the real input and participation gap rather than create another implementation stage.

## Public contacts checked

| Organization | Public contact | Purpose of the request |
|---|---|---|
| Prairie Agricultural Machinery Institute (PAMI), Saskatchewan contact route | `pami@pami.ca` | Applicable commercial storage/aeration evidence and a technical or operator referral |
| Canadian Grain Commission, Statistics and Business Information | `statistics-statistique@grainscanada.gc.ca` | Appropriate historical inventory/turnover sources, their resolution and interpretation |

Sources checked on 8 October 2026: [PAMI contact page](https://pami.ca/contact/) and
[CGC research/data contacts](https://www.grainscanada.gc.ca/en/about-us/contact-us/research-data.html).
PAMI's [equipment-report catalogue](https://pami.ca/equipment-reports/) lists aeration fan
reports; a listed test does not establish installed equipment, current operating duty or
applicability to primary elevators. The CGC page identifies the statistics office's remit;
it does not promise site-level aeration records or participation.

The request footprint is Alberta/Saskatchewan. Manitoba remains the untouched evaluation region.
An organization's office location does not change the requested data footprint. No messages,
forms, purchases or service commitments have been made. These are public leads only.

## Draft 1 — PAMI

To: `pami@pami.ca`

Subject: Evidence request — wheat-storage aeration at AB/SK primary elevators

Hello PAMI team,

I am working on EnaGIS, an open, reproducible tool for prioritizing agricultural sites for
further energy assessment. Our first benchmark covers non-durum wheat storage and ambient-air
aeration at primary elevators in Alberta and Saskatchewan, using a retrospective 2024/25
data context.

Could you point us to an existing report or appropriate technical contact covering commercial
elevator storage classes, wheat inventory/turnover, and compatible fan operating conditions?
We need documented grain depth/test weight, airflow with its bushel or mass basis, total
static pressure at that airflow, fan/motor efficiency, simultaneous operation and cooling-cycle
conditions. Class-level evidence with clear applicability would also be useful.

We have reviewed general aeration guidance and want to check its applicability to these
commercial facilities. Could you also suggest an operator or specialist who might be willing
to discuss the method and help arrange a later, consented verification exercise? That sample
will be frozen before collecting verification responses.

A source link or referral would be a useful first step. Please identify any access, licensing
or confidentiality restrictions. This is an initial information request, with no paid work
being commissioned.

Thank you,
Elie — EnaGIS project

## Draft 2 — Canadian Grain Commission

To: `statistics-statistique@grainscanada.gc.ca`

Subject: Source guidance — AB/SK wheat inventory and turnover, 2024/25

Hello Statistics and Business Information team,

I am working on EnaGIS, an open research tool that screens agricultural locations for further
energy assessment. Our first benchmark is non-durum wheat storage and ambient-air aeration at
primary elevators in Alberta and Saskatchewan, in a retrospective 2024/25 context.

We are seeking guidance on existing sources for wheat inventory, storage occupancy and
turnover/residence time at primary elevators or at defensible facility-class or regional
resolution. We distinguish reported storage capacity from actual inventory and annual
deliveries, and retain shipping-point totals at their published aggregation level.

Could you identify any applicable public report, methodology, or office/operator contact?
Knowing the reporting period, geographic resolution, confidentiality constraints and limits
on deriving residence time would help us avoid unsupported assumptions. We are requesting
Alberta/Saskatchewan information only.

If another organization is better placed to advise on commercial aeration operations or
participation in a future consented verification exercise, a referral would be appreciated.
At this stage we are seeking source documentation and participation leads before freezing
our separate verification sample.

Thank you,
Elie — EnaGIS project

## How a reply advances the existing gates

1. Record source date, period, units, licensing and applicability in the existing
   [technical worksheet](../data/manual/phase6-site-evidence-template.json). Suitable class-level
   evidence may support an explicit model assumption; site-specific measurement is not required
   for every modeled parameter at all 261 candidates. Unsupported details remain UNKNOWN.
2. Review the model against that evidence. If the evidence requires storage-class parameters,
   nonlinear fan curves or a different inventory method, implement and test that declared method
   before real execution. Do not force evidence into the current global-coefficient contract.
3. Record a participant only after an actual commitment, privately, with their agreed role.
   A referral, source author, public email address or sent message is not a commitment.
4. Prepare exact sourced configuration and outcome criteria for human approval. The existing
   [Phase 6 policy proposal](../configs/scenarios/phase6-policy-proposal-v1.json) and
   [Phase 7 protocol proposal](../configs/verification/phase7-canada-v1.review.json) are still
   unapproved. A reply or permission to send these requests does not approve scientific values.
5. Complete the approved real run and prospective comparisons, record its scientific exit,
   then prepare/commit/tag/seal `ranking-v1` and its sample before collecting verification.
   Any site information learned beforehand is prior evidence and cannot be counted as fresh
   post-freeze validation. Record period differences explicitly.

The assistant can process supplied evidence, implement the reviewed method, execute and verify
the pipeline, and build the freeze. It cannot create a third party's commitment, invent missing
operating facts, or attribute human scientific approval to itself. These gates originate in
[AGENTS.md](../AGENTS.md), the [Phase 0 handoff](phase-0-completion.md) and PRD §9/§11.

Sending the above drafts requires explicit user authorization and an available sending account
or user-supplied contact channel. No sender email has been assumed. No recurring monitoring or
follow-up messaging has been scheduled.
