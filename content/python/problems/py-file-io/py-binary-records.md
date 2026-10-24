---
id: py-binary-records
title: Fixed-Size Binary Records
difficulty: Medium
order: 3
tags: binary files, seek, bytes, int.to_bytes
---
## Statement
Sensor logs are often stored as fixed-size binary records so any record can be read directly. Implement:

- `write_records(path, values)`: write each integer as **4 bytes, little-endian, signed** (`int.to_bytes(4, "little", signed=True)`)
- `read_record(path, i)`: return the i-th value (0-based) by **seeking** to its offset, without reading the whole file
- `count_records(path)`: the number of records, from the file size (`os.path.getsize`)

## Starter
```python
import os

def write_records(path, values):
    pass

def read_record(path, i):
    pass

def count_records(path):
    pass
```

## Driver
```python
values = list(map(int, input().split()))
write_records("log.bin", values)
print(count_records("log.bin"), os.path.getsize("log.bin"))
for i in map(int, input().split()):
    print(read_record("log.bin", i))
with open("log.bin", "rb") as f:
    print(f.read(4).hex())
```

## Tests
=== sample
10 -1 300
2 0 1
---
3 12
300
10
-1
0a000000
=== hidden
2147483647 -2147483648 0
1 2 0
---
3 12
-2147483648
0
2147483647
ffffff7f

## Hints
- Write: `f.write(v.to_bytes(4, "little", signed=True))` in mode `"wb"`.
- Read: `f.seek(4 * i)`, `data = f.read(4)`, `int.from_bytes(data, "little", signed=True)`.

## Solution
Fixed-size records turn "find record i" into the arithmetic `offset = 4 * i`, so one `seek` and one 4-byte read do it in O(1).

```python
import os

SIZE = 4

def write_records(path, values):
    with open(path, "wb") as f:
        for v in values:
            f.write(v.to_bytes(SIZE, "little", signed=True))

def read_record(path, i):
    with open(path, "rb") as f:
        f.seek(SIZE * i)
        return int.from_bytes(f.read(SIZE), "little", signed=True)

def count_records(path):
    return os.path.getsize(path) // SIZE
```

10 is `0a 00 00 00` in little-endian order (least significant byte first), which is how x86 and ARM CPUs store integers in memory. The `struct` module packs whole records with several fields at once (`struct.pack("<if", id, value)`), and NumPy's `np.fromfile` reads such logs straight into arrays. This is the same layout a C program would write with `fwrite`.
