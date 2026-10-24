---
id: c-m2-stack-vm
title: Assembler and Virtual Machine for a Stack CPU
difficulty: Expert
order: 1
tags: parsing, structs, enums, unions, bit manipulation, dynamic memory, error handling
time_limit: 2
---
## Statement
Build a two-pass **assembler** and a **virtual machine** for a small stack CPU, like the core of the JVM or CPython's bytecode interpreter.

**Assembly language** (one instruction per line; `;` starts a comment; labels are `name:` on their own line or before an instruction; identifiers are case-sensitive):

| Instruction | Effect |
|---|---|
| `push N` | push the integer N (−2³¹..2³¹−1) |
| `pop`, `dup`, `swap`, `over` | drop the top; duplicate the top; swap the top two; copy the second element to the top |
| `add sub mul div mod` | pop b, pop a, push a op b (64-bit arithmetic; `div`/`mod` truncate toward zero; dividing by 0 is a run-time error) |
| `neg`, `not` | negate; logical not (pushes 1 if the value was 0, else 0) |
| `eq lt gt` | pop b, pop a, push 1 or 0 |
| `jmp L`, `jz L`, `jnz L` | jump to label L; pop and jump if zero / non-zero |
| `call L`, `ret` | push the return address on a separate call stack and jump / pop it and return |
| `load K`, `store K` | push memory cell K / pop into memory cell K (0 ≤ K < 256; all cells start at 0) |
| `print` | pop and print the value on its own line |
| `halt` | stop |

**Encoding.** Pass 1 records each label's address (an instruction index). Pass 2 encodes each instruction as one 64-bit word: the opcode in bits 56–63 and a signed 32-bit operand in the low 32 bits (operands of label instructions are the target addresses). Print the program as hex words before running: `0000: 0100000000000005` (address in 4 hex digits, word in 16 uppercase hex digits). Opcode numbers are given in this order starting at 1: `push pop dup swap over add sub mul div mod neg not eq lt gt jmp jz jnz call ret load store print halt`.

**Execution.** The VM decodes the words (no re-parsing of text!). The data stack holds up to 1024 values, and the call stack up to 256 return addresses. Running off the end of the program halts normally. Stop after **1 000 000 executed instructions** with `error: step limit`.

**Errors** (print one and stop; for assembly errors, print nothing else, including no hex dump):
- assembly: `asm error line N: unknown instruction 'X'`, `asm error line N: bad operand`, `asm error line N: undefined label 'X'`, `asm error line N: duplicate label 'X'`.
- run time: `error: stack underflow at PC`, `error: stack overflow at PC`, `error: division by zero at PC`, `error: bad memory address at PC`, `error: return without call at PC` (PC is the address of the faulting instruction, decimal).

Finally (after a normal halt) print `halted after S steps`.

## Starter
```c
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

int main(void) {
    char line[256];
    while (fgets(line, sizeof line, stdin)) {
    }
    return 0;
}
```

## Tests
=== sample
; compute 5! with a loop, then call a subroutine
        push 5
        store 0         ; n
        push 1
        store 1         ; acc
loop:   load 0
        jz done
        load 1
        load 0
        mul
        store 1
        load 0
        push 1
        sub
        store 0
        jmp loop
done:   load 1
        print
        push 7
        call double
        print
        halt
double: dup
        add
        ret
---
0000: 0100000000000005
0001: 1600000000000000
0002: 0100000000000001
0003: 1600000000000001
0004: 1500000000000000
0005: 110000000000000F
0006: 1500000000000001
0007: 1500000000000000
0008: 0800000000000000
0009: 1600000000000001
000A: 1500000000000000
000B: 0100000000000001
000C: 0700000000000000
000D: 1600000000000000
000E: 1000000000000004
000F: 1500000000000001
0010: 1700000000000000
0011: 0100000000000007
0012: 1300000000000015
0013: 1700000000000000
0014: 1800000000000000
0015: 0300000000000000
0016: 0600000000000000
0017: 1400000000000000
120
14
halted after 70 steps
=== hidden
push -7
push 2
div
print
push -7
push 2
mod
print
push 3
push 4
over
print
swap
print
print
push 0
not
print
push 5
neg
push -5
eq
print
---
0000: 01000000FFFFFFF9
0001: 0100000000000002
0002: 0900000000000000
0003: 1700000000000000
0004: 01000000FFFFFFF9
0005: 0100000000000002
0006: 0A00000000000000
0007: 1700000000000000
0008: 0100000000000003
0009: 0100000000000004
000A: 0500000000000000
000B: 1700000000000000
000C: 0400000000000000
000D: 1700000000000000
000E: 1700000000000000
000F: 0100000000000000
0010: 0C00000000000000
0011: 1700000000000000
0012: 0100000000000005
0013: 0B00000000000000
0014: 01000000FFFFFFFB
0015: 0D00000000000000
0016: 1700000000000000
-3
-1
3
3
4
1
1
halted after 23 steps
=== hidden
push 1
push 0
div
---
0000: 0100000000000001
0001: 0100000000000000
0002: 0900000000000000
error: division by zero at 2
=== hidden
start:
  frob 3
