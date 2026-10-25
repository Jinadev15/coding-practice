# Study guide: Special quiz 2

Quiz 2 is about data layout and bits: 2D buffers, binary encodings, and a tiny CPU.

## 1. Image processing on PGM files

A **PGM** (portable graymap) file is text: `P2`, then the width, height and max value, then `w*h` pixel values. Store the image in **one** contiguous buffer and index it yourself:

```c
typedef struct { int w, h, maxv; unsigned char *px; } Image;
#define AT(img, x, y) ((img)->px[(size_t)(y) * (img)->w + (x)])
```

One `malloc` instead of `h` separate rows is faster (cache-friendly) and needs only one `free`.

**Convolution** (blur, sharpen, edge detection): each output pixel is a weighted sum of its 3×3 neighbourhood:

```c
for (int y = 0; y < h; y++)
  for (int x = 0; x < w; x++) {
    int s = 0;
    for (int ky = -1; ky <= 1; ky++)
      for (int kx = -1; kx <= 1; kx++)
        s += k[ky + 1][kx + 1] * AT(src, clampi(x + kx, 0, w - 1), clampi(y + ky, 0, h - 1));
    AT(dst, x, y) = clampi(s / div, 0, maxv);
  }
```

- **Write to a separate output image.** Writing in place corrupts neighbours that you haven't read yet.
- **Borders:** clamp the coordinates (repeat the edge pixel) or follow whatever rule the statement specifies.

## 2. Delta, ZigZag and varint compression

Sensor readings change slowly: `1000, 1002, 1001, 1005`. Three tricks shrink them:

1. **Delta encoding:** store differences instead of values: `1000, +2, −1, +4`. The numbers become small.
2. **ZigZag:** map signed numbers to unsigned ones so that small magnitudes stay small: `0→0, −1→1, 1→2, −2→3, ...`

```c
uint64_t zz(int64_t v)  { return ((uint64_t)v << 1) ^ (uint64_t)(v >> 63); }
int64_t  unzz(uint64_t u) { return (int64_t)(u >> 1) ^ -(int64_t)(u & 1); }
```

3. **Varint (LEB128):** 7 bits of payload per byte. The high bit means "more bytes follow", so small numbers take a single byte.

```c
size_t put_varint(uint8_t *out, uint64_t u) {
    size_t n = 0;
    while (u >= 0x80) { out[n++] = (uint8_t)(u | 0x80); u >>= 7; }
    out[n++] = (uint8_t)u;
    return n;
}
```

When decoding, reject truncated input and varints longer than 10 bytes. Untrusted input must never make you read past the buffer.

## 3. An assembler and a stack VM

A **stack machine** has no registers. Every instruction pops its operands and pushes its result:

```text
PUSH 2      stack: [2]
PUSH 3      stack: [2, 3]
ADD         stack: [5]
```

**Two-pass assembler:**

- **Pass 1:** record each label's address (`loop:` → instruction index).
- **Pass 2:** emit the instructions and resolve label operands (`JMP loop`).

Two passes are needed because jumps can go *forward* to labels you haven't seen yet.

Encode each instruction in a struct, or pack it into bits: an opcode in the low 8 bits and the operand in the rest. A **tagged union** is a clean model:

```c
typedef enum { OP_PUSH, OP_ADD, OP_JMP, OP_JZ, OP_HALT /* ... */ } Op;
typedef struct { Op op; int32_t arg; } Instr;
```

**The VM loop:**

```c
for (;;) {
    if (pc >= n) return ERR_PC;
    Instr in = code[pc++];
    switch (in.op) {
    case OP_PUSH: if (sp == STACK_MAX) return ERR_OVERFLOW; stack[sp++] = in.arg; break;
    case OP_ADD:  if (sp < 2) return ERR_UNDERFLOW; sp--; stack[sp-1] += stack[sp]; break;
    case OP_HALT: return OK;
    /* ... */
    }
    if (++steps > MAX_STEPS) return ERR_LOOP;     /* guard against infinite loops */
}
```

Every instruction has to check for stack underflow and overflow. A VM must never crash, whatever the program tells it to do.
