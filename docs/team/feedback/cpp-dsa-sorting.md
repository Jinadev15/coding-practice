STATUS: APPROVED

# cpp-dsa-sorting: review

## Checks run
- I tested every sort in the lesson (`bubble`, `insertion`, `merge_sort`, `lomuto` + `quicksort`, `quicksort3`, `sift_down` + `heap_sort`, `counting_sort`) against `std::sort` on 3,000 random arrays, n = 0..9 with duplicates and negatives, under ASan/UBSan. All passed.
- `validate.py` passed on all 9 problems.
- Mutation testing (10 mutants per problem):
  - All wrong mutants were killed in heap, quick, records, frequency, max-gap, min-swaps and largest-number.
  - Insertion and merge had survivors (see issues 1 and 2).
- All 12 MCQs are correct.

## Issues found
1. **`cpp-insertion-sort-trace`:** changing `n <= 12` to `n < 12` for the trace cutoff passed. No test had exactly n = 12.
2. **`cpp-merge-sort-trace`:** changing `n <= 16` to `< 16` for the trace cutoff passed, and so did an out-of-range leftover copy. No test had n = 16.
3. **Lesson claim was incomplete.** The complexity table listed quicksort's extra space as O(log n) without saying that this needs smaller-side-first recursion.
4. The MCQ answer letters were biased: 9 of 12 were `B`.

## Fixed
- I added boundary hidden tests (n = 12 and 13 for insertion, n = 16 and 17 for merge) to the specs. Both rebuilt with `ok`, and `validate.py` passed. Mutation re-check for insertion: 10 of 10 killed.
- I added a footnote to the table on quicksort's stack depth.
- I rebalanced the answer letters.

## Remaining (optional)
- Every problem with a "print the trace only when n ≤ K" rule should test n = K and n = K + 1. Heap (n ≤ 10) and quick (n ≤ 10) currently pass mutation testing, but adding those cases costs nothing.
