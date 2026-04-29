# Open Source Evaluation — LifeLine-ICT

**Repository:** `bos-com/LifeLine-ICT`
**Snapshot date:** 29 April 2026
**Author:** Coursework submission

This file is one of four sibling reports — each in its own repository — that together evaluate the four flagship Bugema Open Source Community (BOSC) projects against open source principles. The companion files live in `bos-com/GreenCode`, `bos-com/OpenCare-Core`, and `bos-com/BOS`. Every claim below is grounded in publicly verifiable evidence from this repository, the BOSC organisation profile, and the `bos-com/bosc-governance` repository, captured on the snapshot date above.

## 1. Evaluation framework

Six principles are applied (drawn from the OSI Open Source Definition, GitHub's Open Source Guides, and CHAOSS community-health metrics):

1. **Recognised licence at root.**
2. **README covers purpose, scope, and setup.**
3. **Explicit project-level governance** (CONTRIBUTING, CODE_OF_CONDUCT, GOVERNANCE).
4. **Inclusive contribution workflow** (issue/PR templates, labels, "good first issue").
5. **Active maintenance and review velocity.**
6. **Code of conduct + security policy at repo level.**

Each principle is graded **Met / Partial / Not met / Unknown**.

## 2. Project profile

LifeLine-ICT has the most explicitly social-impact-oriented description of any BOSC flagship project. The GitHub API returns: "ICT-Driven Disaster Preparedness & Early Warning project by the Bugema Open Source Community (BOSC). We build open-source tools to protect communities from climate risks like floods and droughts, using real-time alerts, sensor-based monitoring, GIS mapping, and community dissemination." The README and the committed `plan.md` describe a layered architecture combining FastAPI backends (Python 3.11+), ESP32-based IoT sensor nodes (Flask logging), SQLAlchemy/Alembic on SQLite, pytest for tests, and (planned) GIS analytics and dashboards. The repository's language breakdown is "98.6% Python, 1.4% other."

The project was created on 20 August 2025. **The most recent push, however, was 13 November 2025 — over five months before the snapshot.** GitHub-side metrics: **38 forks, 1 star, 75 open issues, 41 open and only 2 closed pull requests**. Combined with the absence of recent commits, those numbers paint a picture: the project attracted contributor effort early, then stalled.

## 3. Licensing — the critical finding

**LifeLine-ICT does not ship a `LICENSE` file at the repository root.** This was confirmed by listing the root via the GitHub Contents API: only `README.md`, `plan.md`, and the `.github/`, `backend/`, `docs/`, and `iot/` directories are present. The GitHub REST API correspondingly returns no licence object for this repository.

This is the **single most material finding** in the evaluation of the four BOSC flagship projects. Under default copyright law, source code published without a licence is "all rights reserved": the public can view it but cannot legally copy, modify, or redistribute it. By the OSI's Open Source Definition, **LifeLine-ICT is therefore not currently open source**, regardless of how publicly it is hosted or how prominently BOSC features it on its organisation page. The README does mention "MIT" and "Apache" in passing, but a textual mention is not a licence grant — the repository needs a committed `LICENSE` file with the actual licence text.

**Principle 1: Not met.**

## 4. Governance and community files

The repository contains no `CONTRIBUTING.md`, no `CODE_OF_CONDUCT.md`, and no `SECURITY.md`. The `.github/` folder appears to host workflow definitions rather than community-health files. As with every other BOSC flagship project, the BOSC-wide governance documents in `bos-com/bosc-governance` are not linked from the project README.

**Principle 3: Not met. Principle 6: Not met.**

## 5. Contribution workflow

The contribution data is striking: **41 open pull requests against 2 closed.** Combined with the fact that the most recent push was 13 November 2025 — more than five months before the snapshot — this points to a project where review and merge activity has effectively stopped. This is the classic signature of a project that has lost its active maintainer.

For contributors, the consequence is concrete: PRs sit unreviewed, issues sit untouched, and effort is wasted. For the BOSC community, the consequence is reputational: a flagship project that no longer responds to contributors is a stronger negative signal than one that was never started, because the gap between aspiration and follow-through is visible.

**Principle 2: Met** — the README and `plan.md` together describe purpose, architecture, and tech stack adequately. **Principle 4: Not met** — the workflow is open in the sense that anyone can submit, but submissions do not progress. **Principle 5: Not met** — five months without a push, against an open-to-closed PR ratio of ~20:1.

## 6. Verdict and recommendations

| Principle | Verdict |
|---|---|
| 1. Recognised licence at root | **Not met** |
| 2. README covers purpose, scope, setup | **Met** |
| 3. Explicit project-level governance | **Not met** |
| 4. Inclusive contribution workflow | **Not met** |
| 5. Active maintenance and review velocity | **Not met** |
| 6. Code of conduct + security policy | **Not met** |

**Three concrete next actions, in strict priority order:**

1. **Add a `LICENSE` file.** This is the highest-leverage single change in the entire BOSC portfolio. The README mentions both MIT and Apache; the maintainers should choose one (consistency with the rest of the org points to MIT) and commit the licence text. Until this is done, the repository is not legally open source.
2. **Decide the project's status and say so in the README.** Either appoint a maintainer with merge rights and resume reviewing PRs, or mark the project explicitly paused and tell prospective contributors not to invest effort. Either choice is better than the current ambiguity.
3. **If active development resumes, triage the existing 75 open issues and 41 open PRs.** Closing what is stale and labelling what is live is the only way to recover a workable contribution flow from the current state.

LifeLine-ICT has the most compelling mission of any project evaluated here — disaster preparedness in a region where floods and droughts cost lives. The mismatch between that mission and the current state of the repository (no licence, stalled review pipeline, dozens of unreviewed PRs) is the most actionable finding in the entire BOSC portfolio.

## 7. Sources

- GitHub REST API: `/repos/bos-com/LifeLine-ICT`, `/repos/bos-com/LifeLine-ICT/contents/`.
- GitHub web pages: `README.md`, `plan.md`, `/issues`, `/pulls`.
- BOSC governance: `https://github.com/bos-com/bosc-governance`.
- Framework: OSI *Open Source Definition*; GitHub *Open Source Guides*; CHAOSS community-health metrics.

Counts and timestamps are accurate as of 29 April 2026 and will drift as the project develops.
