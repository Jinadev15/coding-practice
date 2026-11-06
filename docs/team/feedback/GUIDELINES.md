# Reviewer guidelines for authors

These rules come from reviewing the 16 finished C++ topics of Modules 10–13 (126 problems, 185 MCQs, 16 lessons). Each rule is here because the problem behind it showed up more than once. Follow them, and the review becomes a formality.

## How the review checks your work

So you know what to expect:

- Every C++ block in a lesson is compiled. Every complete function is extracted and checked against a brute force on thousands of random inputs, under ASan/UBSan.
- Every problem runs through `validate.py`. Its official test set is then **mutation-tested**: the reviewer flips one operator in your reference (`<`↔`<=`, `+1`, `max`↔`min`, `&&`↔`||`, …), keeps the mutants that really are wrong on random inputs, and checks that your tests reject each one. A wrong mutant that passes your tests means a test is missing.
- MCQs are checked for correctness, ambiguity, duplicates across topics, and **answer-position bias**.

## 1. MCQs

1. **Spread the correct letter evenly anyway.** In the first batch, 146 of 164 answers were `B`. The app shuffles options at runtime (`server.py`), so learners don't see that bias. It still shows in the CSV, in exports and in any non-shuffling view. Aim for a rough A/B/C/D balance, but treat it as nice-to-have. (An earlier version of this file said the app doesn't shuffle. That was wrong: the reviewer checked only `app/` and `static/`.)
2. **Don't make the correct option the longest or most qualified one.** In 132 of 164 questions the correct option was the longest, often the only one with a "because …" clause. Give distractors the same length and the same tone: a plausible misconception with its own (wrong) reason, never "It's slow" or "Nothing".
3. **Mix the question types.** 85% of the questions were `theory`. Each topic needs at least **3 `code` or `output` questions** (trace this loop, find the bug, predict the output) and **at least 1 complexity question**.
4. **No duplicates.** Before writing a question, grep the language's MCQ files for the idea. Duplicates found: the `unique_ptr` recursive-destructor question appeared twice in one topic, and so did negative `%`. "`operator[]` inserts" and "anti-hash tests" each appeared in two topics.
5. **Keep the topic field honest.** A question about `std::multiset::erase` doesn't belong to "Binary Search", and one about `shared_ptr` cycles in doubly linked lists doesn't belong to "Singly Linked Lists".
6. **If an explanation names option letters ("Option A never ends…"), check the letters after any reordering.** Better: refer to the code, not the letter.
7. **Stay within 8–14 per topic.** Two topics had 6–7 questions, and one had 16.
8. **Don't put literal quote characters around fields.** `add_mcqs.py` quotes the CSV for you. Writing `question: "What is …?"` stores the quotes as part of the text, and `\"` stays as a backslash. Second batch: 57 fields in the four tree-topic files arrived wrapped in quotes. The reviewer stripped them.
9. **Write the data the way a reader sees it, not in the problem's input format.** `cpp-tt-02` described a tree as "6 7 5 9 # 6 8", where the leading 6 is the token count from the judge format. A learner reads it as the root value.

## 2. Lessons

1. **Hit every section of the CEO bar, including a table-style dry run of the main algorithm.** The later lessons (intervals, strings, binary search on the answer, linked lists) were 1,200–1,450 words and had no dry run or no pattern-recognition table. The reviewer added some. Write them from the start: `lo | hi | mid | check | update` tables work well.
2. **Test lesson helpers at their boundary parameters, not only typical ones.** The sliding-window `at_most(a, K)` ran out of bounds for `K = −1`, which `exactly(a, 0)` calls. Try `k = 0`, `n = 0`, an empty string and a single element before you publish.
3. **Classes that own raw pointers must delete (or implement) copying.** The lesson's `DList` with a self-referencing sentinel would double-free if copied. Write `X(const X&) = delete; X& operator=(const X&) = delete;` and say why in one comment.
4. **Avoid ambiguous verbs.** "Reverse the rows" can mean "reverse each row" or "reverse the order of the rows", and those two give different rotations. Say exactly which one.
5. **State the conditions of every complexity claim.** "Quicksort uses O(log n) stack" is true only when you recurse into the smaller side first. "`lo + (hi − lo)/2` can't overflow" is true only when `lo ≥ 0`.
6. **Show the node type in a code block once per lesson.** `cpp-dsa-bst` and `cpp-dsa-tree-paths` give `TreeNode` only in prose, so none of their code blocks compile on their own. Put `struct TreeNode { … };` (or `ListNode`) in the first code block that uses it.
7. **Keep fragments obviously fragments.** Statement-level snippets (`for (...)` with undeclared `n`) are fine for illustration. Every *function* or *class* block must compile as written with `#include <bits/stdc++.h>` and `using namespace std;`, plus the struct definitions shown earlier in the same lesson.
8. **Use `long long`, `(unsigned char)` and `size_t` correctly in every sample.** The reviewed lessons did this well. Keep it up.

## 3. Problems

1. **Cover the boundary cases in `hidden`, by hand.** The builder adds only 3 small and 3 big random tests, so whatever the hand-written hidden block doesn't cover is covered by luck. Mutation testing found three binary-search problems where an off-by-one passed every official test:
   - `a[lo] <= a[mid]` changed to `<` (the two-element range, `lo == mid`)
   - `a[mid] > a[hi]` changed to `>=` (duplicates at the ends)
   - a descending search that skips the element right after the summit

   For every binary search, include ranges of size 1 and 2, the target at index 0, at `n−1` and next to the pivot or summit, and an unrotated array.
2. **Hidden-test checklist for each problem:** the empty input (if allowed), `n = 1`, all equal, all distinct, negatives, the maximum value (overflow), the answer at the first and last position, "no answer" (−1, empty), and every tie-break rule in the statement exercised at least once.
3. **Pack many cases into each small test.** Specs whose input is "cases until the end of input" let one small test hold 5–20 random cases, which multiplies the coverage of the 3 small generated tests. Do this for every new problem.
4. **Keep doing what worked:**
   - exact tie-break rules (leftmost, smallest index, stable order)
   - drivers that verify structure (node addresses moved, `prev` links consistent, no leaks)
   - big tests that make the naive solution time out
   - starters that fail
5. **Give each problem in a topic its own idea, and reach 6–10 for DSA topics.** Also check earlier topics: `cpp-st-decode-string` repeats `cpp-str-decode-nested`, and `cpp-ms-trap-rain` repeats `cpp-tp-trapping-rain` (with a different method). If you reuse a classic on purpose, the statement must say which new technique it trains. `cpp-dsa-list-reversal` stopped at 5.
6. **Keep legacy "suite" problems last.** Give them an `order:` after your new problems. `cpp-overflow-stats` had `order: 1`, which collided with `cpp-master-theorem`. Fixed.
7. **Hints climb from a nudge to a near-solution.** They must never paste the code. The reviewed hints follow this well.
