STATUS: APPROVED

# cpp-arrays-two-pointers: review

## Checks run
- I tested `two_sum_sorted`, `three_sum` (against a set of triples), `keep_at_most_k`, `merge_into`, `dutch_flag`, `max_water` and `trap` against brute forces under ASan/UBSan. All passed.
- `validate.py` passed on all 9 problems.
- Mutation testing: the tests killed 81 of 81 wrong mutants across the 9 problems.
- All 13 MCQs are correct.

## Issues found
1. The exam answer about the Dutch flag was imprecise. It said the value swapped in from `lo` "is known to be a 1", but when `lo == mid` it is the 0 itself.
2. The MCQ answer letters were biased: 12 of 13 were `B`.
3. Two MCQs belong to other topics: `cpp-ar-04` (unsigned char indexing) is a strings question, and `cpp-ar-03` (`nth_element`) is a sorting question. This is minor.

## Fixed
- I corrected the Dutch-flag explanation.
- I rebalanced the answer letters.

## Remaining (optional)
- The lesson is 1,723 words. A dry-run table for the Dutch flag would round it out.
