# File I/O

Files are how programs persist data: configuration, logs, datasets, model weights, robot calibration tables. Python's file API is small: `open()`, a handful of methods and the `with` statement. The details that cause real bugs are **modes**, **encodings**, **newlines** and **text vs binary**. This lesson makes those precise, so reading and writing files is never guesswork.

## 1. `open()` and modes

> [!SYNTAX]
> `open(file, mode="r", buffering=-1, encoding=None, errors=None, newline=None)`
>
> Always use it in a `with` block, so the file is closed (and flushed) even on errors.

| Mode | Meaning | If the file exists | If it doesn't |
|---|---|---|---|
| `"r"` | read (the default) | read from the start | `FileNotFoundError` |
| `"w"` | write | **truncated to empty!** | created |
| `"a"` | append | writes go to the end | created |
| `"x"` | exclusive create | `FileExistsError` | created |
| `"r+"` | read and write | start at 0, no truncation | `FileNotFoundError` |
| `"w+"` / `"a+"` | read and write variants | truncate / append | created |
| add `"b"` | **binary**: bytes in, bytes out (`"rb"`, `"wb"`) | | |
| add `"t"` | text (the default): `str` in, `str` out | | |

> [!DANGER]
> `"w"` **erases** the file the moment it's opened, before you write anything. Opening the wrong path with `"w"` destroys data. Use `"x"` when you mean "create a new file, and never overwrite".

## 2. Always specify `encoding` for text files

```python
with open("notes.txt", "w", encoding="utf-8") as f:
    f.write("héllo\n")
with open("notes.txt", encoding="utf-8") as f:
    print(f.read())
```

Without `encoding=`, Python uses the platform default. That's usually UTF-8 on Linux and macOS, but has historically been a legacy code page on Windows, so the same script can work on one machine and produce mojibake (`hÃ©llo`) or `UnicodeDecodeError` on another. (Python 3.15 will make UTF-8 the default everywhere; until then, be explicit.)

## 3. Reading

| Method | Returns | Memory |
|---|---|---|
| `f.read()` | the entire file as one `str` | O(file size) |
| `f.read(n)` | up to `n` characters (bytes in binary mode) | O(n) |
| `f.readline()` | the next line, **including** `\n` (`""` at end of file) | one line |
| `f.readlines()` | a list of all lines | O(file size) |
| `for line in f:` | lines one at a time, lazily | **one line**: the idiom |

```python
with open("data.txt", encoding="utf-8") as f:
    for line in f:                       # streaming: works for any file size
        line = line.rstrip("\n")         # lines keep their newline; strip it
        if not line:
            continue
        print(line)
```

> [!KEY]
> Lines read from a file end with `"\n"` (except possibly the last one). Forgetting to strip it causes `"abc\n" != "abc"` bugs and doubled blank lines when printing (`print` adds its own newline).

## 4. Writing

```python
lines = ["first", "second"]
with open("out.txt", "w", encoding="utf-8") as f:
    f.write("header\n")                      # returns the number of characters written
    f.writelines(l + "\n" for l in lines)    # NO newlines are added for you
    print("footer", file=f)                  # print adds the newline (and sep) for you
```

`write` doesn't add a newline. That's the most common writing bug: everything ends up on one line.

## 5. Text mode vs binary mode

| | Text (`"r"`, `"w"`) | Binary (`"rb"`, `"wb"`) |
|---|---|---|
| Data type | `str` | `bytes` |
| Encoding/decoding | automatic (with `encoding=`) | none: raw bytes |
| Newline translation | `\r\n` ↔ `\n` handled for you | none |
| Use for | `.txt`, `.csv`, `.json`, source code | images, audio, `.npy`, zip, network packets, serial data |

```python
with open("image.png", "rb") as f:
    header = f.read(8)
print(header)                        # b'\x89PNG\r\n\x1a\n'

with open("blob.bin", "wb") as f:
    f.write(bytes([0, 255, 10]))
```

Writing a `str` to a binary file (or `bytes` to a text file) raises `TypeError`.

### Newlines across platforms

