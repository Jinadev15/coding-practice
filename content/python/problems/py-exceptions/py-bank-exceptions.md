---
id: py-bank-exceptions
title: Bank Errors Hierarchy
difficulty: Medium
order: 2
tags: custom exceptions, hierarchy, attributes
---
## Statement
Define a small exception hierarchy and use it in transfer logic:

```text
BankError(Exception)
 ├── InvalidAmount        message: "amount must be positive, got X"
 ├── UnknownAccount       message: "no account 'NAME'", with attribute .name
 └── InsufficientFunds    message: "NAME has B, needs A", with attributes .balance and .needed
```

Then write `transfer(accounts, src, dst, amount)`, which validates in this order (amount, then source, then destination, then funds), raises the right exception, and on success moves the money.

The driver processes commands and prints `ok` or `ClassName: message`. For `InsufficientFunds` it also prints the shortfall computed from the attributes.

## Starter
```python
class BankError(Exception):
    pass

def transfer(accounts, src, dst, amount):
    pass
```

## Driver
```python
accounts = {}
for _ in range(int(input())):
    name, bal = input().split()
    accounts[name] = int(bal)
for _ in range(int(input())):
    src, dst, amt = input().split()
    try:
        transfer(accounts, src, dst, int(amt))
        print("ok")
    except InsufficientFunds as e:
        print(f"{type(e).__name__}: {e} (short by {e.needed - e.balance})")
    except BankError as e:
        print(f"{type(e).__name__}: {e}")
print(" ".join(f"{k}={v}" for k, v in sorted(accounts.items())))
print(issubclass(InsufficientFunds, BankError), issubclass(BankError, Exception))
```

## Tests
=== sample
2
ada 100
bob 50
4
ada bob 30
bob ada 500
ada zed 1
ada bob -5
---
ok
InsufficientFunds: bob has 80, needs 500 (short by 420)
UnknownAccount: no account 'zed'
InvalidAmount: amount must be positive, got -5
ada=70 bob=80
True True
=== hidden
1
x 10
3
y x 1
x x 0
x x 10
---
UnknownAccount: no account 'y'
InvalidAmount: amount must be positive, got 0
ok
x=10
True True

## Hints
- Store extra data on the exception: `def __init__(self, name): super().__init__(f"no account {name!r}"); self.name = name`.
- Validate fully **before** changing any balance, so a failed transfer never leaves money half-moved.

## Solution
Each exception carries the data a handler might need, and its message is built once in `__init__`. `transfer` checks everything before mutating, which keeps the operation **atomic**: either it fully succeeds or nothing changes.

```python
class BankError(Exception):
    pass

class InvalidAmount(BankError):
    def __init__(self, amount):
        super().__init__(f"amount must be positive, got {amount}")
        self.amount = amount

class UnknownAccount(BankError):
    def __init__(self, name):
        super().__init__(f"no account {name!r}")
        self.name = name

class InsufficientFunds(BankError):
    def __init__(self, name, balance, needed):
        super().__init__(f"{name} has {balance}, needs {needed}")
        self.balance = balance
        self.needed = needed

def transfer(accounts, src, dst, amount):
    if amount <= 0:
        raise InvalidAmount(amount)
    for name in (src, dst):
        if name not in accounts:
            raise UnknownAccount(name)
    if accounts[src] < amount:
        raise InsufficientFunds(src, accounts[src], amount)
    accounts[src] -= amount
    accounts[dst] += amount
```

The driver catches the **specific** `InsufficientFunds` first (to use its attributes), then the base `BankError` for everything else, in specific-to-general order. A transfer to yourself (`x x 10`) is allowed and nets to zero. Production banking code would also guard against concurrency (two simultaneous transfers) with locks or database transactions.
