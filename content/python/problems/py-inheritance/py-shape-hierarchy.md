---
id: py-shape-hierarchy
title: Account Hierarchy with super()
difficulty: Medium
order: 1
tags: inheritance, super, overriding
---
## Statement
Build a small account hierarchy:

**`Account(owner, balance=0)`**
- `deposit(x)` adds (x > 0, else `ValueError`)
- `withdraw(x)` subtracts if `x <= balance`, else `ValueError("insufficient")`
- `month_end()` does nothing in the base class
- `__repr__` → `ClassName(owner, balance)` (use `type(self).__name__`)

**`SavingsAccount(owner, balance=0, rate=0.01)`**
- `month_end()` adds interest `round(balance * rate, 2)` (reuse `deposit`, but only if interest > 0)
- withdrawals are limited to **3 per month**; the 4th raises `ValueError("limit")` (the counter resets at `month_end`)

**`OverdraftAccount(owner, balance=0, limit=100)`**
- may go negative down to `-limit`: override `withdraw` to allow `balance - x >= -limit`
- `month_end()` charges a fee of 5 if the balance is negative (subtract directly, may go further negative)

Each subclass `__init__` must call `super().__init__`. Overrides should reuse the base behaviour through `super()` where sensible.

## Starter
```python
class Account:
    def __init__(self, owner, balance=0):
        self.owner = owner
        self.balance = balance


class SavingsAccount(Account):
    pass


class OverdraftAccount(Account):
    pass
```

## Driver
```python
kinds = {"acc": Account, "sav": SavingsAccount, "od": OverdraftAccount}
accts = {}
for line in iter(input, "END"):
    cmd, name, *a = line.split()
    try:
        if cmd == "new":
            accts[name] = kinds[a[0]](name, *map(float, a[1:]))
        elif cmd == "dep":
            accts[name].deposit(float(a[0]))
        elif cmd == "wd":
            accts[name].withdraw(float(a[0]))
        elif cmd == "month":
            accts[name].month_end()
        print(accts[name])
    except ValueError as e:
        print("error:", e)
print(all(isinstance(x, Account) for x in accts.values()))
```

## Tests
=== sample
new s sav 1000 0.05
wd s 10
wd s 10
wd s 10
wd s 10
month s
wd s 10
new o od 50
wd o 120
wd o 50
month o
END
---
SavingsAccount(s, 1000.0)
SavingsAccount(s, 990.0)
SavingsAccount(s, 980.0)
SavingsAccount(s, 970.0)
error: limit
SavingsAccount(s, 1018.5)
SavingsAccount(s, 1008.5)
OverdraftAccount(o, 50.0)
OverdraftAccount(o, -70.0)
error: insufficient
OverdraftAccount(o, -75.0)
True
=== hidden
new a acc 10
wd a 20
dep a -1
month a
new z sav 0
month z
END
---
Account(a, 10.0)
error: insufficient
error: deposit must be positive
Account(a, 10.0)
SavingsAccount(z, 0.0)
SavingsAccount(z, 0.0)
True

## Hints
- `SavingsAccount.withdraw`: check the counter, then call `super().withdraw(x)`, and increment the counter only if that succeeded.
- `OverdraftAccount.withdraw` replaces the rule completely (no `super()` call), since the base rule forbids going negative.
- The base `deposit` raises `ValueError("deposit must be positive")`.

## Solution
```python
class Account:
    def __init__(self, owner, balance=0):
        self.owner = owner
        self.balance = balance

    def deposit(self, x):
        if x <= 0:
            raise ValueError("deposit must be positive")
        self.balance += x

    def withdraw(self, x):
        if x > self.balance:
            raise ValueError("insufficient")
        self.balance -= x

    def month_end(self):
        pass

    def __repr__(self):
        return f"{type(self).__name__}({self.owner}, {self.balance})"


class SavingsAccount(Account):
    MAX_WITHDRAWALS = 3

    def __init__(self, owner, balance=0, rate=0.01):
        super().__init__(owner, balance)
        self.rate = rate
        self._withdrawals = 0

    def withdraw(self, x):
        if self._withdrawals >= self.MAX_WITHDRAWALS:
            raise ValueError("limit")
        super().withdraw(x)
        self._withdrawals += 1

    def month_end(self):
        interest = round(self.balance * self.rate, 2)
        if interest > 0:
            self.deposit(interest)
        self._withdrawals = 0


class OverdraftAccount(Account):
    def __init__(self, owner, balance=0, limit=100):
        super().__init__(owner, balance)
        self.limit = limit

    def withdraw(self, x):
        if self.balance - x < -self.limit:
            raise ValueError("insufficient")
        self.balance -= x

    def month_end(self):
        if self.balance < 0:
            self.balance -= 5
```

`__repr__` uses `type(self).__name__`, so one base implementation prints the right class name for every subclass. Overriding `withdraw` in `OverdraftAccount` **weakens a guarantee** (the balance can now be negative), which is a mild Liskov tension: code that assumed `balance >= 0` for every `Account` would break. That's exactly the kind of design question the SOLID lesson discusses.
