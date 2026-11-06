STATUS: APPROVED

# cpp-dsa-arrays-basics: review

## Checks run
- I tested `rotate_right`, `move_zeros`, `except_self`, `spiral` (every shape from 1×1 to 4×4) and `rotate90` against a brute force under ASan/UBSan, on 3,000 random arrays. All passed.
- `validate.py` passed on all 8 problems.
- Mutation testing: the tests killed 75 of 75 wrong mutants.
- All 12 MCQs are correct.

## Issues found
1. **Ambiguous lesson text (it led to a wrong rotation).** The text said "Counter-clockwise: … or reverse the rows first, then transpose" and "180°: reverse the rows and reverse each row". "Reverse the rows" can mean reversing each row or reversing the row order. If you read it as reversing the row order and then transposing, you get a *clockwise* rotation.
2. The MCQ answer letters were biased: 10 of 12 were `B`.

## Fixed
- I reworded both bullets to name the exact operation: "reverse the *order* of the rows (swap row i with row n−1−i)" and "reverse each row first, then transpose". I verified both by hand on a 3×3 example.
- I rebalanced the answer letters. `cpp-arr-11`'s explanation names option letters, so I remapped it to match.
