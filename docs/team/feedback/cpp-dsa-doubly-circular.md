STATUS: APPROVED

# cpp-dsa-doubly-circular: review

## Checks run
- I tested `DList` (`push_front`/`push_back`/`erase` front/back) against a `deque` model on 2,000 random operation sequences under ASan. No leaks, no errors.
- `validate.py` passed on all 7 problems.
- Mutation testing: the tests killed 35 of 35 wrong mutants.

## Issues found
1. **Ownership bug in the lesson code.** `DList` owns raw nodes and has a self-referencing sentinel, but it was copyable. Any copy would double-free.
2. The lesson had no dry run and no pattern-recognition section. It was 1,268 words.
3. There were only 7 MCQs (the bar is 8–14), and the answer letters were biased: 7 of 7 were `B`.

## Fixed
- I added `DList() = default; DList(const DList&) = delete; DList& operator=(const DList&) = delete;` with a comment explaining why. I re-ran the tests: all pass.
- I added an LRU dry run (capacity 2, matching the problem's sample) and a pattern-recognition table. The lesson is now 1,489 words.
- I added 2 MCQs: `cpp-ddl-08` (output: unlink then link_after gives move-to-front) and `cpp-ddl-09` (inserting into a sorted circular list at the wrap edge). The topic now has 9.
- I rebalanced the answer letters.

## Remaining (optional)
- The lesson is still under 1,800 words. A ring-buffer index trace would help.
