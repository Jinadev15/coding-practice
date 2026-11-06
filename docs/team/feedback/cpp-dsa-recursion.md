STATUS: APPROVED

# cpp-dsa-recursion: review

## Checks run
- I extracted 12 lesson functions and checked them against a brute force or known values under ASan/UBSan:
  - `factorial`, `count_digits`, `is_palindrome`, `power`, `fib`
  - `eval` on two prefix expressions
  - `gcd_rec` and `gcd_loop`
  - `josephus` against simulation for n ≤ 30, k ≤ 7
  - `total` on a nested structure

  All passed.
- `validate.py` passed on all 8 problems.
- Mutation testing: the tests killed 52 of 52 wrong mutants.
- All 12 MCQs are correct.

## Issues found
1. The MCQ answer letters were biased: 9 of 12 were `B`.
2. The difficulty spread has no Hard problem (2 Easy, 6 Medium). That is acceptable for a foundations topic.

## Fixed
- I rebalanced the answer letters.

## Remaining (optional)
- The lesson is 1,874 words. Consider a short memoisation dry-run table for `fib_memo`.
