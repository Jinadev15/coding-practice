# Upgrade roadmap (started 2026-10-26)

**Goal:** take a learner from zero to a level well beyond what companies expect. Every topic teaches fully, from intuition to dry runs, templates, variations, pitfalls and interview answers. Every topic then trains with many problems that each use a *different* pattern or idea.

**Scope:**

| Track | Upgrade |
|---|---|
| C | Unchanged. |
| C++ | DSA (complete, from zero), robotics, OOP. |
| Python | Advanced Python, OOP, and the AI/ML/data stack. Python DSA stays as it is. |

**Standard for every new or rebuilt topic:**

- **Lesson.** Written for someone who has never seen the topic. It covers:
  - why it exists and what it builds intuition for
  - pictures or diagrams
  - a step-by-step dry run
  - complexity, with the proof idea
  - a reusable C++ template
  - how to recognise the pattern in a problem statement
  - all the common variations
  - pitfalls
  - interview Q&A
- **MCQs:** 10–15 per topic (theory, code reading, output prediction, complexity).
- **Problems:** 6–10 for DSA topics, 4–6 elsewhere. They are ordered easy → hard, each targets a distinct idea, and each has three teaching hints and a solution explanation with complexity. References are stress-tested against brute force wherever possible.

Status: `[ ]` todo · `[~]` in progress · `[x]` done

---

## C++ DSA (modules 10–21, replacing the old "10 DSA in C++")

### 10 DSA Foundations
- [x] cpp-complexity-cp: complexity analysis (Big-O/Θ/Ω, amortised, recurrences, master theorem), constraints → algorithm table, fast I/O, stress testing
- [x] cpp-dsa-recursion: recursion from zero (call stack, recursion trees, base cases, recursion → iteration)
- [x] cpp-dsa-arrays-basics: arrays, vectors and matrices (traversals, rotation, spiral, in-place tricks)
- [x] cpp-dsa-sorting: sorting algorithms from scratch (bubble, selection, insertion, merge, quick, heap, counting, radix; stability; comparators)

### 11 Array and String Patterns
- [ ] cpp-arrays-two-pointers: two pointers (opposite ends, same direction, fast/slow, partitioning, Dutch flag)
- [ ] cpp-dsa-sliding-window: fixed and variable windows, "at most K" counting, window plus hash map
- [ ] cpp-hashing-prefix: prefix sums and difference arrays (1D/2D, subarray-sum-K with hashing, range updates)
- [ ] cpp-dsa-hashing: hashing patterns (frequency, grouping, custom hashes, anti-collision, rolling ideas)
- [ ] cpp-dsa-kadane-subarrays: subarray techniques (Kadane, max product, Boyer–Moore voting, cyclic sort, missing/duplicate tricks)
- [ ] cpp-dsa-intervals-sweep: intervals and sweep line (merge, insert, meeting rooms, events, coordinate compression)
- [ ] cpp-dsa-strings-basics: string manipulation patterns (palindromes, anagrams, parsing, string building)

### 12 Searching
- [ ] cpp-binary-search: binary search on indices (lower/upper bound, rotated arrays, peak, 2D matrix)
- [ ] cpp-dsa-binary-search-answer: binary search on the answer (monotone predicates, real-valued search, min-max problems)

### 13 Linked Lists
- [ ] cpp-linked-trees: singly linked lists from scratch (insert/delete/search, sentinel nodes, ownership with unique_ptr)
- [ ] cpp-dsa-doubly-circular: doubly and circular linked lists (Josephus, circular buffers, LRU)
- [ ] cpp-dsa-list-reversal: reversal patterns (whole, sublist, k-group, recursive)
- [ ] cpp-dsa-fast-slow: fast and slow pointers (middle, Floyd cycle and cycle start, happy number, palindrome list)
- [ ] cpp-dsa-list-merge: merge and rearrange (merge two/k, partition, reorder, sort list, add numbers, copy with random pointer)
- [ ] cpp-dsa-skip-list: advanced lists (skip list, XOR list, unrolled list)

### 14 Stacks, Queues and Heaps
- [ ] cpp-stacks-queues: stacks (implementation, balanced brackets, min stack, expression evaluation, infix → postfix)
- [ ] cpp-dsa-monotonic-stack: monotonic stack (next greater, histogram, rain water, stock span, sum of subarray minimums)
- [ ] cpp-dsa-queues-deques: queues and deques (circular queue, queue via stacks, monotonic deque, sliding window max)
- [ ] cpp-dsa-heaps: heaps and priority queues (binary heap from scratch, heapify, top-K, k-way merge, median of stream, scheduling)