---
asm error line 2: unknown instruction 'frob'
=== hidden
  push 1
  jmp nowhere
---
asm error line 2: undefined label 'nowhere'
=== hidden
a: push 1
a: push 2
---
asm error line 2: duplicate label 'a'
=== hidden
push 12x
---
asm error line 1: bad operand
=== hidden
spin: jmp spin
---
0000: 1000000000000000
error: step limit
=== hidden
ret
---
0000: 1400000000000000
error: return without call at 0
=== hidden
store 256
---
0000: 1600000000000100
error: bad memory address at 0
=== hidden
rec: push 1
call rec
---
0000: 0100000000000001
0001: 1300000000000000
error: stack overflow at 1
=== hidden
add
---
0000: 0600000000000000
error: stack underflow at 0
=== hidden
push 2147483647
dup
mul
print
push -2147483648
print
---
0000: 010000007FFFFFFF
0001: 0300000000000000
0002: 0800000000000000
0003: 1700000000000000
0004: 0100000080000000
0005: 1700000000000000
4611686014132420609
-2147483648
halted after 6 steps
=== hidden
; count primes below LIMIT by trial division
        push 2
        store 0          ; n
        push 0
        store 2          ; count
outer:  load 0
        push 600
        lt
        jz finish
        load 0
        call isprime
        load 2
        add
        store 2
        load 0
        push 1
        add
        store 0
        jmp outer
finish: load 2
        print
        halt
; isprime(n): n on stack -> 1 or 0
isprime: store 10
        push 2
        store 11         ; d
iloop:  load 11
        load 11
        mul
        load 10
        gt
        jnz yes
        load 10
        load 11
        mod
        jz no
        load 11
        push 1
        add
        store 11
        jmp iloop
yes:    push 1
        ret
no:     push 0
        ret
---
0000: 0100000000000002
0001: 1600000000000000
0002: 0100000000000000
0003: 1600000000000002
0004: 1500000000000000
0005: 0100000000000258
0006: 0E00000000000000
0007: 1100000000000012
0008: 1500000000000000
0009: 1300000000000015
000A: 1500000000000002
000B: 0600000000000000
000C: 1600000000000002
000D: 1500000000000000
000E: 0100000000000001
000F: 0600000000000000
0010: 1600000000000000
0011: 1000000000000004
0012: 1500000000000002
0013: 1700000000000000
0014: 1800000000000000
0015: 160000000000000A
0016: 0100000000000002
0017: 160000000000000B
0018: 150000000000000B
0019: 150000000000000B
001A: 0800000000000000
001B: 150000000000000A
001C: 0F00000000000000
001D: 1200000000000027
001E: 150000000000000A
001F: 150000000000000B
0020: 0A00000000000000
0021: 1100000000000029
0022: 150000000000000B
0023: 0100000000000001
0024: 0600000000000000
0025: 160000000000000B
0026: 1000000000000018
0027: 0100000000000001
0028: 1400000000000000
0029: 0100000000000000
002A: 1400000000000000
109
halted after 49692 steps

## Hints
- Represent decoded instructions as a struct `{uint8_t op; int32_t arg;}` while assembling, then pack them: `((uint64_t)op << 56) | (uint32_t)arg`. Decode with `op = w >> 56` and `arg = (int32_t)(uint32_t)(w & 0xFFFFFFFF)`.
- Pass 1 tokenises each line: strip the comment, peel off a `label:` if present, and count instructions to assign addresses. Store the label names and addresses in a dynamic array. Pass 2 parses the operands and resolves labels, reporting undefined ones at the line that uses them.
- Keep the source lines in memory (a growable array of strings) so you can run both passes.
- The interpreter is a `switch (op)` inside a loop. Check stack depth **before** each pop or push, and report the PC of the current instruction.
- Use `int64_t` for stack values, so `2147483647 * 2147483647` doesn't overflow.

