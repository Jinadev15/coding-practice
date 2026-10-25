---
id: cpp-tp-palindromes
title: Palindrome Checks with Two Pointers
difficulty: Easy
order: 1
tags: two pointers, strings, palindromes
time_limit: 1
---
## Statement
```cpp
bool is_clean_palindrome(const std::string& s);
    // ignore everything that isn't a letter or digit, and ignore letter case
bool palindrome_after_one_deletion(const std::string& s);
    // can s (exactly as given) become a palindrome by deleting AT MOST one character?
```

`"A man, a plan, a canal: Panama"` is a clean palindrome. `"abca"` becomes one by deleting `c` (or `b`). `"abc"` can't.

Both must be O(n) with O(1) extra memory. For the second one: when `s[L] != s[R]`, one of the two characters must go. Try skipping `L`, or skipping `R`, and check whether the rest is a plain palindrome.

**Input:** lines `clean <text>` or `delete <word>`, until the end of input. The text may contain spaces. Print `yes` or `no`.

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

bool is_clean_palindrome(const string& s) { string t(s.rbegin(), s.rend()); return s == t; }
bool palindrome_after_one_deletion(const string& s) { string t(s.rbegin(), s.rend()); return s == t; }
```

## Driver
```cpp
int main() {
    string line;
    while (getline(cin, line)) {
        if (line.empty()) continue;
        auto sp = line.find(' ');
        string cmd = line.substr(0, sp), arg = sp == string::npos ? "" : line.substr(sp + 1);
        bool r = cmd == "clean" ? is_clean_palindrome(arg) : palindrome_after_one_deletion(arg);
        cout << (r ? "yes" : "no") << '\n';
    }
}
```

## Tests
=== sample
clean A man, a plan, a canal: Panama
clean race a car
delete abca
delete abc
---
yes
no
yes
no
=== hidden
clean
clean !!!
clean 0P
delete a
delete deeee
delete eedede
delete abccbxa
---
yes
yes
no
yes
yes
yes
yes
=== hidden
delete bbcbbb
clean aA1
clean  !..B!!B..! 
delete bbbbabbb
delete bbabbabbabb
clean b .1ba
delete aa
delete a
clean B1..1B
delete babb
clean   b.1
delete babbab
clean ,a,,a,
delete bbaabbbbaabb
delete bbaaabb
clean 
delete ababbbbaa
clean .!! 1
delete abaaabaaaaba
clean AAB.
---
yes
no
yes
yes
yes
no
yes
yes
yes
yes
no
yes
yes
yes
yes
yes
yes
yes
yes
no
=== hidden
delete babbcbab
delete abbbbbbcbba
clean 1A1
delete ababa
clean 
delete bbbb
clean !!
delete a
clean 
clean b b AA b b
delete a
clean aAb.
delete baaa
clean BB..AA..BB
delete aabbbbabbbaa
delete aaabbabbaa
delete baa
clean 1bBbB,,BbBb1
delete bbbabb
clean B.
---
yes
yes
yes
yes
yes
yes
yes
yes
yes
yes
yes
no
yes
yes
yes
yes
yes
yes
yes
yes
=== hidden
delete aa
delete bbbaabb
delete bbbbbababbbb
clean B1A,
clean !aa!
clean B!b  
clean 1
clean A.B
clean ,.A
clean !.BBaaBB.!
clean 1BB1
delete caaa
delete acaaa
delete baab
delete aaababbbaaa
clean B!a,B
delete bcaab
clean BAa .. aAB
delete a
delete abbbbbbbbba
---
yes
yes
yes
no
yes
yes
yes
no
yes
yes
yes
yes
yes
yes
yes
yes
yes
yes
yes
yes
=== hidden
clean aa
delete babbabbbabba
delete bab
clean !!1aaa
delete ab
clean  AB..11..BA 
delete ababaaaaabaa
delete a
delete babababb
delete bc
delete ababacbaba
delete babaaaabab
delete a
delete aba
clean  Aa1!BB!1aA 
delete abaaaacaba
clean 
delete aabaaaaabaa
delete bbb
delete abbcbbbba
---
yes
yes
yes
no
yes
yes
yes
yes
yes
yes
yes
yes
yes
yes
yes
yes
yes
yes
yes
yes
=== hidden
clean .B !,,! B.
delete ab
clean AaaA
delete aabaaaabaa
clean bBABBABb
delete bbbababb
delete ba
clean .,
clean B!B
clean  !abba! 
clean  b!AA!b 
clean 
delete abbab
delete babb
delete bbabb
delete abbbabbba
delete aa
delete babb
delete aa
delete ab
---
yes
yes
yes
yes
yes
yes
yes
yes
yes
yes
yes
yes
yes
yes
yes
yes
yes
yes
yes
yes
=== hidden
clean 
delete babbaaabbab
clean  ,1,BB,1, 
delete acaabaaa
clean a!AbbaabbA!a
clean BBBB
clean B ,A!!
clean a!.,
clean A
clean 
clean .!
clean aa
delete ababbbaba
delete aba
delete bacbbaaabbab
clean A  A1
clean ..
clean .!Bb.
delete babbbbab
delete aababaaa
---
yes
yes
yes
yes
yes
yes
no
yes
yes
yes
yes
yes
yes
yes
yes
no
yes
yes
yes
yes

## Hints
- Move inward from both ends, skipping characters that aren't `isalnum`, and compare with `tolower`.
- For one deletion, scan normally until the first mismatch `s[L] != s[R]`.
- At the mismatch, check whether `s[L+1..R]` or `s[L..R−1]` is a palindrome. You only need to branch once.

## Solution
**Clean palindrome.** Move `L` and `R` inward, skipping characters that aren't letters or digits, and compare the rest case-insensitively. Cast to `unsigned char` before calling `isalnum`/`tolower`, because passing a negative `char` is undefined behaviour.

**One deletion.** Scan from both ends while the characters match. At the first mismatch, one of `s[L]` and `s[R]` must be deleted. The matched outer parts are fine either way, so check whether `s[L+1..R]` **or** `s[L..R−1]` is a palindrome. Each check is O(n), and it happens once, so the whole thing stays O(n).

Complexity: O(n) time, O(1) space for both.

```cpp
#include <bits/stdc++.h>
using namespace std;

bool is_clean_palindrome(const string& s) {
    int L = 0, R = (int)s.size() - 1;
    while (L < R) {
        if (!isalnum((unsigned char)s[L])) { ++L; continue; }    // skip junk on the left
        if (!isalnum((unsigned char)s[R])) { --R; continue; }    // and on the right
        if (tolower((unsigned char)s[L]) != tolower((unsigned char)s[R])) return false;
        ++L; --R;
    }
    return true;
}

static bool plain(const string& s, int L, int R) {
    while (L < R) if (s[L++] != s[R--]) return false;
    return true;
}

bool palindrome_after_one_deletion(const string& s) {
    int L = 0, R = (int)s.size() - 1;
    while (L < R) {
        if (s[L] != s[R]) return plain(s, L + 1, R) || plain(s, L, R - 1);   // delete one of them
        ++L; --R;
    }
    return true;
}
```
