---
id: py-bank-account-class
title: Bank Account Class
difficulty: Easy
order: 1
tags: classes, __init__, methods, state
---
## Statement
Write a class `BankAccount`:

- `BankAccount(owner, balance=0)` stores the owner and starting balance (an int, in cents)
- `deposit(amount)`: amount must be > 0, otherwise raise `ValueError("invalid amount")`. Adds to the balance.
- `withdraw(amount)`: amount must be > 0 (else `ValueError("invalid amount")`) and ≤ balance (else `ValueError("insufficient funds")`).
- `history()`: returns a list of strings, one per successful operation: `"deposit 50"` / `"withdraw 30"`
- `statement()`: returns `"OWNER: BALANCE"`

The driver creates accounts by name and runs commands, printing errors.

## Starter
```python
class BankAccount:
    def __init__(self, owner, balance=0):
        pass
```

## Driver
```python
accounts = {}
for line in iter(input, "END"):
    cmd, name, *rest = line.split()
    try:
        if cmd == "open":
            accounts[name] = BankAccount(name, *map(int, rest))
        elif cmd == "dep":
            accounts[name].deposit(int(rest[0]))
        elif cmd == "wd":
            accounts[name].withdraw(int(rest[0]))
        elif cmd == "show":
            print(accounts[name].statement(), accounts[name].history())
    except ValueError as e:
        print("error:", e)
```

## Tests
=== sample
open ada 100
open bob
dep ada 50
wd ada 500
wd bob 1
dep bob 20
show ada
show bob
END
---
error: insufficient funds
error: insufficient funds
ada: 150 ['deposit 50']
bob: 20 ['deposit 20']
=== hidden
open x 0
dep x -5
wd x 0
dep x 10
wd x 10
show x
END
---
error: invalid amount
error: invalid amount
x: 0 ['deposit 10', 'withdraw 10']

## Solution
State lives in the instance (owner, balance, the log), and every change goes through a method that enforces the rules. That's the point of a class.

```python
class BankAccount:
    def __init__(self, owner, balance=0):
        self.owner = owner
        self.balance = balance
        self._log = []

    def deposit(self, amount):
        if amount <= 0:
            raise ValueError("invalid amount")
        self.balance += amount
        self._log.append(f"deposit {amount}")

    def withdraw(self, amount):
        if amount <= 0:
            raise ValueError("invalid amount")
        if amount > self.balance:
            raise ValueError("insufficient funds")
        self.balance -= amount
        self._log.append(f"withdraw {amount}")

    def history(self):
        return list(self._log)

    def statement(self):
        return f"{self.owner}: {self.balance}"
```

`history()` returns a **copy** of the internal list. Returning `self._log` directly would let callers append fake entries and break the object's integrity, which is encapsulation in practice. Validating before mutating means a failed operation never leaves the account half-changed.