## Solution
```c
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include <errno.h>

enum { OP_PUSH = 1, OP_POP, OP_DUP, OP_SWAP, OP_OVER, OP_ADD, OP_SUB, OP_MUL, OP_DIV, OP_MOD,
       OP_NEG, OP_NOT, OP_EQ, OP_LT, OP_GT, OP_JMP, OP_JZ, OP_JNZ, OP_CALL, OP_RET,
       OP_LOAD, OP_STORE, OP_PRINT, OP_HALT, OP_COUNT };
static const char *names[OP_COUNT] = {"", "push", "pop", "dup", "swap", "over", "add", "sub", "mul",
    "div", "mod", "neg", "not", "eq", "lt", "gt", "jmp", "jz", "jnz", "call", "ret", "load", "store",
    "print", "halt"};

typedef struct { char *name; int addr; } Label;
typedef struct { char **lines; int n, cap; } Lines;

static void *xrealloc(void *p, size_t n) { void *q = realloc(p, n); if (!q) { perror("realloc"); exit(1); } return q; }

/* splits a line into an optional label, mnemonic and operand (in place). returns 0 if the line is empty */
static int split(char *s, char **label, char **mn, char **arg) {
    char *c = strchr(s, ';');
    if (c) *c = '\0';
    *label = *mn = *arg = NULL;
    char *tok[3];
    int nt = 0;
    for (char *t = strtok(s, " \t\r\n"); t && nt < 3; t = strtok(NULL, " \t\r\n")) tok[nt++] = t;
    int i = 0;
    if (nt > 0 && tok[0][strlen(tok[0]) - 1] == ':') { tok[0][strlen(tok[0]) - 1] = '\0'; *label = tok[0]; i = 1; }
    if (i < nt) *mn = tok[i++];
    if (i < nt) *arg = tok[i++];
    return *label || *mn;
}

static int opcode_of(const char *mn) {
    for (int k = 1; k < OP_COUNT; k++) if (strcmp(names[k], mn) == 0) return k;
    return 0;
}
static int takes_label(int op) { return op == OP_JMP || op == OP_JZ || op == OP_JNZ || op == OP_CALL; }
static int takes_int(int op) { return op == OP_PUSH || op == OP_LOAD || op == OP_STORE; }

int main(void) {
    Lines src = {0};
    char buf[256];
    while (fgets(buf, sizeof buf, stdin)) {
        if (src.n == src.cap) { src.cap = src.cap ? src.cap * 2 : 64; src.lines = xrealloc(src.lines, (size_t)src.cap * sizeof *src.lines); }
        src.lines[src.n] = malloc(strlen(buf) + 1);
        strcpy(src.lines[src.n++], buf);
    }

    Label *labels = NULL;
    int nlabels = 0, addr = 0;
    char tmp[256], *label, *mn, *arg;
    for (int i = 0; i < src.n; i++) {                        /* pass 1: labels */
        strcpy(tmp, src.lines[i]);
        if (!split(tmp, &label, &mn, &arg)) continue;
        if (label) {
            for (int k = 0; k < nlabels; k++)
                if (strcmp(labels[k].name, label) == 0) { printf("asm error line %d: duplicate label '%s'\n", i + 1, label); return 0; }
            labels = xrealloc(labels, (size_t)(nlabels + 1) * sizeof *labels);
            labels[nlabels].name = malloc(strlen(label) + 1);
            strcpy(labels[nlabels].name, label);
            labels[nlabels++].addr = addr;
        }
        if (mn) addr++;
    }

    uint64_t *code = malloc((size_t)(addr ? addr : 1) * sizeof *code);
    int n = 0;
    for (int i = 0; i < src.n; i++) {                        /* pass 2: encode */
        strcpy(tmp, src.lines[i]);
        if (!split(tmp, &label, &mn, &arg) || !mn) continue;
        int op = opcode_of(mn);
        if (!op) { printf("asm error line %d: unknown instruction '%s'\n", i + 1, mn); return 0; }
        int64_t val = 0;
        if (takes_label(op)) {
            if (!arg) { printf("asm error line %d: bad operand\n", i + 1); return 0; }
            int found = -1;
            for (int k = 0; k < nlabels; k++) if (strcmp(labels[k].name, arg) == 0) found = labels[k].addr;
            if (found < 0) { printf("asm error line %d: undefined label '%s'\n", i + 1, arg); return 0; }
            val = found;
        } else if (takes_int(op)) {
            char *end;
            errno = 0;
            if (!arg) { printf("asm error line %d: bad operand\n", i + 1); return 0; }
            val = strtoll(arg, &end, 10);
            if (*end || end == arg || errno || val < INT32_MIN || val > INT32_MAX) { printf("asm error line %d: bad operand\n", i + 1); return 0; }
        } else if (arg) {
            printf("asm error line %d: bad operand\n", i + 1);
            return 0;
        }
        code[n++] = ((uint64_t)op << 56) | (uint32_t)(int32_t)val;
    }
    for (int i = 0; i < n; i++) printf("%04X: %016llX\n", (unsigned)i, (unsigned long long)code[i]);

    int64_t stack[1024], mem[256] = {0};
    int calls[256], sp = 0, csp = 0;
    long steps = 0;
    int pc = 0;
#define NEED(k) do { if (sp < (k)) { printf("error: stack underflow at %d\n", pc); return 0; } } while (0)
#define ROOM(k) do { if (sp + (k) > 1024) { printf("error: stack overflow at %d\n", pc); return 0; } } while (0)
    while (pc < n) {
        if (steps++ >= 1000000) { printf("error: step limit\n"); return 0; }
        int op = (int)(code[pc] >> 56);
        int32_t a = (int32_t)(uint32_t)(code[pc] & 0xFFFFFFFFu);
        int next = pc + 1;
        int64_t x, y;
        switch (op) {
            case OP_PUSH: ROOM(1); stack[sp++] = a; break;
            case OP_POP: NEED(1); sp--; break;
            case OP_DUP: NEED(1); ROOM(1); stack[sp] = stack[sp - 1]; sp++; break;
            case OP_SWAP: NEED(2); x = stack[sp - 1]; stack[sp - 1] = stack[sp - 2]; stack[sp - 2] = x; break;
            case OP_OVER: NEED(2); ROOM(1); stack[sp] = stack[sp - 2]; sp++; break;
            case OP_ADD: case OP_SUB: case OP_MUL: case OP_DIV: case OP_MOD:
            case OP_EQ: case OP_LT: case OP_GT:
                NEED(2);
                y = stack[--sp];
                x = stack[--sp];
                if ((op == OP_DIV || op == OP_MOD) && y == 0) { printf("error: division by zero at %d\n", pc); return 0; }
                stack[sp++] = op == OP_ADD ? x + y : op == OP_SUB ? x - y : op == OP_MUL ? x * y
                            : op == OP_DIV ? x / y : op == OP_MOD ? x % y
                            : op == OP_EQ ? x == y : op == OP_LT ? x < y : x > y;
                break;
            case OP_NEG: NEED(1); stack[sp - 1] = -stack[sp - 1]; break;
            case OP_NOT: NEED(1); stack[sp - 1] = !stack[sp - 1]; break;
            case OP_JMP: next = a; break;
            case OP_JZ: NEED(1); if (stack[--sp] == 0) next = a; break;
            case OP_JNZ: NEED(1); if (stack[--sp] != 0) next = a; break;
            case OP_CALL:
                if (csp == 256) { printf("error: stack overflow at %d\n", pc); return 0; }
                calls[csp++] = pc + 1;
                next = a;
                break;
            case OP_RET:
                if (csp == 0) { printf("error: return without call at %d\n", pc); return 0; }
                next = calls[--csp];
                break;
            case OP_LOAD: case OP_STORE:
                if (a < 0 || a >= 256) { printf("error: bad memory address at %d\n", pc); return 0; }
                if (op == OP_LOAD) { ROOM(1); stack[sp++] = mem[a]; }
                else { NEED(1); mem[a] = stack[--sp]; }
                break;
            case OP_PRINT: NEED(1); printf("%lld\n", (long long)stack[--sp]); break;
            case OP_HALT: printf("halted after %ld steps\n", steps); return 0;
        }
        pc = next;
    }
    printf("halted after %ld steps\n", steps);
    for (int i = 0; i < src.n; i++) free(src.lines[i]);
    for (int k = 0; k < nlabels; k++) free(labels[k].name);
    free(src.lines); free(labels); free(code);
    return 0;
}
```

**Milestone review: every module meets in one program.**
- **Strings and parsing (modules 3, 7–8):** comment stripping, tokenising, `label:` detection, `strtoll` with full validation.
- **Two-pass assembly:** forward references (`jz done` before `done:` exists) need the label table from pass 1. That's how every real assembler and linker resolves symbols.
- **Bit manipulation (module 6):** packing the opcode and a signed operand into one 64-bit word, and decoding with shifts and masks. The `(uint32_t)` / `(int32_t)` casts preserve negative operands.
- **Enums and arrays of structs, dynamic memory (modules 5–6):** growable source and label arrays, freed at the end.
- **Defensive execution (module 8):** every stack access is bounds-checked and reports the faulting PC, and a step limit stops infinite loops. That's the difference between a toy and a VM you can safely run untrusted programs on.
- **The fetch-decode-execute loop** with a `switch` is exactly how CPython's `ceval.c` and Lua's VM run bytecode.
