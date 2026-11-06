STATUS: CHANGES NEEDED

# cpp-dsa-list-reversal: review

## Checks run
- I tested `reverse`, `reverse_between` (all m ≤ n) and `reverse_k_group` (k = 1..4) against vector reversal on 2,000 random lists under ASan. All passed.
- `validate.py` passed on all 5 problems.
- Mutation testing: the tests killed 30 of 30 wrong mutants.

## Issues found
1. **Only 5 problems.** DSA topics need 6–10. This is the blocking issue.
2. There were only 6 MCQs, all `theory`, and all with answer `B`.
3. The lesson is 1,176 words, the shortest in the review. It has a dry run but no pattern-recognition table. The "variations" table partly covers that.

## Fixed
- I added 3 MCQs: `cpp-dlr-07` (output: the k-group result), `cpp-dlr-08` (code: the buggy loop that forgets to save `next`) and `cpp-dlr-09` (head insertion: memory and moves). The topic now has 9.
- I rebalanced the answer letters.

## Remaining (for the author or Head)
1. Add **1–3 problems**, each built with `build_problem.py`. Each should train a reversal idea the topic doesn't cover yet:
   - **Add two numbers stored most-significant digit first** (Medium): reverse both lists, add with a carry, reverse the result. Include unequal lengths and a final carry like `999 + 1`.
   - **Double a number stored as a list** (Medium): a reversal, or a one-pass carry look-ahead.
   - **Reverse every sublist between zero separators** (Medium): segment boundaries with the before/after pointers.

   Don't use palindrome or reorder-list here. Those belong to `cpp-dsa-fast-slow`.
2. Expand the lesson toward about 1,800 words:
   - a pattern-recognition table
   - a dry-run table for `reverse_between` with head insertion
   - a short "recursive k-group" aside, with its stack cost
