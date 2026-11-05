# CEO brief: project objective and quality bar

**Owner:** Jinadev (the learner). **CEO:** the orchestrating session. This document is the source of truth for *what* we build and *why*.

## Objective

Turn Coding Practice into a complete learning system that takes Jinadev from zero to an advanced, industry-ready level in **C++, Python and C**, broad enough to work in **any field**:

- software products and web/backend services
- mechanical, civil and electrical engineering software (simulation, CAD/geometry, numerical methods)
- data, AI and ML
- systems, embedded, graphics and games, robotics
- interview preparation for top companies

**Quality matters more than speed.** Every topic must teach completely, and every problem must make him a better engineer.

## Priorities (in order)

1. **C++:** complete DSA from zero (every pattern, idea and pathway), robotics, OOP, systems/performance, engineering computing, graphics, networking.
2. **Python:** everything *except* expanding the DSA module, which stays as it is. That means advanced Python, OOP, web/backend, data/AI/ML, scientific and engineering computing, automation, software engineering.
3. **C:** fill gaps so the C track covers the whole language and its systems/embedded uses. Existing content stays, and thin topics get more problems.

## Non-negotiable quality bar

- **Lessons** (`content/<lang>/lessons/<topic>.md`) are written for someone who has never seen the topic. They cover:
  - why the topic matters
  - intuition and pictures (ASCII or mermaid)
  - a step-by-step dry run
  - complete, correct code
  - complexity and its proof idea
  - pattern recognition cues
  - common mistakes
  - interview/exam Q&A
  - "Check your understanding" with answers in `<details>`

  Typically 1800–3500 words. Every code sample must compile or run as written.
- **Problems:**
  - **Counts:** DSA topics get **6–10**, other topics **4–6**.
  - **Variety:** each one teaches a *different* pattern or idea, ordered Easy → Hard. No near-duplicates.
  - **Built and verified with `tools/build_problem.py`:** the reference is stress-tested against a brute force, C/C++ references run under sanitizers, time limits are checked, and big tests are generated (never embedded).
  - **Statements** are precise (exact I/O format, constraints, tie-breaks). They give 3 teaching hints and a solution explanation with complexity.
- **MCQs:** 8–14 per topic: theory, code reading, output prediction, complexity. Explanations teach.
- **No broken builds.** `python3 tools/validate.py <lang>` must report `OK` before any commit.

## Definition of done for a topic

- The lesson is written to the bar above.
- The problems are built with `build_problem.py` (all `ok`).
- The MCQs are added.
- A curriculum request has been filed.
- The Reviewer has signed it off in `docs/team/feedback/`.
