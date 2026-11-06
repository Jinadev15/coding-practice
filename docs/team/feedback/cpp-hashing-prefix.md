STATUS: APPROVED

# cpp-hashing-prefix: review

## Checks run
- I tested `count_sum_k` and `longest_balanced` against a brute force on 3,000 random inputs under ASan/UBSan. All passed.
- `validate.py` passed on all 8 problems.
- Mutation testing: 52 of 54 wrong mutants were killed. See issues 1 and 2 for the two survivors.
- All 11 MCQs are correct.

## Issues found
1. **Weak test in `cpp-ps-pivot-and-split`.** Changing `n < 3` to `n <= 3` passed, because no test had n = 3 with a valid three-way split.
2. In `cpp-ps-xor-and-balance`, a mutant that shrinks the `seen` array to `2n` survived. That is an out-of-bounds write (UB) when the prefix reaches +n. The judge doesn't run sanitizers, so it isn't a test gap. No action needed.
3. **Duplicate MCQs.** `cpp-hp-03` (−7 % 3) repeated `cpp-pfx-07` (−8 % 3). `cpp-hp-01` and `cpp-hp-04` repeat `cpp-dsa-hashing` ideas.
4. The lesson had no dry run of the prefix-plus-hash-map counter. It was 1,387 words.
5. The MCQ answer letters were biased: 10 of 11 were `B`.

## Fixed
- I added n = 3 and n = 4 cases (`-2 -2 -2`, `0 0 0`, `1 2 3`, `1 1 1 0`) to `5-split.spec`. It rebuilt with `ok`, `validate.py` passed, and the mutation re-check killed 10 of 10.
- I rewrote `cpp-hp-03` as a new question about which key to count for "sum divisible by m" with negative values.
- I added a full dry-run table for `count_sum_k` on `[1, −1, 5, −2, 3]`, k = 3, and checked it by brute force (answer 3). The lesson is now 1,492 words.
- I rebalanced the answer letters.

## Remaining (optional)
- Move `cpp-hp-01` and `cpp-hp-04` to the hashing topic, or replace them with prefix-sum code questions.
- Extend the lesson with a 2D prefix worked example, to reach about 1,800 words.
