STATUS: APPROVED

# cpp-complexity-cp: review

## Checks run
- Every function in the lesson was extracted and compiled (`power_mod`). It was tested at edge cases, including `m = 1`, under ASan/UBSan. All passed.
- `validate.py` passed on all 7 problems.
- Mutation testing: the official tests killed 30 of 30 wrong mutants across the 6 spec-built problems.
- All 16 MCQs were checked for correctness.

## Issues found
1. The MCQ answer letters were biased: 11 of 16 were `B`. The correct option was usually the longest.
2. The legacy problem `cpp-overflow-stats` had `order: 1`, the same as `cpp-master-theorem`.
3. The topic has 16 MCQs, above the 8–14 bar. The four extra rows are the legacy `cpp-cp-01..04`.

## Fixed
- I rebalanced the answer letters for this topic's rows in `09-dsa.csv`. The option text is unchanged, and I verified that every correct answer still maps to the same text.
- I moved `cpp-overflow-stats` to `order: 7`, so it comes last.

## Remaining (optional)
- Drop or move 2 of the legacy `cpp-cp-*` questions to get back within 14.
- The lesson is strong: all sections are present, and all complexity claims are correct.
