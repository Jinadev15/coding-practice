# String Manipulation Patterns

Strings are arrays of characters, so every array technique applies. But string problems add their own toolkit: character counting, palindromes, parsing with a cursor, building output efficiently, and comparing or transforming text. This lesson covers the patterns behind most "easy/medium string" interview questions. Advanced matching algorithms (KMP, Z-function, hashing, Manacher) get their own topic later.

## 1. Strings in C++: what costs what

```cpp
std::string s = "hello";
s.size();                 // O(1)
s[i];                     // O(1), no bounds check
s += 'x';  s += "abc";    // amortised O(1) per character
s.substr(pos, len);       // O(len): creates a COPY
s.find("ll");             // O(n·m) worst case for the naive search
s.insert(0, "x");         // O(n): shifts everything
std::string_view v(s);    // O(1) view: no copy (but beware of dangling)
```

> [!DANGER] Hidden quadratic costs
> - `s = s + c` in a loop copies the whole string every time, which is O(n²) in total. Use `s += c`.
> - Building a result by **prepending** (`out = c + out`) is O(n²). Append, then `reverse` once at the end.
> - Calling `substr` in a loop creates n copies. Pass indices or a `string_view` instead.

**Characters are small integers.** `c - 'a'` maps `'a'..'z'` to `0..25`, and `c - '0'` turns a digit character into its value. Cast to `unsigned char` before calling `isdigit`/`isalpha`/`tolower`, and before indexing arrays.

## 2. Pattern: counting characters

Anagram checks, "can s be built from these letters", "first unique character", and "minimum deletions to make two strings anagrams" all reduce to comparing **frequency arrays**:

```cpp
bool is_anagram(const string& a, const string& b) {
    if (a.size() != b.size()) return false;
    array<int, 26> c{};
    for (char ch : a) ++c[ch - 'a'];
    for (char ch : b) if (--c[ch - 'a'] < 0) return false;
    return true;
}
```

That's O(n) with O(1) memory for a fixed alphabet. With unknown characters, use `array<int,256>` or a hash map.

## 3. Pattern: palindromes

A palindrome reads the same in both directions. The two-pointer check is O(n).

**Longest palindromic substring by expanding around centres.** Every palindrome has a centre, either one character (odd length) or a gap between two characters (even length). Expand outward while the ends match:

```cpp
pair<int,int> longest_palindrome(const string& s) {      // {start, length}
    int bestL = 0, bestLen = s.empty() ? 0 : 1;
    auto expand = [&](int l, int r) {
        while (l >= 0 && r < (int)s.size() && s[l] == s[r]) { --l; ++r; }
        int len = r - l - 1;                              // the loop overshot by one on each side
        if (len > bestLen) { bestLen = len; bestL = l + 1; }
    };
    for (int c = 0; c < (int)s.size(); ++c) { expand(c, c); expand(c, c + 1); }
    return {bestL, bestLen};
}
```

**Dry run** on `"babad"`:

```text
centre       expansion                         palindrome found      best
c=0 (odd)    s[0]='b'; next l=−1 stops         "b" (len 1)           (0, 1)
c=0 (even)   s[0]='b' ≠ s[1]='a'               none
c=1 (odd)    'a'; then s[0]='b' == s[2]='b'    "bab" (len 3)         (0, 3)
             then l=−1 stops
c=1 (even)   s[1]='a' ≠ s[2]='b'               none
c=2 (odd)    'b'; s[1]='a' == s[3]='a';        "aba" (len 3)         (0, 3): not longer, keep leftmost
             s[0]='b' ≠ s[4]='d' stops
...          the remaining centres give length 1
```

That's O(n²) worst case with O(1) memory. Manacher's algorithm does it in O(n) (String Algorithms topic).

**Counting palindromic substrings** uses the same expansion: every successful step is one palindrome.

## 4. Pattern: parsing with a cursor

Many problems are "read structured text": numbers with signs, expressions, compressed strings like `3[a2[c]]`, version numbers like `1.0.10`. Keep an index `i` that only moves forward, and write small helpers:

```cpp
long long read_int(const string& s, size_t& i) {
    bool neg = false;
    if (i < s.size() && (s[i] == '-' || s[i] == '+')) neg = s[i++] == '-';
    long long v = 0;
    while (i < s.size() && isdigit((unsigned char)s[i])) v = v * 10 + (s[i++] - '0');
    return neg ? -v : v;
}
```

**`atoi` done properly** has these rules:

- skip leading spaces;
- accept an optional sign;
- read digits until the first non-digit;
- **clamp** on overflow, by checking *before* multiplying: `v > (LIMIT − d) / 10`.

