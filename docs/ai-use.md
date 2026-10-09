# AI-use disclosure

**Code was written with AI assistance.** The PRD (§11) sets the protocol: "All code is written by
AI. Humans write specs, tests and decisions, review, and do data and outreach work."

| Done by AI coding assistants | Done or decided by humans |
|---|---|
| Writing code, tests and documentation drafts | Product scope, PRD, commodity and geography choice (decisions 0002–0003) |
| Running checks, builds and audits | Approval of protocols and their registration (Phase 4 v1.1) |
| Drafting proposals (e.g. `docs/proposals/`) | Accepting or rejecting proposals; scientific parameters and thresholds |
| | Outreach to data holders and field partners |

Safeguards that do not depend on trusting the AI:

- Repository rules in [AGENTS.md](../AGENTS.md): evidence labels, no silent defaults, units and
  CRS at interfaces, row-count checks, mass conservation.
- 230 Python tests and 6 JavaScript tests; CI on a clean runner.
- A preregistered protocol frozen at a Git tag before evaluation; a negative result was kept.
- Hash-pinned inputs and artifact verifiers (`verify-data`, `verify-run`, `verify-experiment`,
  `build_mvp --verify`).
- Scientific changes proposed by AI go to `docs/proposals/` for human approval.

**Known risk:** a team can ship AI-written code it does not understand. Mitigation:
[TEAM_GUIDE.md](TEAM_GUIDE.md) has a 10-minute explain-back per module. Judges may ask any team
member to explain any module.

This audit and documentation pass (9 October 2026) was carried out with Claude (Anthropic).
