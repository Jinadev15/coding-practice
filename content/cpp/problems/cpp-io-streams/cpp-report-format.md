---
id: cpp-report-format
title: Formatted Report with Manipulators
difficulty: Easy
order: 1
tags: iomanip, getline, stringstream
---
## Statement
Each input line is `name;count;price`. The name may contain spaces, and the fields are separated by `;`. Print a table:

- the name left-aligned in a field of 16
- the count right-aligned in 6
- the total (`count × price`) right-aligned in 12 with 2 decimals

Then a line of 34 `=` and `TOTAL` with the grand total, formatted the same way (`TOTAL` left in 22, the amount right in 12). Read lines with `std::getline`, split them with `std::getline(ss, field, ';')`, and format with `<iomanip>`.

## Starter
```cpp
#include <iostream>
#include <iomanip>
#include <sstream>
#include <string>

int main() {
    std::string line;
    double grand = 0;
    while (std::getline(std::cin, line)) {

    }
    return 0;
}
```

## Tests
=== sample
servo motor;4;12.5
lidar unit;1;399.99
---
servo motor          4       50.00
lidar unit           1      399.99
==================================
TOTAL                       449.99
=== hidden
x;0;10
---
x                    0        0.00
==================================
TOTAL                         0.00

## Solution
```cpp
#include <iostream>
#include <iomanip>
#include <sstream>
#include <string>

int main() {
    std::string line;
    double grand = 0;
    std::cout << std::fixed << std::setprecision(2);
    while (std::getline(std::cin, line)) {
        if (line.empty()) continue;
        std::istringstream ss(line);
        std::string name, count_s, price_s;
        std::getline(ss, name, ';');
        std::getline(ss, count_s, ';');
        std::getline(ss, price_s, ';');
        int count = std::stoi(count_s);
        double total = count * std::stod(price_s);
        grand += total;
        std::cout << std::left << std::setw(16) << name
                  << std::right << std::setw(6) << count
                  << std::setw(12) << total << '\n';
    }
    std::cout << std::string(34, '=') << '\n';
    std::cout << std::left << std::setw(22) << "TOTAL"
              << std::right << std::setw(12) << grand << '\n';
    return 0;
}
```

`std::fixed` and `std::setprecision(2)` are set **once**, because they're sticky. `std::left`/`std::right` are sticky too, so each line switches back to `right` after the name. Only `setw` resets after every item. `std::getline(ss, field, ';')` with a custom delimiter is the idiomatic way to split a line in C++, and it keeps the spaces inside names.
