---
id: cpp-greedy-math-suite
title: "Greedy and Number Theory in C++: Miller–Rabin, Sieve, Scheduling, Largest Number"
difficulty: Hard
order: 1
tags: Miller-Rabin, __int128, sieve, greedy, comparators, interval scheduling
time_limit: 3
---
## Statement
```cpp
bool is_prime64(unsigned long long n);                 // deterministic for all 64-bit n
int count_primes_upto(int n);                          // primes <= n, n <= 3*10^7 (sieve)
long long max_profit_jobs(std::vector<std::array<int,2>> jobs);
    // jobs {deadline, profit}: each takes 1 unit of time, time slots 1..; schedule to maximise total profit
    // greedy: highest profit first, put each job in the LATEST free slot <= its deadline (DSU over slots)
std::string largest_concat(std::vector<long long> nums);
    // arrange non-negative numbers to form the largest possible concatenation ("0" if all zero)
```

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

bool is_prime64(unsigned long long n) {
    if (n < 2) return false;
    for (unsigned long long d = 2; d * d <= n; ++d) if (n % d == 0) return false;
    return true;
}
int count_primes_upto(int n) { int c = 0; for (int i = 2; i <= n; ++i) c += is_prime64(i); return c; }
long long max_profit_jobs(vector<array<int,2>> jobs) { long long s = 0; for (auto& j : jobs) s += j[1]; return s; }
string largest_concat(vector<long long> nums) {
    sort(nums.rbegin(), nums.rend());
    string s; for (auto x : nums) s += to_string(x);
    return s;
}
```

## Driver
```cpp
int main() {
    ios::sync_with_stdio(false); cin.tie(nullptr);
    string cmd;
    while (cin >> cmd) {
        if (cmd == "prime") {
            unsigned long long n; cin >> n;
            cout << "is_prime(" << n << ") = " << (is_prime64(n) ? "yes" : "no") << '\n';
        } else if (cmd == "count") {
            int n; cin >> n;
            cout << "primes<=" << n << " = " << count_primes_upto(n) << '\n';
        } else if (cmd == "jobs") {
            int n; cin >> n; vector<array<int,2>> j(n); for (auto& x : j) cin >> x[0] >> x[1];
            cout << "max_profit = " << max_profit_jobs(j) << '\n';
        } else if (cmd == "concat") {
            int n; cin >> n; vector<long long> a(n); for (auto& x : a) cin >> x;
            cout << "largest = " << largest_concat(a) << '\n';
        } else if (cmd == "gen") {
            int n; unsigned long long seed; cin >> n >> seed;
            mt19937_64 rng(seed);
            int pc = 0;
            for (int i = 0; i < 2000; ++i) pc += is_prime64(rng() | 1ULL);
            vector<array<int,2>> jobs(n);
            for (auto& x : jobs) { x[0] = int(rng() % (n / 2)) + 1; x[1] = int(rng() % 1000000); }
            vector<long long> a(n); for (auto& x : a) x = (long long)(rng() % 1000000);
            string lc = largest_concat(a);
            cout << "gen: primes_among_2000_odds=" << pc << " count30M=" << count_primes_upto(30000000)
                 << " jobs=" << max_profit_jobs(jobs) << " concat_len=" << lc.size() << " head=" << lc.substr(0, 20) << '\n';
        }
    }
}
```

## Tests
=== sample
prime 1000000007
prime 1000000008
count 100
jobs 5
2 100
1 19
2 27
1 25
3 15
concat 5
3 30 34 5 9
---
is_prime(1000000007) = yes
is_prime(1000000008) = no
primes<=100 = 25
max_profit = 142
largest = 9534330
=== hidden
prime 0
prime 1
prime 2
prime 3215031751
prime 18446744073709551557
prime 18446744073709551615
prime 4611686014132420609
prime 1000000000000000003
count 1
count 2
jobs 1
1 5
jobs 3
1 10
1 20
1 30
concat 3
0 0 0
concat 2
10 2
concat 4
121 12 0 1
---
is_prime(0) = no
is_prime(1) = no
is_prime(2) = yes
is_prime(3215031751) = no
is_prime(18446744073709551557) = yes
is_prime(18446744073709551615) = no
is_prime(4611686014132420609) = no
is_prime(1000000000000000003) = yes
primes<=1 = 0
primes<=2 = 1
max_profit = 5
max_profit = 30
largest = 0
largest = 210
largest = 1212110
=== hidden
gen 200000 3
---
gen: primes_among_2000_odds=95 count30M=1857859 jobs=75031235510 concat_len=1177447 head=99999949999939999809

## Hints
- **Miller–Rabin**: write n − 1 = d·2ˢ. For each witness a in {2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37}, check `a^d ≡ 1` or `a^(d·2^r) ≡ −1` for some r < s. Multiply with `(unsigned __int128)a * b % n` to avoid overflow. Handle small n and n equal to a witness first.
- **Sieve**: `vector<char>` (or a bitset over odd numbers only) up to 3·10⁷, marking from p².
- **Jobs**: sort by profit descending. DSU `parent[t]` = the latest free slot ≤ t (0 = none). Placing a job at slot s sets `parent[s] = s − 1`.
- **Concat**: sort strings with the comparator `a + b > b + a`. If the first is "0", return "0".

## Solution
```cpp
#include <bits/stdc++.h>
using namespace std;
using u64 = unsigned long long;

