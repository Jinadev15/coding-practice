---
id: py-money-value-object
title: A Correct Money Value Object
difficulty: Medium
order: 1
tags: value objects, frozen dataclass, Decimal, rounding, immutability, invariants
time_limit: 5
---
## Statement
Money is the canonical value object, and getting it wrong costs real money. Implement `Money` as an **immutable, validated** value with exact decimal arithmetic.

`CURRENCY_DECIMALS = {"USD": 2, "EUR": 2, "INR": 2, "JPY": 0, "KWD": 3}` gives the minor units per currency (given).

**`Money(amount, currency)`**, a `@dataclass(frozen=True)`:
- `amount` may be a `Decimal`, `int` or `str`. A **`float` raises `TypeError`**, because floats can't represent 0.1 exactly.
- An unknown currency raises `ValueError("unknown currency XYZ")`.
- The amount is quantized to the currency's minor units with `ROUND_HALF_EVEN`.
- Equal values are `==` and hash the same. **`==` across currencies is simply `False`.**

**Operations** (all return new objects):
- `+` and `-` between the **same** currency. Different currencies raise `CurrencyMismatch` (a `ValueError` subclass you define).
- Unary `-`.
- `* k` and `k *` for `int` or `Decimal` k, quantized half-even. Multiplying by a `float` or by `Money` raises `TypeError`.
- `<`, `<=`, `>`, `>=` between the same currency, else `CurrencyMismatch`.
- `str(m)` gives `"12.50 USD"` (always the currency's decimals) and `"1000 JPY"`.
- `Money.zero(currency)`.
- `allocate(ratios)`: split into parts proportional to non-negative integer ratios (at least one positive), losing **no minor unit**. Each part gets `floor(units·rᵢ/Σr)` minor units, and the leftover units go one each to the parts with the **largest remainders**, with ties going to the lower index. A negative amount raises `ValueError`.
- `split(n)` is `allocate([1]*n)`.

## Starter
```python
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_EVEN

CURRENCY_DECIMALS = {"USD": 2, "EUR": 2, "INR": 2, "JPY": 0, "KWD": 3}


class CurrencyMismatch(ValueError):
    pass


@dataclass
class Money:
    amount: float
    currency: str

    def __add__(self, other):
        return Money(self.amount + other.amount, self.currency)

    def __str__(self):
        return f"{self.amount} {self.currency}"

    def split(self, n):
        return [Money(self.amount / n, self.currency) for _ in range(n)]
```

## Driver
```python
import sys
from decimal import Decimal

def attempt(label, fn):
    try:
        r = fn()
        print(f"{label}: {r if not isinstance(r, list) else [str(x) for x in r]}")
    except CurrencyMismatch as e:
        print(f"{label}: CurrencyMismatch")
    except (TypeError, ValueError) as e:
        print(f"{label}: {type(e).__name__}: {e}")

for cmd in sys.stdin.read().split():
    if cmd == "basics":
        a, b = Money("10.005", "USD"), Money(Decimal("2.995"), "USD")
        print(a, b, Money(1000, "JPY"), Money("1.2345", "KWD"), Money("0.125", "EUR"), Money("0.135", "EUR"))
        attempt("float", lambda: Money(0.1, "USD"))
        attempt("unknown", lambda: Money(1, "XYZ"))
        print(a + b, a - b, -a, a * 3, 3 * a, a * Decimal("0.5"), Money("10.01", "USD") * Decimal("0.5"))
        attempt("mix add", lambda: a + Money(1, "EUR"))
        attempt("mix lt", lambda: a < Money(1, "EUR"))
        attempt("float mul", lambda: a * 1.5)
        attempt("money mul", lambda: a * b)
        print(a == Money("10.00", "USD"), a == Money("10", "EUR"), a > b, b <= a, Money.zero("JPY"), hash(Money("1.10", "USD")) == hash(Money("1.1", "USD")))
        try:
            a.amount = Decimal(5)
        except Exception as e:
            print("immutable:", type(e).__name__)
        print(len({Money("1", "USD"), Money("1.00", "USD"), Money("1", "EUR")}))
    elif cmd == "allocate":
        attempt("split 3", lambda: Money("100", "USD").split(3))
        attempt("70/30", lambda: Money("0.05", "USD").allocate([70, 30]))
        attempt("1:1:1 jpy", lambda: Money(100, "JPY").allocate([1, 1, 1]))
        attempt("zero ratio", lambda: Money("10", "EUR").allocate([0, 1, 1]))
        attempt("remainders", lambda: Money("0.10", "USD").allocate([1, 2, 3, 4, 5, 6]))
        attempt("kwd", lambda: Money("1.000", "KWD").split(7))
        attempt("negative", lambda: Money("-5", "USD").split(2))
        attempt("no ratios", lambda: Money("5", "USD").allocate([0, 0]))
        parts = Money("12345.67", "INR").allocate([3, 5, 7, 11])
        print("conserved:", sum((p for p in parts), Money.zero("INR")) == Money("12345.67", "INR"), [str(p) for p in parts])
    elif cmd == "ledger":
        total = Money.zero("USD"); x = 7
        for i in range(20000):
            x = (x * 1103515245 + 12345) % (1 << 31)
            m = Money(Decimal(x % 100000) / 100, "USD")
            total = total + (m if i % 3 else -m) * (1 + i % 4)
        print(total, total > Money.zero("USD"))
        shares = total.split(9) if total > Money.zero("USD") else (-total).split(9)
        print([str(s) for s in shares[:3]], sum(shares, Money.zero("USD")))
```

## Tests
=== sample
basics
---
10.00 USD 3.00 USD 1000 JPY 1.234 KWD 0.12 EUR 0.14 EUR
float: TypeError: use Decimal, int or str for money, not float
unknown: ValueError: unknown currency XYZ
13.00 USD 7.00 USD -10.00 USD 30.00 USD 30.00 USD 5.00 USD 5.00 USD
mix add: CurrencyMismatch
mix lt: CurrencyMismatch
float mul: TypeError: money can only be multiplied by int or Decimal
money mul: TypeError: money can only be multiplied by int or Decimal
True False True True 0 JPY True
immutable: FrozenInstanceError
2
=== hidden
allocate
---
split 3: ['33.34 USD', '33.33 USD', '33.33 USD']
70/30: ['0.04 USD', '0.01 USD']
1:1:1 jpy: ['34 JPY', '33 JPY', '33 JPY']
zero ratio: ['0.00 EUR', '5.00 EUR', '5.00 EUR']
remainders: ['0.01 USD', '0.01 USD', '0.01 USD', '0.02 USD', '0.02 USD', '0.03 USD']
kwd: ['0.143 KWD', '0.143 KWD', '0.143 KWD', '0.143 KWD', '0.143 KWD', '0.143 KWD', '0.142 KWD']
negative: ValueError: cannot allocate a negative amount
no ratios: ValueError: ratios must be non-negative with a positive sum
conserved: True ['1424.50 INR', '2374.17 INR', '3323.83 INR', '5223.17 INR']
=== hidden
ledger
---
8157329.08 USD True
['906369.90 USD', '906369.90 USD', '906369.90 USD'] 8157329.08 USD

## Hints
- In `__post_init__`, validate the type and currency, then quantize: `q = Decimal(1).scaleb(-decimals)`, then `amount.quantize(q, rounding=ROUND_HALF_EVEN)`. Store the result with `object.__setattr__`, because the instance is frozen.
- `__eq__` must compare `(amount, currency)` and return `False` (not raise) for a different currency. With `@dataclass(frozen=True, eq=True)`, the generated `__eq__` and `__hash__` already do this once the amounts are normalised.
- `allocate`: work in **integer minor units**, `units = int(amount * 10**d)`. Compute floors and remainders with `divmod(units * r, total)`, then hand out the leftover units by sorting the indices on `(-remainder, index)`.
- `sum(parts, Money.zero(c))` needs `__add__` only, because the start value is a `Money`.

## Solution
```python
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_EVEN

CURRENCY_DECIMALS = {"USD": 2, "EUR": 2, "INR": 2, "JPY": 0, "KWD": 3}


class CurrencyMismatch(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class Money:
    amount: Decimal
    currency: str

    def __post_init__(self):
        if self.currency not in CURRENCY_DECIMALS:
            raise ValueError(f"unknown currency {self.currency}")
        amt = self.amount
        if isinstance(amt, float):
            raise TypeError("use Decimal, int or str for money, not float")
        if isinstance(amt, bool) or not isinstance(amt, (Decimal, int, str)):
            raise TypeError(f"unsupported amount type {type(amt).__name__}")
        q = Decimal(1).scaleb(-CURRENCY_DECIMALS[self.currency])
        object.__setattr__(self, "amount", Decimal(amt).quantize(q, rounding=ROUND_HALF_EVEN))

    @classmethod
    def zero(cls, currency: str) -> "Money":
        return cls(0, currency)

    def _same(self, other) -> "Money":
        if not isinstance(other, Money):
            return NotImplemented
        if other.currency != self.currency:
            raise CurrencyMismatch(f"{self.currency} vs {other.currency}")
        return other

    def __add__(self, other):
        o = self._same(other)
        return o if o is NotImplemented else Money(self.amount + o.amount, self.currency)

    def __sub__(self, other):
        o = self._same(other)
        return o if o is NotImplemented else Money(self.amount - o.amount, self.currency)

    def __neg__(self):
        return Money(-self.amount, self.currency)

    def __mul__(self, k):
        if isinstance(k, bool) or not isinstance(k, (int, Decimal)):
            raise TypeError("money can only be multiplied by int or Decimal")
        return Money(self.amount * k, self.currency)

    __rmul__ = __mul__

    def __lt__(self, other): return self.amount < self._same(other).amount
    def __le__(self, other): return self.amount <= self._same(other).amount
    def __gt__(self, other): return self.amount > self._same(other).amount
    def __ge__(self, other): return self.amount >= self._same(other).amount

    def __str__(self):
        return f"{self.amount} {self.currency}"

    def allocate(self, ratios: list[int]) -> list["Money"]:
        if self.amount < 0:
            raise ValueError("cannot allocate a negative amount")
        if any(r < 0 for r in ratios) or sum(ratios) <= 0:
            raise ValueError("ratios must be non-negative with a positive sum")
        d = CURRENCY_DECIMALS[self.currency]
        units = int(self.amount.scaleb(d))
        total = sum(ratios)
        floors, rems = zip(*(divmod(units * r, total) for r in ratios))
        parts = list(floors)
        leftover = units - sum(parts)
        for i in sorted(range(len(ratios)), key=lambda i: (-rems[i], i))[:leftover]:
            parts[i] += 1
        return [Money(Decimal(p).scaleb(-d), self.currency) for p in parts]

    def split(self, n: int) -> list["Money"]:
        return self.allocate([1] * n)
```

- **Immutable and always valid**: validation and quantization happen once, in `__post_init__`. Every `Money` that exists has a known currency and the right number of decimals, so it can be shared, hashed and used as a dict key safely.
- **No floats**: `Money(0.1)` is rejected, because `0.1` is really 0.1000000000000000055…. `Decimal` from strings or ints is exact, and `ROUND_HALF_EVEN` (banker's rounding) avoids the upward bias of always rounding halves up.
- **The currency is part of the value**: adding or comparing different currencies raises, while `==` just returns `False`. Different currencies are different values, not an error to ask about.
- **Allocation conserves every minor unit**: working in integer minor units with the largest-remainder method splits $0.05 as 70/30 into 0.04 + 0.01, and $100 three ways as 33.34 + 33.33 + 33.33. The sum always equals the original, which naive `amount / n` rounding can't guarantee. That's the classic bug in invoice splitting.
