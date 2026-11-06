# Author A report: Module 13 Linked Lists

All problems were built with `tools/build_problem.py`, and every build printed `ok`. Each build stress-tests the reference against a brute force on 300 random inputs, runs ASan/UBSan, checks the time limit, and confirms the starter fails. Each problem was then judged one at a time with `JUDGE_WORKERS=2`:

- **Registered topics** (`cpp-dsa-fast-slow`, `cpp-dsa-list-reversal`): `validate.py` reports no issue for them.
- **Unregistered topics:** `validate.py` skips their problems, so I judged them through `validate.check_problem`, using a scratch script that calls `load_problem` directly. All OK.

Every lesson code block was compiled. Complete functions were stress-tested against brute forces under ASan/UBSan. MCQ answer letters are balanced per topic.

## Topics delivered

### cpp-dsa-fast-slow (already in curriculum.csv)
- **Lesson:** `content/cpp/lessons/cpp-dsa-fast-slow.md`, about 3,150 words. It covers the middle node, Floyd's algorithm with the entry proof and a dry-run table, cycle length, intersection, the palindrome check with restore, functional graphs (happy numbers, find the duplicate) and Brent's algorithm.
- **Problems (7):**
  - `cpp-fs-middle` (E)
  - `cpp-fs-intersection` (E)
  - `cpp-fs-cycle` (M)
  - `cpp-fs-palindrome` (M; the driver checks the list is restored)
  - `cpp-fs-find-duplicate` (M)
  - `cpp-fs-circular-loops` (H)
  - `cpp-fs-rho-brent` (H)
- **MCQs:** 13 in `content/cpp/mcq/t-cpp-dsa-fast-slow.csv` (`cpp-fsp-01..13`). Answers are 4 A, 3 B, 3 C, 3 D.
- **Request:** `docs/team/requests/curriculum-cpp-dsa-fast-slow.tsv`.

### cpp-dsa-list-merge (NOT yet in curriculum.csv)
- **Lesson:** `content/cpp/lessons/cpp-dsa-list-merge.md`, about 2,700 words. It covers dummy + tail, the stable merge with a dry run, merging k lists (heap and tournament), bottom-up merge sort with a dry run, partition and reorder, adding two numbers in LSD and MSD order, deep copy with random pointers, and an ownership table.
- **Problems (7):**
  - `cpp-lm-merge-two` (E)
  - `cpp-lm-merge-unique` (E)
  - `cpp-lm-add-two` (M; both digit orders, inputs must stay unchanged)
  - `cpp-lm-reorder` (M)
  - `cpp-lm-copy-random` (M)
  - `cpp-lm-sort-list` (M)
  - `cpp-lm-merge-k` (H)
- **MCQs:** 12 in `t-cpp-dsa-list-merge.csv` (`cpp-lmg-01..12`), 3 per letter.
- **Request:** `docs/team/requests/curriculum-cpp-dsa-list-merge.tsv` (`# after: cpp-dsa-fast-slow`).

### cpp-dsa-skip-list (NOT yet in curriculum.csv)
- **Lesson:** `content/cpp/lessons/cpp-dsa-skip-list.md`, about 3,150 words. It covers skip lists (with a search dry-run table and the expected O(log n) argument), indexable skip lists, unrolled lists, intrusive `list_head`/`container_of`, pools with free lists, XOR lists, and LRU vs LFU.
- **Problems (7):**
  - `cpp-sk-array-pool` (E)
  - `cpp-sk-intrusive-scheduler` (M)
  - `cpp-sk-xor-list` (M; reverse must be O(1))
  - `cpp-sk-unrolled-list` (M)
  - `cpp-sk-skip-list` (H; seeded xorshift RNG provided in the starter)
  - `cpp-sk-lfu-cache` (H)
  - `cpp-sk-indexable-skip-list` (H)
- **MCQs:** 12 in `t-cpp-dsa-skip-list.csv` (`cpp-skl-01..12`), 3 per letter.
- **Request:** `docs/team/requests/curriculum-cpp-dsa-skip-list.tsv` (`# after: cpp-dsa-list-merge`, level Advanced).

### cpp-dsa-list-reversal (extra task, Reviewer feedback)
- **Problems (3 new):**
  - `cpp-lr-double-number` (order 6)
  - `cpp-lr-zero-segments` (order 7)
  - `cpp-lr-odd-then-reversed-even` (order 8)

  The topic now has 8 problems. "Add two numbers MSD-first" was **not** added here, because it already exists as `cpp-lm-add-two` in `cpp-dsa-list-merge`.
- **Lesson:** extended from 1,176 to about 2,100 words. New material:
  - a head-insertion dry-run table for `reverse_between`
  - a recursive k-group aside with its stack cost
  - a section on reversal as a tool (carries, segments, head insertion)
  - a pattern-recognition table
  - two more check questions
- **MCQs:** 4 new in `content/cpp/mcq/t-cpp-dsa-list-reversal.csv` (`cpp-dlr-10..13`). The topic now has 13.
- **Note:** `docs/team/requests/author-A-cpp-dsa-list-reversal.md`.

## What the Head must do
1. Apply the two curriculum requests, list-merge and then skip-list. Until then, `validate.py` reports "unknown topic" for their problems and MCQs, and it does not judge them.
2. Ask the Reviewer to re-review `cpp-dsa-list-reversal`.

## Notes and known limits
- **Smaller big tests.** Some tests are smaller than 10⁶, so the reference stays under 30% of the time limit:
  - `cpp-lm-sort-list`: n ≤ 2·10⁵, because pointer chasing on scattered nodes is slow.
  - `cpp-lm-merge-k`: N ≤ 3·10⁵.
  - `cpp-lm-add-two`: p, q ≤ 5·10⁵.
- **O(1)-space requirements are stated but not enforced.** This applies to palindrome, intersection, cycle, copy-random and sort-list: an O(n)-memory solution passes, because the judge has no memory limit. Drivers do enforce relinking (node identity), restoring the input, and no new or shared nodes, wherever the statement asks for it.
- **Possible overlap.** `cpp-lr-odd-then-reversed-even` is close to `cpp-ll-odd-even-partition` (linked-trees). The difference is that the even nodes must come out reversed in one pass by head insertion, which is the reversal idea it trains.
- **Problem file format.** The `.md` loader takes the first ```cpp fence after `## Solution` as the reference solution. A spec's `=== explanation` section must therefore not contain ```cpp blocks. I hit this once and fixed it.
