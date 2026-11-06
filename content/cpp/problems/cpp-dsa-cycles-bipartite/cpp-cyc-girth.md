---
id: cpp-cyc-girth
title: Shortest Cycle in an Undirected Graph (Girth)
difficulty: Hard
order: 7
tags: shortest cycle, girth, BFS from every vertex, non-tree edges
time_limit: 2
---
## Statement
Return the length (number of edges) of the **shortest cycle** in a **simple** undirected graph (no self-loops, no repeated edges), or `-1` if the graph has no cycle. This value is called the graph's **girth**.

```cpp
int girth(int n, const std::vector<std::pair<int,int>>& edges);
```

Finding *a* cycle is easy; finding the *shortest* one is harder. Run a BFS from **every** vertex `s`. During the BFS from `s`, any edge `u–v` that is not a tree edge (`v` already discovered, and `v` is not `u`'s parent) closes a cycle through `s`'s BFS tree of length at most `dist[u] + dist[v] + 1`. The minimum over all roots and all such edges is exactly the girth, because when `s` lies on a shortest cycle, the BFS from `s` sees it with exactly that length.

**Input:** cases until the end of input: `n m`, then `m` lines `u v` (1 ≤ n ≤ 2000, 0 ≤ m ≤ 5000, simple graph).

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

int girth(int n, const vector<pair<int,int>>& edges) {
    // detects whether a cycle exists, but always answers 3
    return (int)edges.size() >= n ? 3 : -1;
}
```

## Driver
```cpp
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    int n, m;
    while (cin >> n >> m) {
        vector<pair<int,int>> e(m);
        for (auto& [u, v] : e) cin >> u >> v;
        cout << girth(n, e) << '\n';
    }
}
```

## Tests
=== sample
6 7
0 1
1 2
2 3
3 4
4 5
5 0
1 4
---
4
=== sample
4 3
0 1
1 2
2 3
---
-1
=== hidden
1 0
---
-1
=== hidden
3 3
0 1
1 2
2 0
---
3
=== hidden
10 15
0 1
1 2
2 3
3 4
4 0
0 5
1 6
2 7
3 8
4 9
5 7
7 9
9 6
6 8
8 5
---
5
=== hidden
500 500
0 1
1 2
2 3
3 4
4 5
5 6
6 7
7 8
8 9
9 10
10 11
11 12
12 13
13 14
14 15
15 16
16 17
17 18
18 19
19 20
20 21
21 22
22 23
23 24
24 25
25 26
26 27
27 28
28 29
29 30
30 31
31 32
32 33
33 34
34 35
35 36
36 37
37 38
38 39
39 40
40 41
41 42
42 43
43 44
44 45
45 46
46 47
47 48
48 49
49 50
50 51
51 52
52 53
53 54
54 55
55 56
56 57
57 58
58 59
59 60
60 61
61 62
62 63
63 64
64 65
65 66
66 67
67 68
68 69
69 70
70 71
71 72
72 73
73 74
74 75
75 76
76 77
77 78
78 79
79 80
80 81
81 82
82 83
83 84
84 85
85 86
86 87
87 88
88 89
89 90
90 91
91 92
92 93
93 94
94 95
95 96
96 97
97 98
98 99
99 100
100 101
101 102
102 103
103 104
104 105
105 106
106 107
107 108
108 109
109 110
110 111
111 112
112 113
113 114
114 115
115 116
116 117
117 118
118 119
119 120
120 121
121 122
122 123
123 124
124 125
125 126
126 127
127 128
128 129
129 130
130 131
131 132
132 133
133 134
134 135
135 136
136 137
137 138
138 139
139 140
140 141
141 142
142 143
143 144
144 145
145 146
146 147
147 148
148 149
149 150
150 151
151 152
152 153
153 154
154 155
155 156
156 157
157 158
158 159
159 160
160 161
161 162
162 163
163 164
164 165
165 166
166 167
167 168
168 169
169 170
170 171
171 172
172 173
173 174
174 175
175 176
176 177
177 178
178 179
179 180
180 181
181 182
182 183
183 184
184 185
185 186
186 187
187 188
188 189
189 190
190 191
191 192
192 193
193 194
194 195
195 196
196 197
197 198
198 199
199 200
200 201
201 202
202 203
203 204
204 205
205 206
206 207
207 208
208 209
209 210
210 211
211 212
212 213
213 214
214 215
215 216
216 217
217 218
218 219
219 220
220 221
221 222
222 223
223 224
224 225
225 226
226 227
227 228
228 229
229 230
230 231
231 232
232 233
233 234
234 235
235 236
236 237
237 238
238 239
239 240
240 241
241 242
242 243
243 244
244 245
245 246
246 247
247 248
248 249
249 250
250 251
251 252
252 253
253 254
254 255
255 256
256 257
257 258
258 259
259 260
260 261
261 262
262 263
263 264
264 265
265 266
266 267
267 268
268 269
269 270
270 271
271 272
272 273
273 274
274 275
275 276
276 277
277 278
278 279
279 280
280 281
281 282
282 283
283 284
284 285
285 286
286 287
287 288
288 289
289 290
290 291
291 292
292 293
293 294
294 295
295 296
296 297
297 298
298 299
299 300
300 301
301 302
302 303
303 304
304 305
305 306
306 307
307 308
308 309
309 310
310 311
311 312
312 313
313 314
314 315
315 316
316 317
317 318
318 319
319 320
320 321
321 322
322 323
323 324
324 325
325 326
326 327
327 328
328 329
329 330
330 331
331 332
332 333
333 334
334 335
335 336
336 337
337 338
338 339
339 340
340 341
341 342
342 343
343 344
344 345
345 346
346 347
347 348
348 349
349 350
350 351
351 352
352 353
353 354
354 355
355 356
356 357
357 358
358 359
359 360
360 361
361 362
362 363
363 364
364 365
365 366
366 367
367 368
368 369
369 370
370 371
371 372
372 373
373 374
374 375
375 376
376 377
377 378
378 379
379 380
380 381
381 382
382 383
383 384
384 385
385 386
386 387
387 388
388 389
389 390
390 391
391 392
392 393
393 394
394 395
395 396
396 397
397 398
398 399
399 400
400 401
401 402
402 403
403 404
404 405
405 406
406 407
407 408
408 409
409 410
410 411
411 412
412 413
413 414
414 415
415 416
416 417
417 418
418 419
419 420
420 421
421 422
422 423
423 424
424 425
425 426
426 427
427 428
428 429
429 430
430 431
431 432
432 433
433 434
434 435
435 436
436 437
437 438
438 439
439 440
440 441
441 442
442 443
443 444
444 445
445 446
446 447
447 448
448 449
449 450
450 451
451 452
452 453
453 454
454 455
455 456
456 457
457 458
458 459
459 460
460 461
461 462
462 463
463 464
464 465
465 466
466 467
467 468
468 469
469 470
470 471
471 472
472 473
473 474
474 475
475 476
476 477
477 478
478 479
479 480
480 481
481 482
482 483
483 484
484 485
485 486
486 487
487 488
488 489
489 490
490 491
491 492
492 493
493 494
494 495
495 496
496 497
497 498
498 499
499 0
---
500
=== hidden
225 420
0 1
0 15
1 2
1 16
2 3
2 17
3 4
3 18
4 5
4 19
5 6
5 20
6 7
6 21
7 8
7 22
8 9
8 23
9 10
9 24
10 11
10 25
11 12
11 26
12 13
12 27
13 14
13 28
14 29
15 16
15 30
16 17
16 31
17 18
17 32
18 19
18 33
19 20
19 34
20 21
20 35
21 22
21 36
22 23
22 37
23 24
23 38
24 25
24 39
25 26
25 40
26 27
26 41
27 28
27 42
28 29
28 43
29 44
30 31
30 45
31 32
31 46
32 33
32 47
33 34
33 48
34 35
34 49
35 36
35 50
36 37
36 51
37 38
37 52
38 39
38 53
39 40
39 54
40 41
40 55
41 42
41 56
42 43
42 57
43 44
43 58
44 59
45 46
45 60
46 47
46 61
47 48
47 62
48 49
48 63
49 50
49 64
50 51
50 65
51 52
51 66
52 53
52 67
53 54
53 68
54 55
54 69
55 56
55 70
56 57
56 71
57 58
57 72
58 59
58 73
59 74
60 61
60 75
61 62
61 76
62 63
62 77
63 64
63 78
64 65
64 79
65 66
65 80
66 67
66 81
67 68
67 82
68 69
68 83
69 70
69 84
70 71
70 85
71 72
71 86
72 73
72 87
73 74
73 88
74 89
75 76
75 90
76 77
76 91
77 78
77 92
78 79
78 93
79 80
79 94
80 81
80 95
81 82
81 96
82 83
82 97
83 84
83 98
84 85
84 99
85 86
85 100
86 87
86 101
87 88
87 102
88 89
88 103
89 104
90 91
90 105
91 92
91 106
92 93
92 107
93 94
93 108
94 95
94 109
95 96
95 110
96 97
96 111
97 98
97 112
98 99
98 113
99 100
99 114
100 101
100 115
101 102
101 116
102 103
102 117
103 104
103 118
104 119
105 106
105 120
106 107
106 121
107 108
107 122
108 109
108 123
109 110
109 124
110 111
110 125
111 112
111 126
112 113
112 127
113 114
113 128
114 115
114 129
115 116
115 130
116 117
116 131
117 118
117 132
118 119
118 133
119 134
120 121
120 135
121 122
121 136
122 123
122 137
123 124
123 138
124 125
124 139
125 126
125 140
126 127
126 141
127 128
127 142
128 129
128 143
129 130
129 144
130 131
130 145
131 132
131 146
132 133
132 147
133 134
133 148
134 149
135 136
135 150
136 137
136 151
137 138
137 152
138 139
138 153
139 140
139 154
140 141
140 155
141 142
141 156
142 143
142 157
143 144
143 158
144 145
144 159
145 146
145 160
146 147
146 161
147 148
147 162
148 149
148 163
149 164
150 151
150 165
151 152
151 166
152 153
152 167
153 154
153 168
154 155
154 169
155 156
155 170
156 157
156 171
157 158
157 172
158 159
158 173
159 160
159 174
160 161
160 175
161 162
161 176
162 163
162 177
163 164
163 178
164 179
165 166
165 180
166 167
166 181
167 168
167 182
168 169
168 183
169 170
169 184
170 171
170 185
171 172
171 186
172 173
172 187
173 174
173 188
174 175
174 189
175 176
175 190
176 177
176 191
177 178
177 192
178 179
178 193
179 194
180 181
180 195
181 182
181 196
182 183
182 197
183 184
183 198
184 185
184 199
185 186
185 200
186 187
186 201
187 188
187 202
188 189
188 203
189 190
189 204
190 191
190 205
191 192
191 206
192 193
192 207
193 194
193 208
194 209
195 196
195 210
196 197
196 211
197 198
197 212
198 199
198 213
199 200
199 214
200 201
200 215
201 202
201 216
202 203
202 217
203 204
203 218
204 205
204 219
205 206
205 220
206 207
206 221
207 208
207 222
208 209
208 223
209 224
210 211
211 212
212 213
213 214
214 215
215 216
216 217
217 218
218 219
219 220
220 221
221 222
222 223
223 224
---
4
=== hidden
8 8
0 1
1 2
2 3
3 4
4 5
5 6
6 0
6 7
---
7
=== hidden
6 8
4 5
1 5
2 3
0 2
1 3
0 5
1 4
1 2
3 1
0 1
2 1
0 1
5 4
1 4
1 3
1 2
0 1
---
3
-1
-1
-1
=== hidden
3 3
0 2
0 1
1 2
2 0
1 0
3 3
0 1
1 2
0 2
---
3
-1
-1
3
=== hidden
3 2
0 2
0 1
7 1
3 4
9 2
7 8
0 1
1 0
---
-1
-1
-1
-1
=== hidden
@gen 3105329470 big
=== hidden
@gen 3105329471 big
=== hidden
@gen 3105329472 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
for _ in range(4 if not big else 1):
    if not big:
        n = r.randint(1, 9); target = r.randint(0, 12)
    else:
        n = 2000; target = r.choice([2100, 5000])
    es = set()
    if big and r.random() < 0.5:
        # a big cycle plus long chords: girth is large-ish
        for i in range(n): es.add((min(i, (i + 1) % n), max(i, (i + 1) % n)))
    tries = 0
    while len(es) < target and tries < 100000:
        tries += 1
        u, v = r.randrange(n), r.randrange(n)
        if u == v: continue
        es.add((min(u, v), max(u, v)))
    es = list(es); r.shuffle(es)
    print(n, len(es))
    for u, v in es: print(u, v)
```

