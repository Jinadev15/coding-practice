---
id: cpp-str-build-and-encode
title: Reverse Words and Run-Length Encoding
difficulty: Easy
order: 5
tags: strings, in-place, run-length encoding, two pointers
time_limit: 1
---
## Statement
```cpp
std::string reverse_words(std::string s);
    // words (maximal runs of non-spaces) in reverse order, joined by single spaces, no leading/trailing spaces
std::string rle_encode(const std::string& s);   // "aaabcc" -> "a3b1c2"   (letters only)
std::string rle_decode(const std::string& s);   // inverse; counts can have several digits ("a12" -> 12 a's)
```

Do `reverse_words` with O(1) extra memory: reverse the whole string, then reverse each word back, compacting the spaces with a write index. Build the RLE output by **appending** (never prepending), using two indices to find each run.

**Input:** lines `rev <text>` (the text may contain extra spaces, but no trailing ones), `enc s` or `dec s`.

## Starter
```cpp
#include <bits/stdc++.h>
using namespace std;

string reverse_words(string s) { reverse(s.begin(), s.end()); return s; }      // also reverses the letters
string rle_encode(const string& s) { return s; }
string rle_decode(const string& s) { return s; }
```

## Driver
```cpp
int main() {
    string line;
    while (getline(cin, line)) {
        if (line.rfind("rev ", 0) == 0) cout << '[' << reverse_words(line.substr(4)) << "]\n";
        else if (line.rfind("enc ", 0) == 0) cout << rle_encode(line.substr(4)) << '\n';
        else if (line.rfind("dec ", 0) == 0) { string d = rle_decode(line.substr(4)); cout << d.size() << ' ' << (d.size() <= 60 ? d : d.substr(0, 60)) << '\n'; }
    }
}
```

## Tests
=== sample
rev the sky is blue
rev   hello world
rev a good   example
enc aaabcc
dec a3b1c2
dec x12
---
[blue is sky the]
[world hello]
[example good a]
a3b1c2
6 aaabcc
12 xxxxxxxxxxxx
=== hidden
rev word
rev a b
enc a
enc abc
dec z1
---
[word]
[b a]
a1
a1b1c1
1 z
=== hidden
rev ab  ba  bbbab b
enc bbb
rev ba a  ba  bb
enc aba
rev baa
enc bbb
enc bbbaaa
enc aaaaaabbb
rev   bbba
rev b
enc aba
dec c3a7a1a5
---
[b bbbab ba ab]
b3
[bb ba a ba]
a1b1a1
[baa]
b3
b3a3
a6b3
[bbba]
[b]
a1b1a1
16 cccaaaaaaaaaaaaa
=== hidden
rev   ab ba
rev   bbbaba ba  aabaa
enc b
rev  a
dec b6a12a6c8
enc aaaaaaaaa
dec a12a2a9
rev a abaa
enc bbbbaaabbb
rev  ab
enc aaaa
enc aaabbbaaaaa
---
[ba ab]
[aabaa ba bbbaba]
b1
[a]
32 bbbbbbaaaaaaaaaaaaaaaaaacccccccc
a9
23 aaaaaaaaaaaaaaaaaaaaaaa
[abaa a]
b4a3b3
[ab]
a4
a3b3a5
=== hidden
dec c9a11b1c12b5
enc aabbb
enc aaaaaaabbbaa
rev baa
dec c8b5c2
rev   baa  aba  baa
rev   baab  aaa
enc aa
rev  ba
rev   b  bbaba  bba
enc bbbbbbbb
dec c10
---
38 cccccccccaaaaaaaaaaabccccccccccccbbbbb
a2b3
a7b3a2
[baa]
15 ccccccccbbbbbcc
[baa aba baa]
[aaa baab]
a2
[ba]
[bba bbaba b]
b8
10 cccccccccc
=== hidden
@gen 1003260223 big
=== hidden
@gen 1003260224 big
=== hidden
@gen 1003260225 big

## Generator
```python
import random, sys
r = random.Random(int(sys.argv[1]))
big = sys.argv[2] == "big"
out = []
for _ in range(12 if not big else 3):
    t = r.random()
    if t < 0.4:
        words = ["".join(r.choice("ab") for _ in range(r.randint(1, 3))) for _ in range(r.randint(1, 5 if not big else 100000))]
        out.append("rev " + "".join(" " * r.randint(0, 2) + w for w in words))
    elif t < 0.7:
        out.append("enc " + "".join(r.choice("ab") * r.randint(1, 3) for _ in range(r.randint(1, 5 if not big else 100000))))
    else:
        out.append("dec " + "".join(r.choice("abc") + str(r.randint(1, 12)) for _ in range(r.randint(1, 5 if not big else 50000))))
print("\n".join(out))
```

## Hints
- Reverse the whole string first. Each word is now backwards, but the words are in the right order.
- Use a write index to copy each word forward with single spaces, then reverse just that word.
- RLE: find the end of each run with an inner loop. When decoding, read all the digits of the count.

## Solution
**Reverse words in place.** Reversing the whole string puts the words in the right order, with each word spelled backwards. A second pass reverses each word back. The write index `w` copies each word to its final position, adding exactly one space between words, which also squeezes out repeated, leading and trailing spaces. It's the read/write pointer and the double-reverse trick together.

**RLE** finds each run with an inner `while`, so it's two indices and still O(n) overall. Appending keeps the building linear. The decoder reads one letter, then the whole multi-digit count, and uses `append(k, c)`.

Complexity: O(n) for each (O(output) for decoding).

```cpp
#include <bits/stdc++.h>
using namespace std;

string reverse_words(string s) {
    reverse(s.begin(), s.end());                         // words in the right order, each backwards
    size_t w = 0;
    for (size_t i = 0; i < s.size(); ) {
        while (i < s.size() && s[i] == ' ') ++i;
        if (i == s.size()) break;
        if (w) s[w++] = ' ';
        size_t start = w;
        while (i < s.size() && s[i] != ' ') s[w++] = s[i++];
        reverse(s.begin() + start, s.begin() + w);       // fix this word
    }
    s.resize(w);
    return s;
}

string rle_encode(const string& s) {
    string out;
    for (size_t i = 0; i < s.size(); ) {
        size_t j = i;
        while (j < s.size() && s[j] == s[i]) ++j;        // [i, j) is one run
        out += s[i];
        out += to_string(j - i);
        i = j;
    }
    return out;
}

string rle_decode(const string& s) {
    string out;
    for (size_t i = 0; i < s.size(); ) {
        char c = s[i++];
        long long k = 0;
        while (i < s.size() && isdigit((unsigned char)s[i])) k = k * 10 + (s[i++] - '0');
        out.append(k, c);
    }
    return out;
}
```