### 15 Trees
- [ ] cpp-dsa-tree-traversals: binary tree basics and traversals (recursive, iterative, Morris, level order, zigzag, vertical, boundary)
- [ ] cpp-dsa-tree-construction: building and serialising trees (from traversals, serialise/deserialise, codec)
- [ ] cpp-dsa-tree-paths: tree properties and paths (height, diameter, balanced, max path sum, root-to-leaf, LCA)
- [ ] cpp-dsa-bst: binary search trees (search/insert/delete, validate, kth, successor, iterator, BST from sorted)
- [ ] cpp-dsa-balanced-bst: self-balancing trees (AVL rotations, red-black properties, treaps, how std::map works)
- [ ] cpp-dsa-tries: tries (prefix search, autocomplete, word search, XOR trie)
- [ ] cpp-advanced-ds: segment trees (point/range, lazy propagation, merge sort tree)
- [ ] cpp-dsa-fenwick: Fenwick trees (BIT, range update/query, 2D BIT, inversions)
- [ ] cpp-dsa-range-queries: static range queries (sparse table, sqrt decomposition, Mo's algorithm)
- [ ] cpp-dsa-tree-advanced: advanced tree techniques (binary lifting, Euler tour, tree DP and rerooting, HLD, centroid decomposition)

### 16 Graphs
- [ ] cpp-graphs: representation, BFS and DFS (adjacency list/matrix, components, grids, multi-source BFS)
- [ ] cpp-dsa-cycles-bipartite: cycles and bipartiteness (directed/undirected cycle detection, bipartite check, odd cycles)
- [ ] cpp-dsa-topo-sort: topological sort and DAGs (Kahn, DFS order, DAG DP, course scheduling)
- [ ] cpp-dsa-shortest-paths: shortest paths (0-1 BFS, Dijkstra, Bellman–Ford, Floyd–Warshall, negative cycles, A*)
- [ ] cpp-dsa-dsu-mst: union-find and MST (path compression, union by rank, weighted DSU, Kruskal, Prim)
- [ ] cpp-dsa-graph-connectivity: connectivity (SCC with Tarjan/Kosaraju, bridges, articulation points, 2-SAT)
- [ ] cpp-dsa-euler-paths: Euler and Hamilton paths (Hierholzer, de Bruijn, bitmask Hamiltonian path)
- [ ] cpp-dsa-flows: flows and matching (Edmonds–Karp, Dinic, min cut, bipartite matching, Hopcroft–Karp)

### 17 Recursion, Backtracking and Divide & Conquer
- [ ] cpp-dsa-backtracking: backtracking (subsets, permutations, combinations, N-Queens, Sudoku, word search, pruning)
- [ ] cpp-dsa-divide-conquer: divide and conquer (inversions, quickselect, closest pair, Karatsuba, master theorem in practice)
- [ ] cpp-dsa-bits: bit manipulation (masks, subset enumeration, XOR tricks, popcount, Gray code)

### 18 Greedy
- [ ] cpp-greedy-math: greedy algorithms and proofs (exchange argument, activity selection, Huffman, jump game, gas station, scheduling)

### 19 Dynamic Programming
- [ ] cpp-dp: DP foundations (memoisation vs tabulation, state design, 1D DP)
- [ ] cpp-dsa-dp-grid: grid and 2D DP (paths, obstacles, min path sum, cherry pickup)
- [ ] cpp-dsa-dp-knapsack: knapsack family (0/1, unbounded, bounded, subset sum, coin change, partitions)
- [ ] cpp-dsa-dp-strings: string DP (LCS, edit distance, LIS (n log n), palindromic subsequences, regex/wildcard matching)
- [ ] cpp-dsa-dp-interval: interval DP (matrix chain, burst balloons, palindrome partitioning, optimal BST)
- [ ] cpp-dsa-dp-trees-graphs: DP on trees and DAGs (independent set, tree diameter DP, longest path in a DAG, counting paths)
- [ ] cpp-dsa-dp-bitmask: bitmask DP (TSP, assignment, SOS DP)
- [ ] cpp-dsa-dp-digit: digit DP and counting
- [ ] cpp-dsa-dp-games-prob: game theory and probability (minimax DP, Nim/Grundy, expected value)
- [ ] cpp-dsa-dp-optimizations: DP optimisations (prefix sums, monotonic queue, convex hull trick, divide-and-conquer, Knuth)

### 20 String Algorithms and Math
- [ ] cpp-dsa-string-matching: pattern matching (KMP, Z-function, Rabin–Karp hashing, Manacher)
- [ ] cpp-dsa-string-advanced: advanced strings (Aho–Corasick, suffix array with LCP, suffix automaton)
- [ ] cpp-dsa-number-theory: number theory (gcd, sieve, factorisation, modular arithmetic, inverses, CRT)
- [ ] cpp-dsa-combinatorics: combinatorics and matrices (nCr mod p, Catalan, inclusion–exclusion, matrix exponentiation)
- [ ] cpp-dsa-geometry: computational geometry (cross product, orientation, segment intersection, convex hull, polygon area)

### 21 Interview Mastery
- [ ] cpp-dsa-design-ds: designing data structures (LRU/LFU, rate limiter, time-based KV, randomized set, hit counter)
- [ ] cpp-dsa-interview-patterns: pattern recognition and mixed mock rounds (identify the pattern, then solve)

## C++ robotics (module 22)
- [ ] cpp-rob-transforms: 2D/3D transforms (rotation matrices, Euler angles, quaternions, homogeneous transforms, tf trees)
- [ ] cpp-rob-kinematics-mobile: mobile robot kinematics (differential drive, Ackermann, odometry)
- [ ] cpp-rob-kinematics-arm: manipulator kinematics (forward kinematics with DH parameters, Jacobians, numerical IK)
- [ ] cpp-rob-control: control (PID with anti-windup, feedforward, LQR basics, pure pursuit, Stanley)
- [ ] cpp-rob-estimation: state estimation (KF, EKF, UKF, particle filter, sensor fusion)
- [ ] cpp-rob-planning-graph: path planning on graphs and grids (Dijkstra, A*, D* Lite ideas, costmaps, inflation)
- [ ] cpp-rob-planning-sampling: sampling-based planning (RRT, RRT*, PRM, collision checking)
- [ ] cpp-rob-trajectories: trajectory generation (splines, minimum-jerk, velocity profiles, time parameterisation)
- [ ] cpp-rob-perception: point-cloud perception (voxel grids, RANSAC, clustering, ICP, normal estimation)
- [ ] cpp-rob-vision: camera geometry (pinhole model, calibration, homography, triangulation, feature matching)
- [ ] cpp-rob-slam: SLAM foundations (scan matching, pose graphs, Gauss–Newton optimisation)
- [ ] cpp-rob-realtime: real-time C++ (no allocation in the loop, memory pools, lock-free queues, timing, jitter)

## C++ OOP (modules 12/14 extended)
- [ ] All 23 GoF patterns across the creational, structural and behavioural topics, each with problems
- [ ] cpp-oop-polymorphism-forms: virtual vs CRTP vs type erasure vs `std::variant`
- [ ] cpp-oop-value-semantics: value types, regular types, invariants, immutability
- [ ] cpp-oop-testing-design: designing for testability (interfaces, dependency injection, gmock)
- [ ] Low-level design case studies: elevator, chess, splitwise, vending machine, ATM, BookMyShow, rate limiter, snake & ladders, hotel booking, logging framework

## Python: advanced, OOP, AI/ML
- [ ] Advanced Python topics to 5+ problems each (decorators, generators, descriptors, metaclasses, typing, context managers, data model, internals, concurrency, testing)
- [ ] New advanced topics: advanced typing (generics, `ParamSpec`, `TypeVar` bounds, overloads), performance (profiling, vectorisation, numba-style thinking, memory), packaging and tooling, logging/config/CLI architecture, async patterns in production
- [ ] OOP: all GoF patterns in Python, plus Python low-level-design case studies
- [ ] NumPy in depth (broadcasting, vectorisation, linear algebra, random, memory layout)
- [ ] pandas in depth (indexing, groupby, merge/join, reshaping, time series, performance)
- [ ] Data visualisation (matplotlib)
- [ ] Statistics and probability with SciPy (distributions, hypothesis tests, bootstrap)
- [ ] scikit-learn (preprocessing, pipelines, model selection, metrics, every major model family)
- [ ] ML from scratch (linear/logistic regression, kNN, Naive Bayes, decision trees, random forests, gradient boosting, SVM, k-means, PCA, GMM/EM)
- [ ] Deep learning with PyTorch (tensors, autograd, nn.Module, training loops, initialisation, optimisers, regularisation, CNNs, RNN/LSTM, attention and transformers from scratch)
- [ ] NLP (tokenisation, embeddings, sequence models), computer vision (augmentation, CNN pipelines)
- [ ] Applied ML engineering (feature engineering, data leakage, evaluation design, model serving, reproducibility, experiment tracking)
- [ ] LLM application engineering (embeddings, vector search, RAG pipelines, evaluation; offline)