## Hints
- A non-tree edge `u–v` met during a BFS from `s` gives a cycle of length at most `dist[u] + dist[v] + 1`.
- The shortest cycle passes through some vertex `s`; the BFS from that `s` finds it exactly. So BFS from every vertex and take the minimum.
- Ignore the edge back to the BFS parent. Stop a BFS early once `2·dist[u] + 1` can't beat the best answer.

## Solution
**Upper bounds from every BFS.** In the BFS from `s`, a non-tree edge `u–v` together with the tree paths `s…u` and `s…v` forms a closed walk of length `dist[u] + dist[v] + 1`. That walk contains a cycle no longer than itself (the two tree paths may share a prefix, which only makes the actual cycle shorter). So every candidate is ≥ the girth.

**Exactness.** Let `C` be a shortest cycle, of length `g`, and `s` any vertex on it. In the BFS from `s`, the vertices of `C` have distances along `C` no larger than their positions around the cycle, and the edge of `C` "opposite" `s` is a non-tree edge whose endpoints have distances summing to at most `g − 1`. So the BFS from `s` produces a candidate ≤ `g`. Combined with the previous paragraph, the minimum is exactly `g`.

**Parent check.** In an undirected graph, the edge back to your BFS parent is the tree edge itself, not a cycle. In a simple graph there is exactly one such edge, so `par[u] != v` is the right test (with parallel edges you would compare edge ids instead, since two copies form a 2-cycle).