Windows ends lines with `\r\n` and Unix with `\n`. In text mode, Python's **universal newlines** convert every line ending to `\n` when reading, and `\n` to the platform's ending when writing. For CSV files, pass `newline=""` and let the `csv` module handle line endings (JSON/CSV lesson).

## 6. File position: `seek` and `tell`

A file object has a current position. Reads and writes move it forward.

```python
with open("data.bin", "rb") as f:
    f.seek(100)          # jump to byte 100
    chunk = f.read(16)
    print(f.tell())      # 116
    f.seek(0)            # back to the start
```

In text mode, only `seek(0)`, `seek(0, 2)` (end of file) and positions previously returned by `tell()` are valid, because characters can be several bytes long. Random access belongs in binary mode.

## 7. Buffering and flushing

Writes are **buffered** in memory and pushed to disk in chunks, for speed. Data reaches the file when the buffer fills, on `f.flush()`, or on `close()` (which `with` does for you). If your program crashes without closing, buffered data can be lost. For logs you want to see immediately: `print(..., flush=True)`, or open with `buffering=1` (line-buffered, text mode).

## 8. Safe writing: atomic replace

Writing a config file in place is dangerous: if the program dies halfway, the file is left corrupted. The professional pattern is to write to a temporary file in the same directory, then atomically swap it in:

```python
import os

def atomic_write(path, text):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(text)
        f.flush()
        os.fsync(f.fileno())       # force it to physical disk
    os.replace(tmp, path)          # atomic on POSIX and Windows
```

Readers see either the old file or the new one, never half of each.

## 9. Common errors

| Error | Cause |
|---|---|
| `FileNotFoundError` | wrong path, or wrong working directory |
| `PermissionError` | no access rights, or a directory path |
| `IsADirectoryError` | opened a directory as a file |
| `UnicodeDecodeError` | wrong `encoding=` (or a binary file in text mode) |
| `io.UnsupportedOperation: not readable` | reading a file opened with `"w"` |
| `ValueError: I/O operation on closed file` | used `f` after its `with` block ended |

> [!TIP]
> Relative paths are resolved against the **current working directory**, not the script's location. To open a file next to your script: `Path(__file__).parent / "data.txt"` (next lesson).

## 10. Exam-ready answers

> [!EXAM]
> **File handling in Python.** Files are opened with `open(path, mode, encoding=...)`, which returns a file object. Modes include `'r'` (read), `'w'` (write, truncating any existing file), `'a'` (append), `'x'` (exclusive creation), `'+'` (read and write), and the suffixes `'t'` (text, the default) and `'b'` (binary). Text mode reads and writes `str`, decoding and encoding with the given encoding and translating newlines; binary mode reads and writes `bytes` unchanged. Data is read with `read()`, `readline()`, `readlines()` or by iterating over the file line by line, and written with `write()` or `writelines()`. Files should be opened in a `with` statement so they are closed automatically, which also flushes the write buffers.

> [!EXAM]
> **`read()` vs `readline()` vs `readlines()`.** `read()` returns the remaining contents as a single string, `readline()` returns the next line including its newline character (an empty string at end of file), and `readlines()` returns a list of all remaining lines. Iterating directly over the file object is the most memory-efficient way to process a file line by line.

## 11. Cheat sheet

| Need | Code |
|---|---|
| read the whole text | `Path(p).read_text(encoding="utf-8")` or `f.read()` |
| stream lines | `for line in f: line = line.rstrip("\n")` |
| write text | `with open(p, "w", encoding="utf-8") as f: f.write(s)` |
| append | mode `"a"` |
| never overwrite | mode `"x"` |
| binary | `"rb"` / `"wb"` with `bytes` |
| line with print | `print(x, file=f)` |
| jump | `f.seek(n)`, `f.tell()` |
| crash-safe write | write `tmp`, then `os.replace(tmp, path)` |

> [!INTERVIEW]
> **"How would you count the lines of a 100 GB log file in Python?"** Stream it: `sum(1 for _ in open(path, "rb"))`. Binary mode skips decoding, and iterating reads buffered chunks, so memory stays constant. For more speed, read big binary blocks and count `b"\n"`: `sum(chunk.count(b"\n") for chunk in iter(lambda: f.read(1 << 20), b""))`. Never `read()` or `readlines()` a file that might not fit in RAM.
