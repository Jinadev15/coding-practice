STATUS: APPROVED

# cpp-dsa-kadane-subarrays: review

## Checks run
- I tested `kadane`, `max_product`, `max_profit_one`, `majority` and `cyclic_sort` against a brute force under ASan/UBSan. All passed.
- I checked the tie rule in `cpp-kd-max-subarray` ("extend on a zero prefix, update only when strictly better" gives the smallest l, then the smallest r) by an exchange argument. The builder's brute-force stress also confirms it.
- `validate.py` passed on all 8 problems.
- Mutation testing: before my fix, the tests killed 59 of 60 wrong mutants.
- All 8 MCQs are correct.

## Issues found
1. **Weak tests in `cpp-kd-majority-vote`.** A wrong mutant that changed `++n2` to `--n2` passed. The tests never made the second candidate accumulate votes.
2. The MCQ answer letters were biased: 8 of 8 were `B`. All 8 questions are `theory`.

## Fixed
- I added 7 hidden cases to `4-majority.spec`, including two-winner arrays (`1 2 2 2 1 1 3 3`, `5 6 7 6 7 6 7 8 6`) and the failing random inputs. I rebuilt it (`ok`), and `validate.py` passed.
- I rebalanced the answer letters.

## Remaining (optional)
- The topic has 8 MCQs, the minimum. Add 2 output questions, for example a Kadane trace table or the `max_product` values on `[-2, 3, -4]`.
- The lesson is 1,503 words and has a Kadane dry run. Fine.
