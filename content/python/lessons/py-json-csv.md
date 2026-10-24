# JSON, CSV and Serialization

Programs need to exchange data with files, web APIs, other languages and their own future runs. **Serialization** turns in-memory objects into bytes or text that can be stored or sent; **deserialization** turns them back. In practice two formats cover most needs: **JSON** (web APIs, config files, ROS 2 parameters, ML experiment metadata) and **CSV** (spreadsheets, datasets, sensor logs). Python also has **pickle** for Python-only object storage, and it carries a security warning you must know.

## 1. JSON in one picture

JSON (JavaScript Object Notation) is a text format with six value types. They map onto Python like this:

| JSON | Python (loading) | Python → JSON (dumping) |
|---|---|---|
| object `{"k": v}` | `dict` | `dict` (keys converted to strings) |
| array `[1, 2]` | `list` | `list` **and `tuple`** |
| string `"text"` | `str` | `str` |
| number `3`, `2.5` | `int`, `float` | `int`, `float` |
| `true` / `false` | `True` / `False` | `bool` |
| `null` | `None` | `None` |

> [!KEY]
> Round trips are **not** always identical: tuples come back as lists, and non-string dict keys come back as strings (`{1: "a"}` → `{"1": "a"}`). Sets, bytes, dates and your own classes can't be dumped at all without help.

## 2. The four functions

| | String | File |
|---|---|---|
| Python → JSON | `json.dumps(obj)` | `json.dump(obj, f)` |
| JSON → Python | `json.loads(text)` | `json.load(f)` |

Memory aid: the **s** stands for **string**.

```python
import json

robot = {"name": "rover", "wheels": 4, "sensors": ["lidar", "imu"], "active": True, "pose": None}
text = json.dumps(robot)
print(text)
# {"name": "rover", "wheels": 4, "sensors": ["lidar", "imu"], "active": true, "pose": null}

back = json.loads(text)
print(back["sensors"][0])        # lidar

with open("robot.json", "w", encoding="utf-8") as f:
    json.dump(robot, f, indent=2)          # pretty-printed file
with open("robot.json", encoding="utf-8") as f:
    cfg = json.load(f)
```

### Useful options

```python
json.dumps(d, indent=2)               # human-readable, multi-line
json.dumps(d, sort_keys=True)         # deterministic key order (nice for diffs and tests)
json.dumps(d, ensure_ascii=False)     # keep "é" instead of "é"
json.dumps(d, separators=(",", ":"))  # most compact form
json.dumps(d, default=str)            # call str() on anything not serializable (dates…)
```

```python
from datetime import date
json.dumps({"day": date(2026, 1, 2)}, default=str)    # '{"day": "2026-01-02"}'
json.dumps({1, 2})        # TypeError: Object of type set is not JSON serializable
```

### Errors when loading

JSON is **stricter** than Python literal syntax:

```python
json.loads("{'a': 1}")   # JSONDecodeError: property names need DOUBLE quotes
json.loads('{"a": 1,}')  # JSONDecodeError: no trailing commas
json.loads("[True]")     # JSONDecodeError: it's true, not True
```

> [!WARNING]
> Python's `json` accepts and emits `NaN` and `Infinity`, which are **not** valid JSON. Other languages may refuse them. Pass `allow_nan=False` to catch them when producing JSON for other systems.

## 3. JSON for your own classes

```python
from dataclasses import dataclass, asdict

@dataclass
class Pose:
    x: float
    y: float
    theta: float

p = Pose(1.0, 2.0, 0.5)
text = json.dumps(asdict(p))           # '{"x": 1.0, "y": 2.0, "theta": 0.5}'
p2 = Pose(**json.loads(text))          # rebuild: unpack the dict into the constructor
```

The pattern "object → dict → JSON" and "JSON → dict → object" is how almost every web framework and config system works. Pydantic automates it with validation.

## 4. CSV: tables as text

A CSV file is rows of fields separated by commas. It looks trivial, until a field contains a comma, a quote or a newline. **Never parse CSV with `line.split(",")`.** Use the `csv` module, which handles quoting correctly:

```text
name,age
Ada,36
"Smith, J",40
```

