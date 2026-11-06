STATUS: APPROVED

# cpp-linked-trees: review

## Checks run
- I tested `remove_all`, `free_list`, `SList` (against a deque model), `reverse_rec` and the iterative `unique_ptr` destructor idiom under ASan on 2,000 random sequences. No errors and no leaks.
- `validate.py` passed on all 8 problems.
- Mutation testing: the tests killed 27 of 27 wrong mutants across the 7 spec-built problems. Zero-sum had no wrong mutants among the sampled sites.
- All 11 MCQs are correct.

## Issues found
1. **Duplicate MCQ.** `cpp-lt-01` and `cpp-dll-04` both asked about the recursive `unique_ptr` destructor.
2. Off-topic MCQs: `cpp-lt-02` (a deque of tree nodes) and `cpp-lt-03` (`shared_ptr` prev links in a doubly linked list). These come from the legacy topic, whose id is still "linked-trees".
3. The lesson had no dry run and no pattern-recognition section (1,335 words).
4. The MCQ answer letters were biased: 10 of 11 were `B`.

## Fixed
- I rewrote `cpp-lt-01` as an output question: tracing a `p && p->next` skip-two loop prints `1 3`.
- I added a `remove_all` dry run (it shows why `p` doesn't advance after a deletion) and a linked-list pattern-recognition table. The lesson is now 1,570 words.
- I rebalanced the answer letters.

## Remaining (optional)
- Move `cpp-lt-03` to `cpp-dsa-doubly-circular`.
- The topic id `cpp-linked-trees` no longer matches its content (singly linked lists). Renaming is a Head or curriculum decision.