**Nested structures** (`3[a2[c]]` → `accaccacc`) need recursion (Recursion topic) or a stack: push the current string and repeat count when you see `[`, then pop and combine at `]`.

## 5. Pattern: building output

- Append, don't prepend. `reserve` when you know the final size.
- **Reverse words in place:** reverse the whole string, then reverse each word. It's the same trick as array rotation.
- **Run-length encoding** (`aaabcc` → `a3b1c2`): scan the runs with two indices.
- **Zig-zag / rows conversion:** write characters into row buffers by simulation, then concatenate the rows.

```cpp
string reverse_words(string s) {             // "  the sky  is blue " -> "blue is sky the"
    reverse(s.begin(), s.end());             // words are now in the right order, but each is backwards
    size_t w = 0;                            // write position: also squeezes the extra spaces
    for (size_t i = 0; i < s.size(); ) {
        while (i < s.size() && s[i] == ' ') ++i;          // skip spaces
        if (i == s.size()) break;
        if (w) s[w++] = ' ';                              // one space between words
        size_t start = w;
        while (i < s.size() && s[i] != ' ') s[w++] = s[i++];
        reverse(s.begin() + start, s.begin() + w);        // un-reverse this word
    }
    s.resize(w);
    return s;
}
```

## 6. Pattern: comparing strings cleverly

- **Backspace comparison** (`"ab#c"` vs `"ad#c"`): scan both strings **from the right**, skipping characters that a `#` deletes. That's O(1) extra memory, with no need to build the strings.
- **One edit apart** (insert, delete or replace one character): walk both strings together. At the first mismatch, the rest must match after skipping one character in the longer string (or in both, for a replace).
- **Version numbers** `1.01` vs `1.001`: split on `.`, compare the numeric values, and treat missing parts as 0.
- **Longest common prefix:** compare column by column, or sort the strings and compare only the first and last.

## 7. Pattern: string ↔ number arithmetic

Adding or multiplying huge numbers stored as strings is schoolbook arithmetic on digit arrays (see the C special-quiz guide):

- **Addition:** go from the right, keeping a carry.
- **Multiplication:** `res[i + j + 1] += d1[i] · d2[j]`, then normalise the carries in one pass. That's O(n·m).
- Strip leading zeros at the end, but keep a single "0".

## 8. Recognising the pattern

| Problem says… | Technique |
|---|---|
| anagram / permutation / "can be formed from" | frequency array |
| palindrome substring / count palindromes | expand around centres (Manacher later) |
| "parse", "decode", "evaluate", nested brackets | cursor + helpers, or recursion / a stack |
| reverse words / rotate | reverse the whole thing, then the parts |
| compare after edits / backspaces | scan from the right, or two pointers with skips |
| very large numbers as strings | digit arrays with carries |

## 9. Complexity reminders

- Counting: O(n).
- Expanding around centres: O(n²) worst case, O(1) memory.
- Building output: O(output length) when appending.
- Naive substring search: O(n·m). KMP/Z: O(n + m) (later).

## 10. Common mistakes

- **Signed `char` as an index,** or passed to `<cctype>` functions.
- **`substr(i, len)` with `i > size()`** throws `std::out_of_range`.
- **Forgetting the even-length centres** in palindrome expansion.
- **Overflow in `atoi`.** Check the bounds before `v * 10 + d`.
- **Comparing numeric strings lexicographically** ("10" < "9").

## 11. Interview questions

> [!INTERVIEW] "Find the longest palindromic substring."
> Expand around every centre: there are 2n − 1 centres (n characters plus n − 1 gaps). That's O(n²) time and O(1) space, and it's simple to code without bugs. Mention Manacher's algorithm as the O(n) optimisation, and dynamic programming over (i, j) as an O(n²)-memory alternative.

> [!EXAM] Why is `result = c + result` inside a loop slow?
> Each prepend creates a new string and copies the existing characters, so building n characters costs 1 + 2 + … + n = O(n²). Appending with `+=` is amortised O(1) per character. Append, then reverse once.

## Check your understanding

1. How many centres does the expand-around-centre method check for a string of length n?
2. Compare `"a##c"` and `"#a#c"` with backspaces: are they equal?
3. Why does atoi check `v > (INT_MAX − d) / 10` before updating?

<details><summary>Answers</summary>

1. 2n − 1: n single-character centres and n − 1 gaps between characters.
2. Yes, both become `"c"`.
3. To detect that `v * 10 + d` would overflow before it happens. Signed overflow is undefined behaviour.

</details>
