# File Handling

Programs persist data in files: logs, configuration, calibration tables, recorded sensor data, model weights. C's standard I/O library (`<stdio.h>`) works through `FILE *` **streams**, buffered handles with text and binary modes. This lesson covers opening and closing files correctly, formatted and line-based text I/O, binary I/O with `fread`/`fwrite`, random access with `fseek`/`ftell`, buffering, and the end-of-file and error checks that separate robust code from code that "usually works".

## 1. Opening and closing

```c
#include <stdio.h>

FILE *f = fopen("data.txt", "r");
if (f == NULL) {                 // ALWAYS check: missing file, permissions, wrong path...
    perror("data.txt");          // prints "data.txt: No such file or directory"
    return 1;
}
/* ... use f ... */
fclose(f);                       // flushes buffers and releases the handle
```

| Mode | Meaning | File must exist? | Truncates? |
|---|---|---|---|
| `"r"` | read | yes | no |
| `"w"` | write | no (created) | **yes** |
| `"a"` | append (every write goes to the end) | no (created) | no |
| `"r+"` | read and write | yes | no |
| `"w+"` | read and write | no | **yes** |
| `"a+"` | read and append | no | no |
| add `"b"` | binary (`"rb"`, `"wb"`) | | |
| add `"x"` (C11) | with `"w"`: fail if the file exists (`"wx"`) | | |

> [!KEY]
> On POSIX systems text and binary modes are identical. On Windows, text mode translates `\n` ↔ `\r\n` and treats Ctrl-Z as end of file, which corrupts binary data. Always use `"b"` for binary files so the code is portable. And every successful `fopen` needs exactly one `fclose`: the OS limits open files per process (`ulimit -n`, often 1024).

The standard streams `stdin`, `stdout` and `stderr` are pre-opened `FILE *`s.

## 2. Text I/O

```c
fprintf(f, "%s,%d,%.3f\n", name, id, value);     // formatted output
fputs("raw line\n", f);  fputc('x', f);

int a, b;
if (fscanf(f, "%d %d", &a, &b) != 2) { /* parse error or EOF */ }

char line[256];
while (fgets(line, sizeof line, f)) {            // reads up to size-1 chars, KEEPS the '\n'
    line[strcspn(line, "\n")] = '\0';            // strip the newline (if present)
    /* process line */
}
```

> [!WARNING]
> Mixing `fscanf` and `fgets` is a classic bug: `fscanf("%d")` leaves the rest of the line, including its `'\n'`, in the buffer, so the next `fgets` returns an "empty" line. Prefer reading whole lines with `fgets` (or POSIX `getline` for unlimited length), then parsing each line with `sscanf`/`strtol`.

```c
// POSIX getline: grows the buffer automatically, handles any line length
char *buf = NULL;
size_t cap = 0;
ssize_t n;
while ((n = getline(&buf, &cap, f)) != -1) { /* buf holds the line, n its length */ }
free(buf);
```

## 3. Detecting the end of file correctly

```c
// WRONG: feof only becomes true AFTER a read has failed, so the last line is processed twice
while (!feof(f)) { fgets(line, sizeof line, f); process(line); }

// RIGHT: test the result of the read itself
while (fgets(line, sizeof line, f)) process(line);

int c;                       // int, not char: EOF (-1) must be distinguishable from byte 0xFF
while ((c = fgetc(f)) != EOF) { ... }
if (ferror(f)) perror("read failed");   // after the loop: was it EOF or an error?
```

## 4. Binary I/O

```c
typedef struct { double t; float x, y, theta; } Sample;

Sample log[1000];
FILE *out = fopen("run.bin", "wb");
size_t written = fwrite(log, sizeof log[0], 1000, out);   // returns the number of ELEMENTS written
if (written != 1000) perror("fwrite");
fclose(out);

FILE *in = fopen("run.bin", "rb");
Sample s;
while (fread(&s, sizeof s, 1, in) == 1) { /* one record at a time */ }
fclose(in);
```

Binary is compact and fast (no formatting or parsing). But a raw struct dump depends on the machine's **endianness, padding and type sizes**, so the file isn't portable between architectures or compilers. For data exchange, serialise field by field with explicit byte order (the Telemetry Codec problem), or use a text format.

## 5. Random access

```c
fseek(f, 0, SEEK_END);          // origin: SEEK_SET (start), SEEK_CUR (current), SEEK_END (end)
long size = ftell(f);           // current position = file size here
rewind(f);                      // back to the start (also clears the error indicator)
fseek(f, 10 * (long)sizeof(Sample), SEEK_SET);   // jump to record #10 directly
```

For files over 2 GB, use the POSIX `fseeko`/`ftello` with `off_t`. Note that `long` is 32-bit on Windows.

## 6. Buffering

Streams buffer data in memory and transfer it in blocks: `stdout` is **line-buffered** on a terminal but **fully buffered** when redirected to a file or pipe, and `stderr` is **unbuffered**. So output order can differ from the code's order when both are redirected together:

```c
printf("step 1\n");          // may sit in the buffer...
fprintf(stderr, "error!\n"); // ...while this appears immediately
fflush(stdout);              // force the buffer out (also: setvbuf(stdout, NULL, _IONBF, 0))
```

A crash loses unflushed buffered data, which is why logs that must survive crashes go to `stderr` or are flushed explicitly.

## 7. Exam-ready answers

> [!EXAM]
> **File handling in C.** Files are accessed through `FILE` streams opened with `fopen(path, mode)`, which returns NULL on failure, and closed with `fclose`, which flushes buffered output. Modes select reading (`"r"`), writing with truncation (`"w"`), appending (`"a"`), update (`"+"`) and binary mode (`"b"`). Text is read and written with `fscanf`/`fprintf`, `fgets`/`fputs` and `fgetc`/`fputc`; binary data with `fread`/`fwrite`, which transfer a given number of fixed-size elements and return the number transferred. `fseek`, `ftell` and `rewind` provide random access. Input loops should test the return value of the read function rather than `feof`, which becomes true only after a read attempt fails, and `ferror` distinguishes errors from end of file. Streams are buffered, so `fflush` forces pending output to be written.

## 8. Cheat sheet

| Need | Code |
|---|---|
| open safely | `FILE *f = fopen(p, "r"); if (!f) { perror(p); ... }` |
| read lines | `while (fgets(buf, sizeof buf, f))` / `getline` |
| strip the newline | `buf[strcspn(buf, "\n")] = '\0';` |
| parse a line | `sscanf(buf, "%d,%lf", &id, &v) == 2` |
| read chars | `int c; while ((c = fgetc(f)) != EOF)` |
| binary records | `fwrite(arr, sizeof arr[0], n, f)` / `fread(...) == n` |
| file size | `fseek(f, 0, SEEK_END); ftell(f)` |
| force output | `fflush(f)` |

> [!INTERVIEW]
> **"What's wrong with `while (!feof(fp)) { fgets(buf, N, fp); puts(buf); }`?"** `feof` reports end of file only *after* a read has already hit it. After the last line is read successfully, `feof` is still false, so the loop runs once more: `fgets` fails and returns NULL, leaving `buf` unchanged, and the last line is printed twice (or garbage if the file was empty). The correct idiom tests the read itself: `while (fgets(buf, N, fp)) ...`, then checks `ferror(fp)` afterwards to distinguish an I/O error from a normal end of file.
