STATUS: APPROVED

# cpp-dsa-sliding-window: review

## Checks run
- I tested every lesson function against a brute force under ASan/UBSan, on 3,000 random inputs:
  - `max_window_sum`, `longest_unique`, `shortest_at_least`, `count_product_less`
  - `exactly` for K = 0..4
  - `anagram_starts`
- `validate.py` passed on all 9 problems.
- Mutation testing: the tests killed 93 of 93 wrong mutants.
- All 9 MCQs are correct.

## Issues found
1. **Lesson code bug.** `exactly(a, 0)` calls `at_most(a, -1)`. With K < 0, the shrink loop advanced `L` past `R` and read out of bounds (UB under ASan).
2. The MCQ answer letters were biased: 9 of 9 were `B`.

## Fixed
- I added `if (K < 0) return 0;` to `at_most` with a comment. `exactly(a, 0)` is now correct, and the brute-force comparison passes for K = 0..4.
- I rebalanced the answer letters.
