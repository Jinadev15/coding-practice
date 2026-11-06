STATUS: APPROVED

# cpp-binary-search: review

## Checks run
- I tested `first_true` against `lower_bound` on 3,000 random arrays. All passed.
- `validate.py` passed on all 7 problems.
- Mutation testing: before my fixes, the tests killed 80 of 83 wrong mutants.
- All 11 MCQs are correct.

## Issues found (three weak test sets)
1. In `cpp-bs-rotated`, changing `a[lo] <= a[mid]` to `<` passed. The tests had no two-element search range where `lo == mid` matters.
2. In `cpp-bs-rotated-duplicates`, changing find_min's `a[mid] > a[hi]` to `>=` passed.
3. In `cpp-bs-peaks-bitonic`, a descending search starting at `top + 2` (skipping the element right after the summit) passed.
4. **Lesson claim was too strong.** It said "`lo + (hi − lo)/2` can't overflow". That is false when lo can be a large negative value.
5. The MCQ answer letters were biased: 11 of 11 were `B`. `cpp-bs-02` (multiset erase) is off-topic.

## Fixed
- I added hand-written hidden blocks to `3-rotated.spec`, `4-rotdup.spec` and `5-peak.spec`. They cover two-element arrays, unrotated arrays, targets next to the pivot or summit, and the failing random inputs.
- All three rebuilt with `ok` and pass `validate.py`.
- I re-ran mutation testing on all three: 0 survivors (12/12, 11/11 and 11/11 killed).
- I added a lesson note on the negative-range overflow, with `std::midpoint` as an alternative.
- I rebalanced the answer letters.
