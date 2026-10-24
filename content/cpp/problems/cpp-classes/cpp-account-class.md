---
id: cpp-account-class
title: Bank Account with Invariants
difficulty: Easy
order: 1
tags: classes, encapsulation, const member functions
---
## Statement
Write a class `Account` that **guarantees its balance never goes negative**. Money is stored in integer cents.

```cpp
class Account {
public:
    Account(std::string owner, long long cents);   // throw std::invalid_argument if cents < 0
    bool deposit(long long cents);    // false (and no change) if cents <= 0
    bool withdraw(long long cents);   // false (and no change) if cents <= 0 or cents > balance
    long long balance() const;
    const std::string& owner() const;
    int transactions() const;         // number of SUCCESSFUL deposits + withdrawals
};
```

The data must be `private`. The driver reads commands and prints through `const Account&`, so every query function must be `const`.

Commands (one per line, after a first line with the number of commands):

| Command | Effect | Output |
|---|---|---|
| `open NAME CENTS` | create an account | `opened NAME` or `error` (if CENTS < 0 or NAME exists) |
| `dep NAME C` / `wd NAME C` | deposit / withdraw | `ok` or `fail` |
| `xfer A B C` | withdraw from A, deposit into B only if the withdrawal succeeded | `ok` or `fail` |
| `show NAME` | | `NAME: $D.CC (T tx)` |

Unknown names never appear in `dep`/`wd`/`xfer`/`show`.

## Starter
```cpp
#include <string>
#include <stdexcept>

class Account {
public:
    Account(std::string owner, long long cents) {}
    bool deposit(long long cents) { return false; }
    bool withdraw(long long cents) { return false; }
    long long balance() const { return 0; }
    const std::string& owner() const { static std::string s; return s; }
    int transactions() const { return 0; }
};
```

## Driver
```cpp
#include <iostream>
#include <iomanip>
#include <map>

void show(const Account& a) {
    std::cout << a.owner() << ": $" << a.balance() / 100 << '.'
              << std::setw(2) << std::setfill('0') << a.balance() % 100 << std::setfill(' ')
              << " (" << a.transactions() << " tx)\n";
}

int main() {
    std::map<std::string, Account> accts;
    int n; std::cin >> n;
    while (n--) {
        std::string cmd, a, b; long long c;
        std::cin >> cmd;
        if (cmd == "open") {
            std::cin >> a >> c;
            if (accts.count(a)) { std::cout << "error\n"; continue; }
            try { accts.emplace(a, Account(a, c)); std::cout << "opened " << a << '\n'; }
            catch (const std::invalid_argument&) { std::cout << "error\n"; }
        } else if (cmd == "dep" || cmd == "wd") {
            std::cin >> a >> c;
            Account& acc = accts.at(a);
            bool ok = cmd == "dep" ? acc.deposit(c) : acc.withdraw(c);
            std::cout << (ok ? "ok\n" : "fail\n");
        } else if (cmd == "xfer") {
            std::cin >> a >> b >> c;
            bool ok = accts.at(a).withdraw(c);
            if (ok) accts.at(b).deposit(c);
            std::cout << (ok ? "ok\n" : "fail\n");
        } else if (cmd == "show") {
            std::cin >> a;
            show(accts.at(a));
        }
    }
}
```

## Tests
=== sample
9
open ada 1000
open bob 0
dep ada 550
wd bob 1
xfer ada bob 1200
show ada
show bob
open eve -5
show bob
---
opened ada
opened bob
ok
fail
ok
ada: $3.50 (2 tx)
bob: $12.00 (1 tx)
error
bob: $12.00 (1 tx)
=== hidden
12
open x 0
dep x 0
dep x -100
wd x 0
dep x 1
wd x 1
wd x 1
show x
open x 50
open y 99999999
xfer y x 99999999
show x
---
opened x
fail
fail
fail
ok
ok
fail
x: $0.00 (2 tx)
error
opened y
ok
x: $999999.99 (3 tx)
=== hidden
8
open a 500
open b 500
xfer a b 500
xfer a b 1
xfer b a 1001
show a
show b
wd b 1000
---
opened a
opened b
ok
fail
fail
a: $0.00 (1 tx)
b: $10.00 (1 tx)
ok
=== hidden
5
open big 900000000000
wd big 900000000000
dep big 7
show big
show big
---
opened big
ok
ok
big: $0.07 (2 tx)
big: $0.07 (2 tx)

## Hints
- Validate in the constructor and throw, so an invalid `Account` can never exist.
- `withdraw` must check `cents > balance_` before changing anything.
- Only count a transaction after it succeeded.

## Solution
```cpp
#include <string>
#include <stdexcept>
#include <utility>

class Account {
public:
    Account(std::string owner, long long cents) : owner_(std::move(owner)), balance_(cents) {
        if (cents < 0) throw std::invalid_argument("negative opening balance");
    }
    bool deposit(long long cents) {
        if (cents <= 0) return false;
        balance_ += cents;
        ++tx_;
        return true;
    }
    bool withdraw(long long cents) {
        if (cents <= 0 || cents > balance_) return false;
        balance_ -= cents;
        ++tx_;
        return true;
    }
    long long balance() const { return balance_; }
    const std::string& owner() const { return owner_; }
    int transactions() const { return tx_; }

private:
    std::string owner_;
    long long balance_;
    int tx_ = 0;
};
```

The class invariant ("balance ≥ 0") is established by the constructor (it throws rather than create an invalid object) and preserved by every mutator. Each one checks first and modifies only on success. Because the data is private, no outside code can break the invariant, which is the whole point of encapsulation. The query functions are `const`, so they work through the driver's `const Account&`.
