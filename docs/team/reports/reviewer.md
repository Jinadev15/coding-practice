# Reviewer report: C++ Modules 10–13

**Scope:** 16 topics, 126 problems, 185 MCQs (180 originally, plus 5 I added) and 16 lessons.
**Feedback:** one file per topic in `docs/team/feedback/`, plus `docs/team/feedback/GUIDELINES.md`.

## Verdicts

| Topic | Status | Main reason |
|---|---|---|
| cpp-complexity-cp | APPROVED | |
| cpp-dsa-recursion | APPROVED | |
| cpp-dsa-arrays-basics | APPROVED | ambiguous rotation wording fixed |
| cpp-dsa-sorting | APPROVED | weak trace-boundary tests fixed |
| cpp-arrays-two-pointers | APPROVED | |
| cpp-dsa-sliding-window | APPROVED | lesson `at_most(K<0)` out-of-bounds bug fixed |
| cpp-hashing-prefix | APPROVED | weak n=3 test in pivot-and-split fixed; duplicate MCQ rewritten |
| cpp-dsa-hashing | APPROVED | weak tests in nearby-almost-duplicate fixed |
| cpp-dsa-kadane-subarrays | APPROVED | weak tests in majority-vote fixed |
| cpp-dsa-intervals-sweep | APPROVED | lesson short (recommendation) |
| cpp-dsa-strings-basics | APPROVED | dry run added |
| cpp-binary-search | APPROVED | 3 weak test sets fixed |
| cpp-dsa-binary-search-answer | APPROVED | dry run added; lesson short (recommendation) |
| cpp-linked-trees | APPROVED | duplicate MCQ rewritten; dry run and pattern table added |
| cpp-dsa-doubly-circular | APPROVED | `DList` copy/double-free fixed; 2 MCQs added |
| cpp-dsa-list-reversal | **CHANGES NEEDED** | only 5 problems; needs 1–3 more (see feedback) |

## How I verified

1. **Lesson code.**
   - I compiled every C++ block.
   - I extracted every complete function and class (about 75) and checked them against brute forces on thousands of random inputs under ASan/UBSan. All pass now.
   - The only real bugs were `at_most(a, -1)` (out of bounds) and a copyable `DList` (double free).
2. **Problems.**
   - `validate.py` passed on all 126 problems.
   - **Mutation testing:** for each spec-built problem, I flipped one operator in the reference 10–24 times. I kept the mutants that are really wrong on 60 random inputs, and checked that the official tests reject them.
   - This found weak tests in 8 problems. I strengthened each one through its spec and rebuilt it (`ok`), and re-checked it (0 survivors): bs-rotated, bs-rotated-duplicates, bs-peaks-bitonic, hs-nearby-almost-duplicate, kd-majority-vote, insertion-sort-trace, merge-sort-trace and ps-pivot-and-split.
   - Four survivors were out-of-bounds UB mutants: skyline, the sorted-matrix k-th problem, xor-and-balance, and merge-sort's leftover copy. Those aren't test gaps. The judge doesn't run sanitizers.
3. **Statements.** I read all 121 spec statements, hints and hidden blocks. They are precise, with exact tie-breaks and good edge-case samples. I found no duplicates within a topic.
4. **MCQs.** I checked all of them.
   - **Systemic defect:** 146 of 164 answers were `B`, and the correct option was the longest in 132 of 164.
   - I rebalanced the answer letters for all 16 topics. I verified that every correct answer still maps to the same text, and remapped the one explanation that names letters.
   - I rewrote 2 duplicate questions (`cpp-hp-03`, `cpp-lt-01`).
   - I added 5 questions (`cpp-ddl-08`, `cpp-ddl-09`, `cpp-dlr-07..09`), so every topic now has at least 8.

## What the Head must do

- Commit the changes listed below. I ran no git commands.
- Give `cpp-dsa-list-reversal` back to an author for 1–3 extra problems and a longer lesson (`docs/team/feedback/cpp-dsa-list-reversal.md`).
- Give authors `docs/team/feedback/GUIDELINES.md` before new work. The MCQ letter and length bias, and the hand-written boundary hidden tests, are the two biggest recurring issues.
- Optional authoring backlog: expand the short lessons toward 1,800 words (intervals, binary search on the answer, doubly linked lists, hashing, strings). Add code and output MCQs: 85% are `theory`.

## Files changed

- **Lessons:**
  - `cpp-dsa-arrays-basics.md`
  - `cpp-arrays-two-pointers.md`
  - `cpp-dsa-sliding-window.md`
  - `cpp-dsa-sorting.md`
  - `cpp-binary-search.md`
  - `cpp-hashing-prefix.md` (dry run)
  - `cpp-dsa-strings-basics.md` (dry run)
  - `cpp-dsa-binary-search-answer.md` (dry run)
  - `cpp-linked-trees.md` (dry run and pattern table)
  - `cpp-dsa-doubly-circular.md` (dry run, pattern table and copy deletion)
- **MCQs:** `content/cpp/mcq/09-dsa.csv`, rows of these 16 topics only.
- **Specs and rebuilt problems:**
  - `cpp-binary-search/{3-rotated,4-rotdup,5-peak}`
  - `cpp-dsa-hashing/7-almostdup`
  - `cpp-dsa-kadane-subarrays/4-majority`
  - `cpp-dsa-sorting/{1-insertion,2-merge}`
  - `cpp-hashing-prefix/5-split`
- **Front matter:** `cpp-complexity-cp/cpp-overflow-stats.md` (order 1 changed to 7).
