# Planner report (Agent 1)

Plans written:

- `docs/team/plan/cpp.md`
- `docs/team/plan/python.md`
- `docs/team/plan/c.md`

Every topic uses the playbook format: a header with its status, a summary, what the lesson must cover, and problems ordered Easy→Hard, one idea per problem. I made no git changes and edited no files outside the plan and report files.

## Counts

| Language | Modules | Topics | existing-ok | existing-thin | rebuild | new | Planned new problems |
|---|---|---|---|---|---|---|---|
| C++ | 33 | 211 | 16 | 72 | 5 | 118 | ~992 (240 thin top-ups, 45 rebuild, 706 new, 1 optional) |
| Python | 27 | 226 | 32 (27 DSA + 5 that already have ≥4 problems) | 108 | 0 | 86 | 748 (349 thin top-ups, 399 new) |
| C | 16 | 91 | 0 | 74 | 0 | 17 | 283 (214 thin top-ups, 69 new) |

**Total: about 2,020 planned problems.**

How the counts work:

- **Thin top-ups.** A script checked that every existing-thin topic ends with 4–6 problems in total (existing plus added). The added problems are listed in the plan.
- **DSA topics** get 6–10 problems.
- **C++ rebuilds:** cpp-stacks-queues, cpp-graphs, cpp-advanced-ds (segment trees), cpp-greedy-math and cpp-dp. Each one is narrowed to one focused topic. Its old suite problem stays as the last, mixed-review problem.
- **Wave 1 topics** that are already assigned (fast-slow, list-merge, skip-list, Module 14, Module 15 part 1, Module 16 part 1) are planned in full, so authors can check their sets against the plan.

## Recommended build order

**C++**

1. Finish the DSA modules in order: Module 13 (the rest) → 14 → 15 → 16 → 17 → 18 → 19 (11 DP topics) → 20 → 21.
2. Robotics (22).
3. OOP, all 23 GoF patterns and the low-level design (LLD) case studies (23–24).
4. Language-core top-ups for Modules 01–09. These have no dependencies, so one author can run them in parallel with anything above.
5. Concurrency extras and performance (26), then systems/networking (27).
6. Engineering computing (28) and geometry/CAD (29), then graphics/games (30).
7. Embedded (31), tooling/libraries (25), interop (32) and interview theory (33).

**Python**

1. Foundations top-ups for Modules 01–12. Most topics need only +2 problems, so this is cheap and high value.
2. Web/backend (17), in order: HTTP → Flask → FastAPI → SQL → SQLAlchemy → auth/security → Django → real-time/caching → API testing → deployment → projects.
3. Scientific stack (19) → ML (20) → deep learning (21) → NLP/CV (22) → ML engineering (23) → LLM apps (24).
4. Engineering computing (25).
5. OOP, patterns and LLD (14–15).
6. Data engineering and automation (18), tooling (16), system design (27), robotics (26).

**C**

1. Pointers and memory (04–05).
2. Foundations, functions, arrays and strings (01–03).
3. Data structures and algorithms (09–10).
4. Systems programming (12).
5. Embedded (13).
6. Everything else.

## Things the Head must do

1. **Relabel modules in `curriculum.csv`.** The old C++ labels "10 DSA in C++", "11 Libraries and Frameworks", "12 Design Patterns", "13 Interview Theory" and "14 Master OOP" clash with the new DSA modules 10–21. The proposed new numbers are in the module map at the top of `cpp.md`.
2. **Retitle the rebuilt topics** when their curriculum requests come in. Proposed titles:
   - "Stacks: Implementation and Classic Uses"
   - "Graph Representation, BFS and DFS"
   - "Segment Trees"
   - "Greedy Algorithms and Proofs"
   - "DP Foundations: 1D DP"
3. **Fix the problem count for cpp-dsa-list-reversal (marked done).** It has 5 problems, one below the DSA band. The plan suggests an optional sixth problem.
4. **Settle two Python judge gaps.**
   - **matplotlib** is not in the judge list you gave me. The plan assumes it is installed and that problems inspect Figure/Axes objects with the Agg backend. Please confirm it is in `.venv-judge`.
   - **pint, hypothesis, alembic, celery, redis and DRF** are not available. The plan teaches each concept and has the learner build a small version by hand.
5. **Python web problems must run in-process.** They use TestClient, `test_client()`, the Django test Client, `httpx.MockTransport` or `socketpair()`. Django problems need settings configured inside the file, with an in-memory SQLite database. Tell authors this when you assign the work.
