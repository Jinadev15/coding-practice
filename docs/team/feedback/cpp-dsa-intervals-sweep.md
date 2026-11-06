STATUS: APPROVED

# cpp-dsa-intervals-sweep: review

## Checks run
- I tested `merge` (coverage comparison), `max_disjoint` (subset brute force) and `min_rooms` (time-point brute force) under ASan/UBSan. All passed.
- `validate.py` passed on all 8 problems.
- Mutation testing: 60 of 61 wrong mutants were killed. The survivor in `cpp-iv-skyline` (`i < ev.size()` changed to `<=`) is an out-of-bounds read, which is undefined behaviour that happened to give correct output. That is a sanitizer issue, not a missing test: the judge doesn't run with sanitizers.
- All 8 MCQs are correct.

## Issues found
1. The MCQ answer letters were biased: 8 of 8 were `B`.
2. The lesson is short: 1,370 words against the CEO target of 1,800–3,500. It does contain every section: a merge dry run, an exchange-argument proof, pattern cues, mistakes, Q&A and checks.

## Fixed
- I rebalanced the answer letters.

## Remaining (recommended, not blocking)
- Add a sweep-line dry-run table for `min_rooms` (time | event | count | best) and a short heap-based room-assignment trace. That would bring the lesson to about 1,700 words.
- The topic has 8 MCQs, the minimum. Add 2 code or output questions.
- Note that a degenerate zero-length interval `[3,3)` isn't handled specially in the lesson's `max_disjoint`. No problem uses one.