```python
import csv

with open("people.csv", newline="", encoding="utf-8") as f:
    for row in csv.reader(f):
        print(row)
# ['name', 'age']
# ['Ada', '36']
# ['Smith, J', '40']   ← the quoted comma stays inside the field
```

> [!KEY]
> - Open CSV files with **`newline=""`**. The `csv` module handles line endings itself; without it, you can get blank rows on Windows or broken multi-line fields.
> - Every field comes back as a **string**. Convert numbers yourself: `int(row["age"])`.

### `DictReader` and `DictWriter`: rows as dicts

```python
with open("people.csv", newline="", encoding="utf-8") as f:
    for rec in csv.DictReader(f):          # the header row becomes the keys
        print(rec["name"], int(rec["age"]))

rows = [{"sensor": "imu", "value": 0.98}, {"sensor": "lidar", "value": 4.2}]
with open("out.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["sensor", "value"])
    w.writeheader()
    w.writerows(rows)
```

The writer quotes fields when it needs to: `["a,b", 'c"d', 3]` becomes `"a,b","c""d",3` (an embedded quote is doubled).

Other dialects: `csv.reader(f, delimiter="\t")` for TSV, `delimiter=";"` for European spreadsheets. For heavy data analysis, pandas' `read_csv` is the tool (Scientific Stack module), but the `csv` module is dependency-free and streams files of any size.

## 5. pickle: Python objects as bytes, and its danger

```python
import pickle
data = {"weights": [0.1, 0.2], "seen": {1, 2}}     # sets are fine here
blob = pickle.dumps(data)                           # bytes
print(pickle.loads(blob))
```

pickle can store almost any Python object, including sets, class instances and nested structures, which is why ML libraries use it (and PyTorch's `torch.save` is built on it). But:

> [!DANGER]
> **Never unpickle data from an untrusted source.** A pickle can contain instructions that execute arbitrary code during `pickle.loads`. Loading a malicious `.pkl` (or an old-format model file downloaded from the internet) can take over your machine. Use JSON for data exchange; use pickle only for files you created yourself. (This is why `torch.load` now defaults to `weights_only=True`.)

| Format | Human-readable | Cross-language | Arbitrary Python objects | Safe with untrusted input |
|---|---|---|---|---|
| JSON | yes | yes | no | yes |
| CSV | yes | yes | no (flat tables of strings) | yes |
| pickle | no | no | yes | **no** |

## 6. Exam-ready answers

> [!EXAM]
> **Serialization.** Serialization is the conversion of an in-memory object into a format that can be stored or transmitted (a string or byte stream), and deserialization is the reverse. Python's `json` module converts between Python objects and JSON text using `dumps`/`dump` and `loads`/`load`; dictionaries map to JSON objects, lists and tuples to arrays, and `None`, `True` and `False` to `null`, `true` and `false`. The `csv` module reads and writes delimited tabular data, correctly handling quoting, with `reader`/`writer` for rows as lists and `DictReader`/`DictWriter` for rows as dictionaries. The `pickle` module serializes arbitrary Python objects to a binary format, but it must never be used on untrusted data because unpickling can execute arbitrary code.

## 7. Cheat sheet

| Need | Code |
|---|---|
| object → JSON text | `json.dumps(obj, indent=2)` |
| JSON text → object | `json.loads(s)` |
| JSON file | `json.dump(obj, f)` / `json.load(f)` |
| dates and other types | `default=str` |
| dataclass ↔ JSON | `json.dumps(asdict(x))` / `Cls(**json.loads(s))` |
| read CSV rows | `csv.reader(f)` with `newline=""` |
| CSV rows as dicts | `csv.DictReader(f)` |
| write CSV | `csv.DictWriter(f, fieldnames=[...])` + `writeheader()` |
| tab-separated | `delimiter="\t"` |
| Python-only private cache | `pickle` (trusted files only!) |

> [!INTERVIEW]
> **"Why not `line.split(',')` for CSV?"** Fields may contain commas, quotes and even newlines inside quotes (`"Smith, J"`, `"He said ""hi"""`). A naive split breaks those rows and silently shifts columns. That's a data-corruption bug that tests on clean sample data won't catch. The `csv` module implements the quoting rules (RFC 4180).
