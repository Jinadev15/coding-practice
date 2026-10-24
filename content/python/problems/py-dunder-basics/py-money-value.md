---
id: py-money-value
title: Money Value Object
difficulty: Medium
order: 1
tags: __repr__, __eq__, __hash__, __lt__, value objects
---
## Statement
Write an immutable value class `Money(amount, currency)` where `amount` is stored as integer **cents**:

- constructor: `Money("12.50", "USD")` (amount given as a string with at most 2 decimals; may be negative)
- `__repr__` → `Money('12.50', 'USD')`, and `__str__` → `12.50 USD`
- `__eq__`: equal if both cents and currency are equal; comparing with a non-Money returns `NotImplemented`
- `__hash__` consistent with `__eq__`
- `__lt__`: ordering by amount, **only for the same currency**. Different currencies raise `ValueError("currency mismatch")`. Use `functools.total_ordering` to get the other comparisons.
- `__add__`: same-currency addition returns a new Money; different currencies raise `ValueError`

Make the object effectively immutable: store `_cents` and `_currency` and expose read-only properties `cents` and `currency`.

## Starter
```python
from functools import total_ordering

@total_ordering
class Money:
    def __init__(self, amount, currency):
        pass
```

## Driver
```python
items = [Money(a, c) for a, c in (x.split() for x in input().split(","))]
print(items)
print(*items, sep=" | ")
print(len(set(items)), "distinct")
usd = [m for m in items if m.currency == "USD"]
print("sorted:", sorted(usd))
print("max:", max(usd), "| total:", sum(usd[1:], usd[0]))
print(Money("1", "USD") == "1 USD", Money("1.0", "USD") == Money("1", "USD"))
try:
    Money("1", "USD") < Money("1", "EUR")
except ValueError as e:
    print("error:", e)
try:
    items[0].cents = 5
except AttributeError:
    print("immutable")
```

## Tests
=== sample
12.50 USD,3 USD,12.5 USD,7 EUR
---
[Money('12.50', 'USD'), Money('3.00', 'USD'), Money('12.50', 'USD'), Money('7.00', 'EUR')]
12.50 USD | 3.00 USD | 12.50 USD | 7.00 EUR
3 distinct
sorted: [Money('3.00', 'USD'), Money('12.50', 'USD'), Money('12.50', 'USD')]
max: 12.50 USD | total: 28.00 USD
False True
error: currency mismatch
immutable
=== hidden
-1.05 USD,0.99 USD
---
[Money('-1.05', 'USD'), Money('0.99', 'USD')]
-1.05 USD | 0.99 USD
2 distinct
sorted: [Money('-1.05', 'USD'), Money('0.99', 'USD')]
max: 0.99 USD | total: -0.06 USD
False True
error: currency mismatch
immutable

## Hints
- Parse: handle the sign, then `whole, _, frac = text.partition(".")`, `cents = int(whole) * 100 + int(frac.ljust(2, "0") or 0)`.
- Format: `sign = "-" if c < 0 else ""; c = abs(c); f"{sign}{c // 100}.{c % 100:02d}"`.
- `__hash__`: `hash((self._cents, self._currency))`.

## Solution
```python
from functools import total_ordering

@total_ordering
class Money:
    def __init__(self, amount, currency):
        text = str(amount).strip()
        sign = -1 if text.startswith("-") else 1
        whole, _, frac = text.lstrip("+-").partition(".")
        if len(frac) > 2:
            raise ValueError("too many decimals")
        self._cents = sign * (int(whole or 0) * 100 + int(frac.ljust(2, "0") or 0))
        self._currency = currency

    @property
    def cents(self):
        return self._cents

    @property
    def currency(self):
        return self._currency

    def _amount_text(self):
        sign = "-" if self._cents < 0 else ""
        c = abs(self._cents)
        return f"{sign}{c // 100}.{c % 100:02d}"

    def __repr__(self):
        return f"Money({self._amount_text()!r}, {self._currency!r})"

    def __str__(self):
        return f"{self._amount_text()} {self._currency}"

    def __eq__(self, other):
        if not isinstance(other, Money):
            return NotImplemented
        return (self._cents, self._currency) == (other._cents, other._currency)

    def __hash__(self):
        return hash((self._cents, self._currency))

    def _check(self, other):
        if self._currency != other._currency:
            raise ValueError("currency mismatch")

    def __lt__(self, other):
        if not isinstance(other, Money):
            return NotImplemented
        self._check(other)
        return self._cents < other._cents

    def __add__(self, other):
        if not isinstance(other, Money):
            return NotImplemented
        self._check(other)
        return Money(f"{(self._cents + other._cents) / 100:.2f}", self._currency)
```

`"12.50"` and `"12.5"` produce equal objects with equal hashes, so the set keeps one, which shows the eq/hash contract working. Refusing to compare different currencies is a **domain invariant** enforced by the type. Real financial code (and the Money pattern from *Patterns of Enterprise Application Architecture*) works this way.
