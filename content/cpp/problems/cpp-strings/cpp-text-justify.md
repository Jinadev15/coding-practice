---
id: cpp-text-justify
title: Full Text Justification
difficulty: Hard
order: 1
tags: string, string_view, greedy, formatting
---
## Statement
Format a paragraph into lines of exactly `W` characters (the classic text-justification problem):

- Pack words greedily: put as many words on each line as fit, with at least one space between words.
- **Fully justify** every line except the last: distribute the spaces as evenly as possible between words, and when they don't divide evenly, the **leftmost** gaps get one more space.
- A line containing a single word is left-aligned and padded with spaces on the right.
- The **last line** is left-aligned (single spaces between words) and padded on the right.
- Every output line is wrapped in `|` characters so the trailing spaces are visible.

Input: `W` on the first line, then the text (any number of lines; words are separated by any whitespace). Every word's length is ≤ W. If there are no words, print nothing.

Use `std::string_view` to refer to words in the input buffer without copying them.

## Starter
```cpp
#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <iterator>

int main() {
    int W;
    std::cin >> W;
    std::string text((std::istreambuf_iterator<char>(std::cin)), std::istreambuf_iterator<char>());
}
```

## Tests
=== sample
16
This is an example of text justification.
---
|This    is    an|
|example  of text|
|justification.  |
=== hidden
20
What must be acknowledgment shall be
---
|What     must     be|
|acknowledgment shall|
|be                  |
=== hidden
5
a b c d e f g h i j k
---
|a b c|
|d e f|
|g h i|
|j k  |
=== hidden
10
   
---

=== hidden
6
robots
---
|robots|
=== hidden
11
Science  is what we
understand well enough to explain to a computer.
Art is everything else we do
---
|Science  is|
|what     we|
|understand |
|well enough|
|to  explain|
|to        a|
|computer.  |
|Art      is|
|everything |
|else we do |

## Hints
- Split `text` into `std::string_view` words by scanning for runs of non-whitespace. The views stay valid because `text` lives until the end of `main`.
- For a line with words `[i, j)`: `letters` = the sum of their lengths, `gaps = j - i - 1`, `spaces = W - letters`. Each gap gets `spaces / gaps` spaces, and the first `spaces % gaps` gaps get one more.
- Build each line in a `std::string` with `reserve(W)` and `append(n, ' ')`.

## Solution
```cpp
#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <iterator>
#include <cctype>

int main() {
    int W;
    std::cin >> W;
    std::string text((std::istreambuf_iterator<char>(std::cin)), std::istreambuf_iterator<char>());

    std::vector<std::string_view> words;
    std::string_view all(text);
    std::size_t i = 0;
    while (i < all.size()) {
        while (i < all.size() && std::isspace(static_cast<unsigned char>(all[i]))) ++i;
        std::size_t j = i;
        while (j < all.size() && !std::isspace(static_cast<unsigned char>(all[j]))) ++j;
        if (j > i) words.push_back(all.substr(i, j - i));   // a view, no copy
        i = j;
    }

    std::string line;
    line.reserve(static_cast<std::size_t>(W));
    for (std::size_t a = 0; a < words.size();) {
        std::size_t b = a, letters = 0;
        while (b < words.size() && letters + words[b].size() + (b - a) <= static_cast<std::size_t>(W))
            letters += words[b++].size();
        std::size_t gaps = b - a - 1;
        line.clear();
        if (b == words.size() || gaps == 0) {               // last line or single word: left-align
            for (std::size_t k = a; k < b; ++k) {
                if (k > a) line += ' ';
                line += words[k];
            }
            line.append(static_cast<std::size_t>(W) - line.size(), ' ');
        } else {
            std::size_t spaces = static_cast<std::size_t>(W) - letters;
            for (std::size_t k = a; k < b; ++k) {
                line += words[k];
                if (k + 1 < b) line.append(spaces / gaps + (k - a < spaces % gaps ? 1 : 0), ' ');
            }
        }
        std::cout << '|' << line << "|\n";
        a = b;
    }
}
```

The greedy packing condition `letters + next_word + (number of words so far) <= W` accounts for the minimum one space per gap. `string_view` lets the word list point into the single input buffer, so no per-word allocations are made, which is the idiomatic use of views as *parameters and local slices of a longer-lived owner*. Appending a `string_view` to a `std::string` and `append(count, ' ')` build each line in place inside a buffer that's reserved once.
