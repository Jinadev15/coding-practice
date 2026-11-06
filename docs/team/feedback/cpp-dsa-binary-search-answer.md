STATUS: APPROVED

# cpp-dsa-binary-search-answer: review

## Checks run
- I tested `min_speed` against a linear search for the speed. All passed.
- `validate.py` passed on all 9 problems.
- Mutation testing: 67 of 68 wrong mutants were killed. The one survivor, in `cpp-bsa-sorted-matrix-kth`, changes `m[n-1][n-1]` to an out-of-row read. That is undefined behaviour that happened to pass, not a missing test.
- All 9 MCQs are correct.

## Issues found
1. The lesson had no dry run of the search. It was the shortest lesson in the module: 1,234 words.
2. The MCQ answer letters were biased: 9 of 9 were `B`. All 9 are `theory`.

## Fixed
- I added a full `lo | hi | k | hours | feasible | update` dry-run table for Koko on `[3,6,7,11]`, h = 8. I checked every row by hand: the answer is 4. The lesson is now 1,349 words.
- I rebalanced the answer letters.

## Remaining (recommended, not blocking)
- Add a worked example for "maximise the minimum" (aggressive cows) with its own trace, and a short section on picking `lo`/`hi` bounds. Target about 1,800 words.
- Add 2–3 code or output MCQs, for example "which update pair loops forever on lo = 4, hi = 5".