static u64 mulmod(u64 a, u64 b, u64 m) { return (unsigned __int128)a * b % m; }
static u64 powmod(u64 a, u64 e, u64 m) {
    u64 r = 1 % m;
    a %= m;
    for (; e; e >>= 1, a = mulmod(a, a, m)) if (e & 1) r = mulmod(r, a, m);
    return r;
}

bool is_prime64(u64 n) {
    if (n < 2) return false;
    static const u64 W[] = {2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37};
    for (u64 p : W) if (n % p == 0) return n == p;
    u64 d = n - 1; int s = 0;
    while (!(d & 1)) { d >>= 1; ++s; }
    for (u64 a : W) {
        u64 x = powmod(a, d, n);
        if (x == 1 || x == n - 1) continue;
        bool composite = true;
        for (int r = 1; r < s; ++r) {
            x = mulmod(x, x, n);
            if (x == n - 1) { composite = false; break; }
        }
        if (composite) return false;
    }
    return true;
}

int count_primes_upto(int n) {
    if (n < 2) return 0;
    vector<char> comp(n + 1, 0);
    int cnt = 0;
    for (long long i = 2; i <= n; ++i) {
        if (comp[i]) continue;
        ++cnt;
        for (long long j = i * i; j <= n; j += i) comp[j] = 1;
    }
    return cnt;
}

long long max_profit_jobs(vector<array<int,2>> jobs) {
    sort(jobs.begin(), jobs.end(), [](const auto& a, const auto& b) { return a[1] > b[1]; });
    int T = 0;
    for (auto& j : jobs) T = max(T, j[0]);
    vector<int> parent(T + 1);
    iota(parent.begin(), parent.end(), 0);
    auto find = [&](int x) { while (parent[x] != x) x = parent[x] = parent[parent[x]]; return x; };
    long long total = 0;
    for (auto& [deadline, profit] : jobs) {
        int slot = find(min(deadline, T));
        if (slot > 0) { total += profit; parent[slot] = slot - 1; }   // occupy it; the next search falls left
    }
    return total;
}

string largest_concat(vector<long long> nums) {
    vector<string> s;
    s.reserve(nums.size());
    for (auto x : nums) s.push_back(to_string(x));
    sort(s.begin(), s.end(), [](const string& a, const string& b) { return a + b > b + a; });
    if (s.empty() || s[0] == "0") return "0";
    string out;
    for (auto& x : s) out += x;
    return out;
}
```

- **Miller–Rabin with 12 prime witnesses** is a proof, not a heuristic, for every n < 3.3·10²⁴. The `__int128` product keeps `a·b mod n` exact for 64-bit moduli. Trial division up to √n would need 4·10⁹ steps for the largest 64-bit primes.
- **The sieve** marks the multiples of each prime from p², an O(n log log n) sweep through a byte array. 3·10⁷ bytes is 30 MB, and halving it by skipping even numbers is a common refinement.
- **Job scheduling** is an exchange-argument greedy. Taking jobs by decreasing profit and placing each as late as possible keeps the earlier slots free for jobs with tighter deadlines. A DSU over the time slots finds "the latest free slot ≤ d" in near-O(1), instead of scanning backwards.
- **Largest number**: the comparator `a + b > b + a` is a valid strict weak ordering (it's transitive, which takes a proof), so `std::sort` is safe. The leading-zero check turns "000" into "0".
