STATUS: APPROVED

# cpp-dsa-strings-basics: review

## Checks run
- I tested `is_anagram`, `longest_palindrome` (against a brute force, leftmost tie), `read_int` and `reverse_words` (including all-space input) under ASan/UBSan. All passed.
- `validate.py` passed on all 8 problems.
- Mutation testing: the tests killed 48 of 48 wrong mutants across the 8 problems.
- All 8 MCQs are correct.

## Issues found
1. The lesson had no dry run (1,385 words).
2. The lesson cross-references "the C special-quiz guide", which is odd in a C++ lesson. Minor.
3. The MCQ answer letters were biased: 8 of 8 were `B`. The topic has only the minimum 8.

## Fixed
- I added a centre-by-centre dry run of expand-around-centre on `"babad"`, consistent with the problem's leftmost-tie rule. The lesson is now 1,460 words.
- I rebalanced the answer letters.

## Remaining (optional)
- Add 2 code or output MCQs, for example the result of `reverse_words("  a  b ")` or the RLE of `"aaabcc"`.
- Replace the C-guide reference with a pointer to the upcoming C++ String Algorithms topic.
