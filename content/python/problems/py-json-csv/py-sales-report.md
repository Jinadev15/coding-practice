---
id: py-sales-report
title: Sales Report CSV
difficulty: Medium
order: 3
tags: csv, aggregation, csv.writer quoting
---
## Statement
Standard input is a CSV of sales with header `region,product,units,unit_price`. Region and product names may contain commas (quoted).

Write a CSV report to **standard output** using `csv.writer` (so names with commas are quoted automatically) with header `region,units,revenue,top_product`, one row per region sorted by **revenue descending** (ties: region name ascending), where:

- `units` is the total units in the region
- `revenue` is the total of `units × unit_price`, formatted with exactly 2 decimals
- `top_product` is the product with the most units in that region (ties: product name ascending)

Rows with a non-numeric `units` or `unit_price` are skipped. Use `lineterminator="\n"` for the writer.

## Starter
```python
import csv
import sys
```

## Tests
=== sample
region,product,units,unit_price
north,widget,10,2.50
south,gadget,3,100
north,gizmo,12,1
"east, coast",widget,1,9.99
south,widget,x,1
---
region,units,revenue,top_product
south,3,300.00,gadget
north,22,37.00,gizmo
"east, coast",1,9.99,widget
=== hidden
region,product,units,unit_price
a,"p, q",2,1
a,r,2,1
b,s,1,4
---
region,units,revenue,top_product
a,4,4.00,"p, q"
b,1,4.00,s
=== hidden
region,product,units,unit_price
---
region,units,revenue,top_product

## Hints
- `csv.DictReader(sys.stdin)` and `csv.writer(sys.stdout, lineterminator="\n")`.
- Aggregate per region in a dict: total units, total revenue, and a nested dict of units per product.
- Store revenue in cents (or use `round` at the end) to avoid float noise. The tests are safe either way when you format with `:.2f`.

## Solution
Aggregate into nested dicts, then sort and let `csv.writer` handle the quoting of names that contain commas.

```python
import csv
import sys

regions = {}
for row in csv.DictReader(sys.stdin):
    try:
        units = int(row["units"])
        price = float(row["unit_price"])
    except ValueError:
        continue
    r = regions.setdefault(row["region"], {"units": 0, "revenue": 0.0, "products": {}})
    r["units"] += units
    r["revenue"] += units * price
    r["products"][row["product"]] = r["products"].get(row["product"], 0) + units

out = csv.writer(sys.stdout, lineterminator="\n")
out.writerow(["region", "units", "revenue", "top_product"])
for name, r in sorted(regions.items(), key=lambda kv: (-kv[1]["revenue"], kv[0])):
    top = min(r["products"], key=lambda p: (-r["products"][p], p))
    out.writerow([name, r["units"], f"{r['revenue']:.2f}", top])
```

`csv.writer` adds quotes only where needed (`"east, coast"`, `"p, q"`), so the output stays valid CSV that any spreadsheet can open. The default line terminator is `\r\n` (per the CSV standard), which is why the problem asks for `lineterminator="\n"`.
