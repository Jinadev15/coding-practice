---
id: cpp-hello-stl
title: First C++ Program: Word Stats
difficulty: Easy
order: 1
tags: iostream, string, vector
---
## Statement
Read words from standard input until EOF. Print:

1. `words: N`
2. `longest: W` (the first one on ties; `longest: -` if there are no words)
3. the words in reverse order on one line, separated by spaces

Use `std::string` and `std::vector`, with no C arrays or `char*`.

## Starter
```cpp
#include <iostream>
#include <string>
#include <vector>

int main() {
    std::vector<std::string> words;
    std::string w;

    return 0;
}
```

## Tests
=== sample
the robot moves forward
---
words: 4
longest: forward
forward moves robot the
=== hidden
a bb cc
---
words: 3
longest: bb
cc bb a
=== hidden

---
words: 0
longest: -


## Solution
```cpp
#include <iostream>
#include <string>
#include <vector>

int main() {
    std::vector<std::string> words;
    std::string w;
    while (std::cin >> w) words.push_back(w);
    std::cout << "words: " << words.size() << '\n';
    std::string longest = "-";
    std::size_t best = 0;
    for (const auto& s : words)
        if (s.size() > best) { best = s.size(); longest = s; }
    std::cout << "longest: " << longest << '\n';
    for (std::size_t i = words.size(); i-- > 0; )
        std::cout << words[i] << (i ? " " : "");
    std::cout << '\n';
    return 0;
}
```

`std::string` and `std::vector` manage their own memory: no buffer sizes, no `malloc`, no overflow. Compare that with the equivalent C program, which needs fixed-size buffers or manual `realloc`. `words.size()` returns `std::size_t`, so the reverse loop uses the `i-- > 0` idiom to avoid unsigned wrap-around.
