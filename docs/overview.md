# Overview

## The decision EnaGIS supports

A productive-use-energy team has budget for about ten site visits. It needs to know which
agricultural aggregation points to phone and visit first, and how much to trust that order.
EnaGIS is **stage 1 of a funnel**: screen (EnaGIS) → phone check → site visit and business case.
Source: [PRD §1–2](reference/prd-2026-10-04.md).

## What it does

1. **Registry.** Loads documented facilities from open sources, keeping source, date, licence,
   location precision class and capacity as stated. Pilot: 340 Prairie primary elevators, 261 in
   the Alberta/Saskatchewan development area (AAFC 2024).
2. **Production and assignment.** Assigns reporting-region wheat production (Statistics Canada
   2024) to the elevators in that region, conserving tonnes and exposing unserved tonnes.
3. **Energy requirement.** Converts assigned tonnes to stored tonnes, aeration airflow and fan
   electrical power with a physics formula ([method](method.md)).
4. **Supply and gap.** Compares the requirement with *documented* electrical capacity. Pilot: none
   documented, so the gap is UNKNOWN everywhere.
5. **Shortlist.** Ranks sites, attaches evidence and a pre-visit question, and exports CSV/GeoJSON
   and a printable one-page brief.
6. **Siting experiment (the ML part).** A preregistered, spatially held-out presence-only model
   tested whether road-accessible production predicts where facilities are documented. It lost
   to the production-only baseline (KILL).

## What you see

An offline map application (`app/index.html`) with four lenses: **Where first** (top 10),
**How sure** (evidence and the registered comparison), **How to get there** (coordinates and
pre-visit checklist) and **How it works** (method steps). Search works worldwide. Outside the
pilot, EnaGIS shows UNKNOWN and the evidence needed, rather than inventing numbers.

| Where first | How sure | Outside the pilot |
|---|---|---|
| ![](screenshots/1-where-first.png) | ![](screenshots/2-how-sure.png) | ![](screenshots/3-kigali.png) |

## What it is not

Not a feasibility study, not proof of bankable demand or willingness to pay, not a continuous
energy map, and not validated in the field yet. See [limitations](limitations.md).

## Who built it and how

A small hackathon team with AI-written code under human specifications, tests and review. See
[ai-use.md](ai-use.md) and the [project history](project-history.md).
