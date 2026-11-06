# Author C report: C++ Module 15 Trees, part 1

## Topics done

All four topics have a lesson, problems built with `tools/build_problem.py`, an MCQ file and a curriculum request.

| Topic | Lesson words | Problems | MCQs | Curriculum request |
|---|---|---|---|---|
| cpp-dsa-tree-traversals | ~3250 | 8 | 12 | `# after: cpp-dsa-heaps` |
| cpp-dsa-tree-construction | ~2420 | 8 | 11 | `# after: cpp-dsa-tree-traversals` |
| cpp-dsa-tree-paths | ~2380 | 8 | 12 | `# after: cpp-dsa-tree-construction` |
| cpp-dsa-bst | ~2420 | 9 | 11 | `# after: cpp-dsa-tree-paths` |

### Problem ids, in order (Easy → Hard)

- **cpp-dsa-tree-traversals:**
  - `cpp-tt-three-orders` (E)
  - `cpp-tt-level-order` (E)
  - `cpp-tt-iterative-stack` (M)
  - `cpp-tt-morris` (M)
  - `cpp-tt-zigzag-views` (M)
  - `cpp-tt-max-width` (M)
  - `cpp-tt-vertical-order` (H)
  - `cpp-tt-boundary` (H)
- **cpp-dsa-tree-construction:**
  - `cpp-tc-parent-links` (E)
  - `cpp-tc-invert-symmetric` (E)
  - `cpp-tc-from-traversals` (M; pre+in and post+in)
  - `cpp-tc-codec` (M)
  - `cpp-tc-bst-from-preorder` (M)
  - `cpp-tc-maximum-tree` (M; monotonic stack / Cartesian tree)
  - `cpp-tc-subtree-match` (H; serialization + KMP)
  - `cpp-tc-recover-dashes` (H)
- **cpp-dsa-tree-paths:**
  - `cpp-tpath-depths` (E)
  - `cpp-tpath-good-nodes` (E)
  - `cpp-tpath-diameter-balanced` (M)
  - `cpp-tpath-root-leaf-paths` (M)
  - `cpp-tpath-lca-distance` (M)
  - `cpp-tpath-path-sum-iii` (M)
  - `cpp-tpath-tree-rob` (M; tree DP intro)
  - `cpp-tpath-max-path-sum` (H)
- **cpp-dsa-bst:**
  - `cpp-bst-search-insert` (E)
  - `cpp-bst-sorted-to-balanced` (E)
  - `cpp-bst-validate` (M)
  - `cpp-bst-delete` (M)
  - `cpp-bst-order-queries` (M; k-th, successor, predecessor)
  - `cpp-bst-iterator` (M)
  - `cpp-bst-two-sum` (M)
  - `cpp-bst-range-trim` (M)
  - `cpp-bst-recover` (H)

## What the Head must do

1. **Add the four topics to `content/cpp/curriculum.csv`** from `docs/team/requests/curriculum-cpp-dsa-{tree-traversals,tree-construction,tree-paths,bst}.tsv` (module "15 Trees"). Until then, `validate.py` prints `unknown topic folder` / `unknown topic` content errors for these folders and MCQ files. The problems themselves pass: no `[problem …]` errors.
2. **MCQ id prefixes:** `cpp-tt-`, `cpp-tc-`, `cpp-tpath-`, `cpp-bst-`. `cpp-tp-` was already taken by two-pointers, so the paths topic uses `cpp-tpath-` for both its MCQs and its problems.
3. Commit `content/cpp/lessons/cpp-dsa-{tree-traversals,tree-construction,tree-paths,bst}.md`, `content/cpp/problems/cpp-dsa-{tree-traversals,tree-construction,tree-paths,bst}/`, `content/cpp/mcq/t-cpp-dsa-{tree-traversals,tree-construction,tree-paths,bst}.csv` and the four request files.

## Shared design (useful to the Reviewer and to the part 2 author)

- **Tree format:** every problem uses level order with `#` for a missing child, prefixed by the token count (`5 1 2 3 # 4`; `0` = empty). Every statement explains the format. Output trees are printed the same way without the count (`empty` for no nodes), and anything over 60 tokens is printed as `nodes=N hash=H`. Long lists are printed as `count=C hash=H`.
- **Drivers:** they read stdin with one buffered read and build and free trees iteratively, so 5·10⁵-node chains are safe. They guard against cycles and shared nodes when printing (`INVALID …`), and they check structure where it matters:
  - Morris must restore the tree (`TREE MODIFIED`).
  - `is_symmetric` must not modify the tree.
  - The codec frees the original before deserializing.
  - `recover` must keep the same node addresses (`NODES CHANGED`).
- **Stack depth:** problems that teach recursion run the user's code on a 256 MB pthread stack (statement: "plain recursion is safe here"). Problems that teach iteration (`cpp-tt-iterative-stack`, `cpp-tt-morris`) run on the normal 8 MB stack with 5·10⁵-node left or zigzag chains. I checked that a recursive solution segfaults on those big tests. `cpp-bst-iterator`'s 3·10⁵ chain does *not* crash a recursive flattener (the frames are small), so its statement only recommends iteration and makes no claim about crashing.
- **Sizes:** every big test is at most about 10⁶ numbers. References stay under 30% of the time limit, and all of them were stress-tested against a brute force (300 inputs, every 10th under ASan/UBSan).
- **MCQs:** answer letters are balanced (3/3/3/3 or 3/3/3/2 per topic). Correct options are no longer the longest (at most a tie). Each topic has at least 3 code/output questions and at least 1 complexity question.
- **Lessons:** every C++ block compiles (checked with a script). The BST lesson's functions were also run against `std::set` on 3000 random operation sequences under ASan/UBSan. Each lesson has table-style dry runs, complexity, pattern cues, mistakes, interview Q&A and "Check your understanding".

## Authoring sources

- Spec templates are in `.authoring/cpp/cpp-dsa-tree-paths/src/` and `.authoring/cpp/cpp-dsa-bst/src/` (`*.spec.in` with `@@PLACEHOLDERS@@`).
- The shared pieces and helper scripts are in `.authoring/cpp/cpp-dsa-tree-traversals/lib/`:
  - the shared pieces: `head.txt`, `drv.txt`, `gen.txt`, …
  - `expand.py` (fills the placeholders and auto-fixes tree token counts)
  - `b.sh` / `bspec.sh` (build, then validate with `JUDGE_WORKERS=2`, one problem at a time)
  - `balance.py` (MCQ answer balancing)
  - `lc.py` (compiles the lesson code blocks)
- The traversal and construction specs are maintained directly as expanded `.spec` files, because their templates were lost when the scratchpad was cleared.

## Verification

- `build_problem.py` printed `ok` for all 33 problems.
- `JUDGE_WORKERS=2 python3 tools/validate.py cpp <id>` was run one problem at a time for each problem after its final build. The only output was the expected "unknown topic folder" content errors.
