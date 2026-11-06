STATUS: APPROVED

# cpp-dsa-hashing: review

## Checks run
- I tested `two_sum` and `longest_consecutive` against a brute force. The `SplitMix` hash compiles for both `long long` and `pair<int,int>` keys.
- `validate.py` passed on all 8 problems.
- Mutation testing: before my fix, the tests killed 47 of 50 wrong mutants.
- All 11 MCQs are correct.

## Issues found
1. **Weak tests in `cpp-hs-nearby-almost-duplicate`.** Three wrong mutants passed every official test:
   - one that removed the left-neighbour bucket check (`near(id - 1)` became `near(id)`)
   - one that used `id + 2` instead of `id + 1`
   - one that broke floor division for negative values

   The neighbour-bucket logic is the whole point of the problem, and nothing tested it.
2. The MCQ answer letters were biased: 11 of 11 were `B`. All 11 questions are `theory`, with no code or output questions.
3. `cpp-hs-08` (anti-hash) repeats `cpp-hp-04` in `cpp-hashing-prefix`.

## Fixed
- I added a hidden block to `.authoring/cpp/cpp-dsa-hashing/7-almostdup.spec`. It covers left and right neighbour buckets with positive and negative values, equal negative values with t = 0, and the three failing random inputs.
- I rebuilt the problem: it printed `ok`, and `validate.py` passed.
- I rebalanced the answer letters.

## Remaining
- Recommended: replace 2–3 theory MCQs with code or output questions (trace `longest_consecutive` on a small set, find the `operator[]` bug in a snippet).
