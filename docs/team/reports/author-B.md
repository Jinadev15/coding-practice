# Author B report: C++ Module 14 "Stacks, Queues and Heaps"

All four topics are done: lesson, problems, MCQs and curriculum request. I made no git changes.

## Topics

| Topic | Lesson (words) | Problems | MCQs (new file) |
|---|---|---|---|
| cpp-stacks-queues (rebuilt as "Stacks from Scratch") | ~3000 | 9 new + legacy suite | 10 in `t-cpp-stacks-queues.csv` (+3 legacy in `09-dsa.csv` = 13) |
| cpp-dsa-monotonic-stack | ~2500 | 8 | 11 |
| cpp-dsa-queues-deques | ~2500 | 9 | 11 |
| cpp-dsa-heaps | ~2400 | 9 | 12 |

### Problem ids (Easy to Hard, in `order:`)

- **cpp-stacks-queues:** cpp-st-array-stack, cpp-st-balanced, cpp-st-min-stack, cpp-st-rpn, cpp-st-shunting-yard, cpp-st-calculator, cpp-st-decode-string, cpp-st-undo-editor, cpp-st-iterative-dfs. The legacy `cpp-monotonic-suite` stays in place, with `order: 10` (I edited only its front matter).
- **cpp-dsa-monotonic-stack:** cpp-ms-next-greater, cpp-ms-stock-spanner, cpp-ms-histogram, cpp-ms-maximal-rectangle, cpp-ms-trap-rain, cpp-ms-sum-subarray-mins, cpp-ms-greedy-stack, cpp-ms-132-pattern.
- **cpp-dsa-queues-deques:** cpp-qd-circular-queue, cpp-qd-two-stack-queue, cpp-qd-ring-deque, cpp-qd-multi-source-bfs, cpp-qd-window-max, cpp-qd-longest-limit, cpp-qd-constrained-subseq, cpp-qd-shortest-sum-k, cpp-qd-round-robin.
- **cpp-dsa-heaps:** cpp-hp-binary-heap, cpp-hp-kth-largest-stream, cpp-hp-top-k-frequent, cpp-hp-kway-merge, cpp-hp-running-median, cpp-hp-sjf-cpu, cpp-hp-cooldown-scheduler, cpp-hp-ipo, cpp-hp-indexed-pq.

The specs are in `.authoring/cpp/<topic>/N-name.spec`.

## Verification

- **Builds:** every spec printed `ok` from `tools/build_problem.py`. Each was stress-tested against its brute force, ran under ASan/UBSan, and its starter fails.
- **Validation:** every problem passed `check_problem` from `tools/validate.py`. The heaps were checked with `JUDGE_WORKERS=2 JUDGE_WAIT=100000 python3 tools/validate.py cpp <id>`, one at a time. That run shows no `[problem]` errors.
  - The only remaining issues are `[content]` lines saying "unknown topic 'cpp-dsa-heaps'" (9 problems and 12 MCQs). They go away once the heaps curriculum request is applied.
  - Other authors' new topics, such as `cpp-dsa-cycles-bipartite`, also show up in those lines.
- **Lesson code:** every C++ block in all four lessons compiles under `-fsanitize=address,undefined` and runs with the output stated in its comments.
- **MCQs:**
  - Answer letters are balanced in every topic, per GUIDELINES.md.
  - Distractor lengths were evened out so the correct option is mostly not the longest.
  - Each topic has at least 3 code/output questions and at least 1 complexity question.
  - Duplicates removed: my "pop() returns void" question duplicated legacy `cpp-sq-01`, and the "min-heap declaration" question duplicated `cpp-sq-02`. I dropped the first and replaced the second.

## For the Head

1. **Curriculum:** `docs/team/requests/curriculum-cpp-dsa-heaps.tsv` still needs applying (`# after: cpp-dsa-queues-deques`). The other three requests already appear in `content/cpp/curriculum.csv`.
2. **Legacy MCQs:** `content/cpp/mcq/09-dsa.csv` still holds 3 legacy questions for `cpp-stacks-queues` (`cpp-sq-01..03`). I didn't touch them.
   - `cpp-sq-02` (min-heap declaration) and `cpp-sq-03` (deque DP) are really heap and deque questions.
   - Consider moving them to `cpp-dsa-heaps` and `cpp-dsa-queues-deques`.
3. **Time limits:** `cpp-ms-next-greater`, `cpp-ms-maximal-rectangle`, `cpp-qd-window-max`, `cpp-hp-kway-merge` and `cpp-st-iterative-dfs` use `time_limit: 2`. Their 10⁶-number I/O plus cache-unfriendly access was close to the 30% margin at 1 s.
4. **Stack depth:** `cpp-st-iterative-dfs` depends on the default 8 MB stack. Its starter is the correct recursive DFS, and it fails by overflowing the stack on a path-like tree about 10⁶ deep. If the judge ever raises the stack limit, the starter would pass.
