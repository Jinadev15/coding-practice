---
id: py-m1-inventory
title: Warehouse Inventory Engine
difficulty: Hard
order: 1
tags: dicts, parsing, validation, sorting, formatting
---
## Statement
Build the core of a warehouse inventory system. Process commands from stdin until the end of input. All quantities are non-negative integers and prices have at most 2 decimals; store money as **integer cents** internally to avoid float errors.

| Command | Effect | Output |
|---|---|---|
| `ADD sku name price qty` | create an item (name has no spaces) | `added SKU` or `error: duplicate SKU` |
| `RESTOCK sku qty` | increase stock | `restocked SKU to N` |
| `SELL sku qty` | sell `qty` units if enough stock | `sold Q SKU for $X.XX` or `error: insufficient SKU (have N)` |
| `PRICE sku price` | change the price | `price SKU $X.XX` |
| `REMOVE sku` | delete the item (only if its stock is 0) | `removed SKU` or `error: SKU still has N units` |
| `REPORT` | inventory table (see below) | |
| `TOP k` | the k best-selling skus by units sold (ties: revenue desc, then sku asc), as `sku units $revenue`, one per line | |

Any command naming an unknown sku prints `error: unknown SKU`. A malformed command (wrong argument count, non-numeric values, negative numbers, or a price with more than 2 decimals) prints `error: bad command`. Blank lines are ignored.

**REPORT** prints the items sorted by sku: `sku` left-aligned in 8, `name` left-aligned in 12, `qty` right-aligned in 5, and the value of the stock (`qty × price`) right-aligned in 12 as `$X,XXX.XX` with thousands separators. Then a final line: `TOTAL` left-aligned in 25, followed by the total value right-aligned in 12 in the same format. With no items, print `(empty)` instead of the item lines, followed by the TOTAL line.

## Starter
```python
import sys

def main():
    for raw in sys.stdin.read().splitlines():
        line = raw.strip()
        if not line:
            continue
        cmd, *args = line.split()
        # dispatch here

main()
```

## Tests
=== sample
ADD A1 widget 2.50 10
ADD B2 gadget 1000 3
SELL A1 4
SELL B2 5
RESTOCK B2 2
SELL B2 5
ADD A1 dup 1 1
PRICE A1 3
REPORT
TOP 5
---
added A1
added B2
sold 4 A1 for $10.00
error: insufficient B2 (have 3)
restocked B2 to 5
sold 5 B2 for $5,000.00
error: duplicate A1
price A1 $3.00
A1      widget          6      $18.00
B2      gadget          0       $0.00
TOTAL                          $18.00
B2 5 $5,000.00
A1 4 $10.00
=== hidden
REPORT
ADD X1 thing 0.10 3
SELL X1 1
SELL X1 1
SELL X1 1
REMOVE X1
SELL X1 1
REPORT
---
(empty)
TOTAL                           $0.00
added X1
sold 1 X1 for $0.10
sold 1 X1 for $0.10
sold 1 X1 for $0.10
removed X1
error: unknown X1
(empty)
TOTAL                           $0.00
=== hidden
ADD P1 pen 1.999 5
ADD P1 pen -1 5
ADD P1 pen 1.5
ADD P1 pen 1.5 five
FLY P1
ADD P1 pen 1.5 5
REMOVE P1
SELL P1 0
RESTOCK Q9 1
ADD Z9 zeta 0.5 2
ADD M5 mid 0.5 2
SELL Z9 2
SELL M5 2
TOP 2
---
error: bad command
error: bad command
error: bad command
error: bad command
error: bad command
added P1
error: P1 still has 5 units
sold 0 P1 for $0.00
error: unknown Q9
added Z9
added M5
sold 2 Z9 for $1.00
sold 2 M5 for $1.00
M5 2 $1.00
Z9 2 $1.00
=== hidden
ADD BIG bulk 12345.67 1000
REPORT
SELL BIG 999
TOP 1
REPORT
---
added BIG
BIG     bulk         1000$12,345,670.00
TOTAL                    $12,345,670.00
sold 999 BIG for $12,333,324.33
BIG 999 $12,333,324.33
BIG     bulk            1  $12,345.67
TOTAL                      $12,345.67