**Pruning.** Once `2·dist[u] + 1 ≥ best`, every later candidate from this root is at least that long, so the BFS can stop.

Complexity: O(n·(n + m)), about 1.4·10⁷ steps here. (A per-edge alternative, "delete `u–v` and BFS for the shortest `u`–`v` path", is O(m·(n + m)).)

```cpp
#include <bits/stdc++.h>
using namespace std;

int girth(int n, const vector<pair<int,int>>& edges) {
    vector<vector<int>> adj(n);
    for (auto [u, v] : edges) { adj[u].push_back(v); adj[v].push_back(u); }
    int best = INT_MAX;
    vector<int> dist(n), par(n), q(n);
    for (int s = 0; s < n; ++s) {
        fill(dist.begin(), dist.end(), -1);
        int head = 0, tail = 0;
        dist[s] = 0; par[s] = -1; q[tail++] = s;
        while (head < tail) {
            int u = q[head++];
            if (2 * dist[u] + 1 >= best) break;        // nothing shorter can appear from here on
            for (int v : adj[u]) {
                if (dist[v] == -1) { dist[v] = dist[u] + 1; par[v] = u; q[tail++] = v; }
                else if (par[u] != v)                  // non-tree edge: closes a cycle
                    best = min(best, dist[u] + dist[v] + 1);
            }
        }
    }
    return best == INT_MAX ? -1 : best;
}
```