## Hints
- Parse money with a helper: split on `.`, validate at most 2 decimal digits, return integer cents. Raise `ValueError` for anything bad, and have the dispatcher turn every `ValueError` into `error: bad command`.
- Format cents: `f"${cents // 100:,}.{cents % 100:02d}"`.
- Keep per-sku `sold_units` and `revenue_cents` for `TOP`.
- Validate the argument count per command with a table: `ARITY = {"ADD": 4, "RESTOCK": 2, ...}`.

## Solution
The design separates **parsing** (which raises `ValueError` on any bad input) from **business rules** (which print specific errors). Money is integer cents throughout, and a single formatting helper keeps every amount consistent.

```python
import sys

ARITY = {"ADD": 4, "RESTOCK": 2, "SELL": 2, "PRICE": 2, "REMOVE": 1, "REPORT": 0, "TOP": 1}

def to_cents(text):
    whole, _, frac = text.partition(".")
    if not whole.isdigit() or (frac and not frac.isdigit()) or len(frac) > 2:
        raise ValueError(text)
    return int(whole) * 100 + int(frac.ljust(2, "0") or 0)

def to_qty(text):
    if not text.isdigit():
        raise ValueError(text)
    return int(text)

def money(cents):
    return f"${cents // 100:,}.{cents % 100:02d}"

def main():
    items = {}   # sku -> dict(name, price, qty, sold, revenue)
    for raw in sys.stdin.read().splitlines():
        line = raw.strip()
        if not line:
            continue
        cmd, *args = line.split()
        try:
            if cmd not in ARITY or len(args) != ARITY[cmd]:
                raise ValueError(cmd)
            if cmd == "ADD":
                sku, name, price, qty = args
                price, qty = to_cents(price), to_qty(qty)
                if sku in items:
                    print(f"error: duplicate {sku}")
                else:
                    items[sku] = {"name": name, "price": price, "qty": qty,
                                  "sold": 0, "revenue": 0}
                    print(f"added {sku}")
            elif cmd == "REPORT":
                total = 0
                if not items:
                    print("(empty)")
                for sku in sorted(items):
                    it = items[sku]
                    value = it["qty"] * it["price"]
                    total += value
                    print(f"{sku:<8}{it['name']:<12}{it['qty']:>5}{money(value):>12}")
                print(f"{'TOTAL':<25}{money(total):>12}")
            elif cmd == "TOP":
                k = to_qty(args[0])
                ranked = sorted(items.items(),
                                key=lambda kv: (-kv[1]["sold"], -kv[1]["revenue"], kv[0]))
                for sku, it in ranked[:k]:
                    print(sku, it["sold"], money(it["revenue"]))
            else:
                sku = args[0]
                num = to_cents(args[1]) if cmd == "PRICE" else (to_qty(args[1]) if len(args) > 1 else None)
                if sku not in items:
                    print(f"error: unknown {sku}")
                    continue
                it = items[sku]
                if cmd == "RESTOCK":
                    it["qty"] += num
                    print(f"restocked {sku} to {it['qty']}")
                elif cmd == "SELL":
                    if num > it["qty"]:
                        print(f"error: insufficient {sku} (have {it['qty']})")
                    else:
                        it["qty"] -= num
                        it["sold"] += num
                        it["revenue"] += num * it["price"]
                        print(f"sold {num} {sku} for {money(num * it['price'])}")
                elif cmd == "PRICE":
                    it["price"] = num
                    print(f"price {sku} {money(num)}")
                elif cmd == "REMOVE":
                    if it["qty"]:
                        print(f"error: {sku} still has {it['qty']} units")
                    else:
                        del items[sku]
                        print(f"removed {sku}")
        except ValueError:
            print("error: bad command")

main()
```

Validation happens **before** any lookup, so `SELL P1 x` is a bad command even for an unknown sku. Note how `RESTOCK Q9 1` parses fine and only then reports the unknown sku. This is exactly the shape of a real command processor. In the OOP module you'll restructure it into `Item`, `Inventory` and `Command` classes, and see how much easier it becomes to extend.
