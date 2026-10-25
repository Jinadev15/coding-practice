---
id: c-m4-json-dom
title: A Strict JSON Parser, DOM and Serializer
difficulty: Expert
order: 1
tags: parsing, recursive descent, tagged unions, UTF-8, dynamic memory, error reporting
time_limit: 4
---
## Statement
Robot configurations, ROS 2 parameter dumps and REST payloads are JSON. Implement a **strict RFC 8259 parser** that builds a DOM tree (tagged unions), plus path queries and a canonical serializer.

```c
typedef enum { J_NULL, J_BOOL, J_NUM, J_STR, J_ARR, J_OBJ } JType;
typedef struct Json Json;                            /* opaque node */
```

| Function | Contract |
|---|---|
| `Json *json_parse(const char *text, int *err_pos)` | The whole text must be exactly one JSON value, with optional surrounding whitespace (space, `\t`, `\n`, `\r`). Returns NULL on error and sets `*err_pos` (see below). |
| `void json_free(Json *j)` | Accepts NULL. |
| `JType json_type(const Json *j)` | |
| `const Json *json_get(const Json *root, const char *path)` | Paths look like `robots[2].pose.x`. Keys are `[A-Za-z0-9_-]+`, separated by `.`, and indices are `[n]`. `""` is the root. Returns NULL for a malformed path, a missing key or index, or a type mismatch. |
| `double json_num(j)`, `int json_bool(j)`, `const char *json_str(j)`, `size_t json_len(j)` | `json_len`: the element count of an array or object, or the byte length of a string. Strings may contain `\u0000`. |
| `char *json_dump(const Json *j, int sorted)` | Compact canonical text in a new `malloc` buffer. Objects keep insertion order, or sort keys by bytes when `sorted`. **Duplicate keys: the last value wins, at the position of the first occurrence.** |

**Grammar details**
- Numbers follow `-?(0|[1-9][0-9]*)(\.[0-9]+)?([eE][+-]?[0-9]+)?`.
- Strings support escapes `\" \\ \/ \b \f \n \r \t \uXXXX`. Surrogate pairs combine, and the result is stored as **UTF-8**. A lone surrogate is an error.
- Raw bytes `< 0x20` inside strings are errors. Other bytes are copied as-is.
- Nesting deeper than **512** is an error.

**`err_pos` rules**
- An unexpected character gives its offset, and an unexpected end of input gives `strlen(text)`.
- A bad escape (unknown letter, a bad hex digit, or an invalid or lone surrogate) gives the offset of the **backslash** that starts that escape. For a high surrogate not followed by a low one, that's the high surrogate's backslash.
- Exceeding the depth limit gives the offset of the bracket that exceeds it.

**`json_dump` output**
- Separators are `,` and `:` with no spaces.
- A number that's integral with magnitude below 1e15 prints as an integer (`-0` prints `0`). Otherwise use `%.17g`.
- Strings escape `"`, `\`, `\b \f \n \r \t`, and other bytes below 0x20 as `\u00xx` (lowercase hex). All other bytes are written raw.

## Starter
```c
#include <stdlib.h>
#include <string.h>

typedef enum { J_NULL, J_BOOL, J_NUM, J_STR, J_ARR, J_OBJ } JType;
typedef struct Json { JType t; double num; } Json;

Json *json_parse(const char *text, int *err_pos) {
    Json *j = calloc(1, sizeof *j);
    j->t = J_NUM; j->num = atof(text); *err_pos = -1;
    return j;
}
void json_free(Json *j) { free(j); }
JType json_type(const Json *j) { return j->t; }
const Json *json_get(const Json *root, const char *path) { return *path ? NULL : root; }
double json_num(const Json *j) { return j->num; }
int json_bool(const Json *j) { (void)j; return 0; }
const char *json_str(const Json *j) { (void)j; return ""; }
size_t json_len(const Json *j) { (void)j; return 0; }
char *json_dump(const Json *j, int sorted) { (void)j; (void)sorted; char *s = malloc(5); strcpy(s, "null"); return s; }
```

## Driver
```c
#include <stdio.h>

static void parse_show(const char *label, const char *text, int sorted) {
    int pos = -7;
    Json *j = json_parse(text, &pos);
    if (!j) { printf("%s: error at %d\n", label, pos); return; }
    char *s = json_dump(j, sorted);
    printf("%s: %s\n", label, s);
    free(s); json_free(j);
}

int main(void) {
    char cmd[16];
    while (scanf("%15s", cmd) == 1) {
        if (!strcmp(cmd, "values")) {
            parse_show("scalars", " [null, true, false, 0, -0, 12, -3.5, 1e3, 2.5E-3, 123456789012345678, 0.1] ", 0);
            parse_show("strings", "[\"a\\\"b\\\\c\\/d\", \"tab\\there\\n\", \"\\u00e9\\u20ac\", \"\\ud83e\\udd16\", \"\\u0001\"]", 0);
            parse_show("object", "{\"z\": 1, \"a\": {\"y\": [1, 2, {\"k\": null}], \"b\": \"x\"}, \"m\": []}", 0);
            parse_show("sorted", "{\"z\": 1, \"a\": {\"y\": [1, 2, {\"k\": null}], \"b\": \"x\"}, \"m\": []}", 1);
            parse_show("dupkeys", "{\"a\": 1, \"b\": 2, \"a\": 3}", 0);
            parse_show("empty", "  {}  ", 0);
            parse_show("nested", "[[[[[]]]],{}]", 0);
        } else if (!strcmp(cmd, "errors")) {
            const char *bad[] = {"", "   ", "[1,]", "[1 2]", "{\"a\" 1}", "{a:1}", "01", "-", "1.", "1e", "+1", "tru", "nulls",
                                 "\"abc", "\"a\\x\"", "\"\\u12G4\"", "\"\\ud800\"", "\"\\udc00x\"", "\"\\ud800\\u0041\"", "\"a\tb\"", "[1]]", "{\"a\":1,}", "\"\\"};
            for (int i = 0; i < 23; i++) { char label[16]; snprintf(label, sizeof label, "bad%02d", i); parse_show(label, bad[i], 0); }
            static char deep[2000]; memset(deep, '[', 513); memset(deep + 513, ']', 513); deep[1026] = 0;
            parse_show("depth513", deep, 0);
            memset(deep, '[', 512); memset(deep + 512, ']', 512); deep[1024] = 0;
            int pos; Json *j = json_parse(deep, &pos); printf("depth512: %s\n", j ? "ok" : "error"); json_free(j);
        } else if (!strcmp(cmd, "query")) {
            const char *cfg = "{\"robot\": {\"name\": \"rover\", \"wheels\": 4, \"sensors\": [{\"type\": \"lidar\", \"rate\": 10.5},"
                              " {\"type\": \"imu\", \"rate\": 200}], \"enabled\": true, \"id\": \"a\\u0000b\"}, \"list\": [[1, 2], [3]]}";
            int pos; Json *j = json_parse(cfg, &pos);
            const char *paths[] = {"robot.name", "robot.wheels", "robot.sensors[1].rate", "robot.sensors[0].type", "robot.enabled",
                                   "list[0][1]", "list[1]", "robot.sensors[2]", "robot.missing", "robot..name", "robot.name[0]", "list[x]", "", "robot.id"};
            for (int i = 0; i < 14; i++) {
                const Json *n = json_get(j, paths[i]);
                printf("%-22s ", paths[i][0] ? paths[i] : "<root>");
                if (!n) { printf("NULL\n"); continue; }
                switch (json_type(n)) {
                case J_STR: printf("str len=%zu '%s'\n", json_len(n), json_str(n)); break;
                case J_NUM: printf("num %g\n", json_num(n)); break;
                case J_BOOL: printf("bool %d\n", json_bool(n)); break;
                case J_ARR: printf("array len=%zu\n", json_len(n)); break;
                case J_OBJ: printf("object len=%zu\n", json_len(n)); break;
                default: printf("null\n");
                }
            }
            json_free(j); json_free(NULL);
        } else if (!strcmp(cmd, "big")) {
            size_t cap = 16000000, n = 0; char *buf = malloc(cap);
            n += (size_t)sprintf(buf + n, "{\"points\": [");
            unsigned x = 9;
            for (int i = 0; i < 100000; i++) {
                x = x * 1103515245u + 12345u;
                n += (size_t)sprintf(buf + n, "%s{\"id\": %d, \"x\": %d.%02u, \"tag\": \"p\\u00e9%u\", \"ok\": %s}", i ? ", " : "", i, (int)(x >> 20) - 2048, (x >> 4) % 100, x % 997, (x & 1) ? "true" : "false");
            }
            n += (size_t)sprintf(buf + n, "], \"meta\": {\"count\": 100000}}");
            int pos; Json *j = json_parse(buf, &pos);
            char *out = json_dump(j, 1);
            Json *again = json_parse(out, &pos);
            char *out2 = json_dump(again, 1);
            double sum = 0; char path[64];
            for (int i = 0; i < 100000; i += 997) { snprintf(path, sizeof path, "points[%d].x", i); sum += json_num(json_get(j, path)); }
            printf("len %zu roundtrip %d count %g sum %.2f tag %s\n", strlen(out), strcmp(out, out2) == 0, json_num(json_get(j, "meta.count")), sum, json_str(json_get(j, "points[99999].tag")));
            free(out); free(out2); json_free(j); json_free(again); free(buf);
        }
    }
    return 0;
}
```

## Tests
=== sample
values
---
scalars: [null,true,false,0,0,12,-3.5,1000,0.0025000000000000001,1.2345678901234568e+17,0.10000000000000001]
strings: ["a\"b\\c/d","tab\there\n","é€","🤖","\u0001"]
object: {"z":1,"a":{"y":[1,2,{"k":null}],"b":"x"},"m":[]}
sorted: {"a":{"b":"x","y":[1,2,{"k":null}]},"m":[],"z":1}
dupkeys: {"a":3,"b":2}
empty: {}
nested: [[[[[]]]],{}]
=== hidden
errors
---
bad00: error at 0
bad01: error at 3
bad02: error at 3
bad03: error at 3
bad04: error at 5
bad05: error at 1
bad06: error at 1
bad07: error at 1
bad08: error at 2
bad09: error at 2
bad10: error at 0
bad11: error at 3
bad12: error at 4
bad13: error at 4
bad14: error at 2
bad15: error at 1
bad16: error at 1
bad17: error at 1
bad18: error at 1
bad19: error at 2
bad20: error at 3
bad21: error at 7
bad22: error at 2
depth513: error at 512
depth512: ok
=== hidden
query
---
robot.name             str len=5 'rover'
robot.wheels           num 4
robot.sensors[1].rate  num 200
robot.sensors[0].type  str len=5 'lidar'
robot.enabled          bool 1
list[0][1]             num 2
list[1]                array len=1
robot.sensors[2]       NULL
robot.missing          NULL
robot..name            NULL
robot.name[0]          NULL
list[x]                NULL
<root>                 object len=2
robot.id               str len=3 'a'
=== hidden
big
---
len 5803373 roundtrip 1 count 100000 sum -15527.02 tag pé502

## Hints
- Node: `struct Json { JType t; double num; int b; char *s; size_t slen; Json **items; char **keys; size_t *klens; size_t n, cap; }`. Use one struct for all types, with the fields used according to `t`.
- Parser state: `{ const char *s; size_t i, len; int err; size_t err_pos; int depth; }`. Write `parse_value`, `parse_string`, `parse_number`, `parse_array` and `parse_object`, and record the **first** error position only.
- Strings: a growable byte buffer. For `\uXXXX`: if it's a high surrogate (D800–DBFF), it must be followed by `\u` with a low surrogate (DC00–DFFF). Then combine `0x10000 + ((hi - 0xD800) << 10) + (lo - 0xDC00)`, and encode as UTF-8 in 1–4 bytes.
- Numbers: check the grammar by hand while scanning, then convert with `strtod` on the validated slice.
- Duplicate keys: when inserting into an object, search for an existing key first, and replace its value in place.

## Solution
```c
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef enum { J_NULL, J_BOOL, J_NUM, J_STR, J_ARR, J_OBJ } JType;
typedef struct Json Json;
struct Json {
    JType t;
    double num;
    int b;
    char *s; size_t slen;                 /* J_STR */
    Json **items; char **keys; size_t *klens; size_t n, cap;   /* J_ARR / J_OBJ */
};

typedef struct { const char *s; size_t i, len; int err; size_t err_pos; int depth; } P;

static void fail(P *p, size_t pos) { if (!p->err) { p->err = 1; p->err_pos = pos; } }
static void skip_ws(P *p) { while (p->i < p->len && strchr(" \t\n\r", p->s[p->i]) && p->s[p->i]) p->i++; }

void json_free(Json *j) {
    if (!j) return;
    for (size_t k = 0; k < j->n; k++) { json_free(j->items[k]); if (j->keys) free(j->keys[k]); }
    free(j->items); free(j->keys); free(j->klens); free(j->s);
    free(j);
}

static Json *node(JType t) { Json *j = calloc(1, sizeof *j); if (j) j->t = t; return j; }

typedef struct { char *d; size_t n, cap; } Buf;
static int buf_put(Buf *b, const char *src, size_t k) {
    if (b->n + k + 1 > b->cap) {
        size_t nc = (b->cap ? b->cap * 2 : 32); while (nc < b->n + k + 1) nc *= 2;
        char *nd = realloc(b->d, nc); if (!nd) return 0;
        b->d = nd; b->cap = nc;
    }
    memcpy(b->d + b->n, src, k); b->n += k; b->d[b->n] = 0;
    return 1;
}
static void put_utf8(Buf *b, unsigned cp) {
    char u[4]; size_t k;
    if (cp < 0x80) { u[0] = (char)cp; k = 1; }
    else if (cp < 0x800) { u[0] = (char)(0xC0 | cp >> 6); u[1] = (char)(0x80 | (cp & 0x3F)); k = 2; }
    else if (cp < 0x10000) { u[0] = (char)(0xE0 | cp >> 12); u[1] = (char)(0x80 | (cp >> 6 & 0x3F)); u[2] = (char)(0x80 | (cp & 0x3F)); k = 3; }
    else { u[0] = (char)(0xF0 | cp >> 18); u[1] = (char)(0x80 | (cp >> 12 & 0x3F)); u[2] = (char)(0x80 | (cp >> 6 & 0x3F)); u[3] = (char)(0x80 | (cp & 0x3F)); k = 4; }
    buf_put(b, u, k);
}

static int hex4(P *p, size_t at, unsigned *out) {            /* 4 hex digits starting at `at` */
    unsigned v = 0;
    for (size_t k = 0; k < 4; k++) {
        if (at + k >= p->len) return 0;
        char c = p->s[at + k];
        v <<= 4;
        if (c >= '0' && c <= '9') v |= (unsigned)(c - '0');
        else if (c >= 'a' && c <= 'f') v |= (unsigned)(c - 'a' + 10);
        else if (c >= 'A' && c <= 'F') v |= (unsigned)(c - 'A' + 10);
        else return 0;
    }
    *out = v;
    return 1;
}

static int parse_string_raw(P *p, Buf *b) {                  /* p->s[p->i] == '"' */
    p->i++;
    for (;;) {
        if (p->i >= p->len) { fail(p, p->len); return 0; }
        unsigned char c = (unsigned char)p->s[p->i];
        if (c == '"') { p->i++; if (!b->d) buf_put(b, "", 0); return 1; }
        if (c < 0x20) { fail(p, p->i); return 0; }
        if (c != '\\') { buf_put(b, (const char *)&p->s[p->i], 1); p->i++; continue; }
        size_t bs = p->i;
        if (p->i + 1 >= p->len) { fail(p, p->len); return 0; }
        char e = p->s[p->i + 1];
        const char *simple = strchr("\"\\/bfnrt", e);
        if (simple && e) {
            static const char map[] = "\"\\/\b\f\n\r\t";
            buf_put(b, &map[simple - "\"\\/bfnrt"], 1);
            p->i += 2;
            continue;
        }
        if (e != 'u') { fail(p, bs); return 0; }
        unsigned cp;
        if (!hex4(p, bs + 2, &cp)) { fail(p, bs); return 0; }
        p->i = bs + 6;
        if (cp >= 0xDC00 && cp <= 0xDFFF) { fail(p, bs); return 0; }          /* lone low surrogate */
        if (cp >= 0xD800 && cp <= 0xDBFF) {
            unsigned lo;
            if (p->i + 1 < p->len && p->s[p->i] == '\\' && p->s[p->i + 1] == 'u' && hex4(p, p->i + 2, &lo) && lo >= 0xDC00 && lo <= 0xDFFF) {
                cp = 0x10000 + ((cp - 0xD800) << 10) + (lo - 0xDC00);
                p->i += 6;
            } else { fail(p, bs); return 0; }
        }
        put_utf8(b, cp);
    }
}

static Json *parse_value(P *p);

static Json *parse_number(P *p) {
    size_t st = p->i, i = p->i;
    if (i < p->len && p->s[i] == '-') i++;
    if (i >= p->len) { fail(p, p->len); return NULL; }
    if (p->s[i] == '0') i++;
    else if (p->s[i] >= '1' && p->s[i] <= '9') while (i < p->len && p->s[i] >= '0' && p->s[i] <= '9') i++;
    else { fail(p, i); return NULL; }
    if (i < p->len && p->s[i] == '.') {
        i++;
        if (i >= p->len) { fail(p, p->len); return NULL; }
        if (p->s[i] < '0' || p->s[i] > '9') { fail(p, i); return NULL; }
        while (i < p->len && p->s[i] >= '0' && p->s[i] <= '9') i++;
    }
    if (i < p->len && (p->s[i] == 'e' || p->s[i] == 'E')) {
        i++;
        if (i < p->len && (p->s[i] == '+' || p->s[i] == '-')) i++;
        if (i >= p->len) { fail(p, p->len); return NULL; }
        if (p->s[i] < '0' || p->s[i] > '9') { fail(p, i); return NULL; }
        while (i < p->len && p->s[i] >= '0' && p->s[i] <= '9') i++;
    }
    char tmp[512]; size_t k = i - st;
    Json *j = node(J_NUM);
    if (k < sizeof tmp) { memcpy(tmp, p->s + st, k); tmp[k] = 0; j->num = strtod(tmp, NULL); }
    else { char *h = malloc(k + 1); memcpy(h, p->s + st, k); h[k] = 0; j->num = strtod(h, NULL); free(h); }
    p->i = i;
    return j;
}

static int push_item(Json *c, Json *v, char *key, size_t klen) {
    if (key) {                                                 /* duplicate key: replace in place */
        for (size_t k = 0; k < c->n; k++)
            if (c->klens[k] == klen && memcmp(c->keys[k], key, klen) == 0) { json_free(c->items[k]); c->items[k] = v; free(key); return 1; }
    }
    if (c->n == c->cap) {
        size_t nc = c->cap ? c->cap * 2 : 4;
        Json **ni = realloc(c->items, nc * sizeof *ni); if (!ni) return 0; c->items = ni;
        if (c->t == J_OBJ) {
            char **nk = realloc(c->keys, nc * sizeof *nk); if (!nk) return 0; c->keys = nk;
            size_t *nl = realloc(c->klens, nc * sizeof *nl); if (!nl) return 0; c->klens = nl;
        }
        c->cap = nc;
    }
    c->items[c->n] = v;
    if (c->t == J_OBJ) { c->keys[c->n] = key; c->klens[c->n] = klen; }
    c->n++;
    return 1;
}

static Json *parse_container(P *p, int obj) {
    size_t open = p->i;
    if (++p->depth > 512) { fail(p, open); return NULL; }
    p->i++;
    Json *c = node(obj ? J_OBJ : J_ARR);
    skip_ws(p);
    char close = obj ? '}' : ']';
    if (p->i < p->len && p->s[p->i] == close) { p->i++; p->depth--; return c; }
    for (;;) {
        char *key = NULL; size_t klen = 0;
        if (obj) {
            skip_ws(p);
            if (p->i >= p->len) { fail(p, p->len); break; }
            if (p->s[p->i] != '"') { fail(p, p->i); break; }
            Buf kb = {0};
            if (!parse_string_raw(p, &kb)) { free(kb.d); break; }
            key = kb.d; klen = kb.n;
            skip_ws(p);
            if (p->i >= p->len) { fail(p, p->len); free(key); break; }
            if (p->s[p->i] != ':') { fail(p, p->i); free(key); break; }
            p->i++;
        }
        Json *v = parse_value(p);
        if (!v) { free(key); break; }
        push_item(c, v, key, klen);
        skip_ws(p);
        if (p->i >= p->len) { fail(p, p->len); break; }
        if (p->s[p->i] == ',') { p->i++; continue; }
        if (p->s[p->i] == close) { p->i++; p->depth--; return c; }
        fail(p, p->i);
        break;
    }
    json_free(c);
    return NULL;
}

static Json *parse_literal(P *p, const char *word, JType t, int b) {
    size_t k = strlen(word);
    for (size_t q = 0; q < k; q++) {
        if (p->i + q >= p->len) { fail(p, p->len); return NULL; }
        if (p->s[p->i + q] != word[q]) { fail(p, p->i + q); return NULL; }
    }
    p->i += k;
    Json *j = node(t); j->b = b;
    return j;
}

static Json *parse_value(P *p) {
    skip_ws(p);
    if (p->i >= p->len) { fail(p, p->len); return NULL; }
    char c = p->s[p->i];
    if (c == '{' || c == '[') return parse_container(p, c == '{');
    if (c == '"') {
        Buf b = {0};
        if (!parse_string_raw(p, &b)) { free(b.d); return NULL; }
        Json *j = node(J_STR); j->s = b.d; j->slen = b.n;
        return j;
    }
    if (c == 't') return parse_literal(p, "true", J_BOOL, 1);
    if (c == 'f') return parse_literal(p, "false", J_BOOL, 0);
    if (c == 'n') return parse_literal(p, "null", J_NULL, 0);
    if (c == '-' || (c >= '0' && c <= '9')) return parse_number(p);
    fail(p, p->i);
    return NULL;
}

Json *json_parse(const char *text, int *err_pos) {
    P p = { text, 0, strlen(text), 0, 0, 0 };
    Json *j = parse_value(&p);
    if (j) {
        skip_ws(&p);
        if (p.i != p.len) { fail(&p, p.i); json_free(j); j = NULL; }
    }
    *err_pos = j ? -1 : (int)p.err_pos;
    return j;
}

JType json_type(const Json *j) { return j->t; }
double json_num(const Json *j) { return j->num; }
int json_bool(const Json *j) { return j->b; }
const char *json_str(const Json *j) { return j->s; }
size_t json_len(const Json *j) { return j->t == J_STR ? j->slen : j->n; }

const Json *json_get(const Json *root, const char *path) {
    const Json *cur = root;
    const char *s = path;
    int first = 1;
    while (*s && cur) {
        if (*s == '[') {
            s++;
            if (*s < '0' || *s > '9') return NULL;
            size_t idx = 0;
            while (*s >= '0' && *s <= '9') idx = idx * 10 + (size_t)(*s++ - '0');
            if (*s++ != ']' || cur->t != J_ARR || idx >= cur->n) return NULL;
            cur = cur->items[idx];
        } else {
            if (!first) { if (*s != '.') return NULL; s++; }
            const char *k = s;
            while ((*s >= 'a' && *s <= 'z') || (*s >= 'A' && *s <= 'Z') || (*s >= '0' && *s <= '9') || *s == '_' || *s == '-') s++;
            size_t kl = (size_t)(s - k);
            if (kl == 0 || cur->t != J_OBJ) return NULL;
            const Json *next = NULL;
            for (size_t q = 0; q < cur->n; q++)
                if (cur->klens[q] == kl && memcmp(cur->keys[q], k, kl) == 0) { next = cur->items[q]; break; }
            cur = next;
        }
        first = 0;
    }
    return cur;
}

static void dump_str(Buf *b, const char *s, size_t n) {
    buf_put(b, "\"", 1);
    for (size_t i = 0; i < n; i++) {
        unsigned char c = (unsigned char)s[i];
        char esc[8];
        switch (c) {
        case '"': buf_put(b, "\\\"", 2); break;
        case '\\': buf_put(b, "\\\\", 2); break;
        case '\b': buf_put(b, "\\b", 2); break;
        case '\f': buf_put(b, "\\f", 2); break;
        case '\n': buf_put(b, "\\n", 2); break;
        case '\r': buf_put(b, "\\r", 2); break;
        case '\t': buf_put(b, "\\t", 2); break;
        default:
            if (c < 0x20) { snprintf(esc, sizeof esc, "\\u%04x", c); buf_put(b, esc, 6); }
            else buf_put(b, (const char *)&s[i], 1);
        }
    }
    buf_put(b, "\"", 1);
}

static const Json *g_sort_obj;
static int key_cmp(const void *a, const void *bb) {
    size_t x = *(const size_t *)a, y = *(const size_t *)bb;
    size_t lx = g_sort_obj->klens[x], ly = g_sort_obj->klens[y];
    int c = memcmp(g_sort_obj->keys[x], g_sort_obj->keys[y], lx < ly ? lx : ly);
    return c ? c : (lx > ly) - (lx < ly);
}

static void dump(Buf *b, const Json *j, int sorted) {
    char tmp[64];
    switch (j->t) {
    case J_NULL: buf_put(b, "null", 4); break;
    case J_BOOL: buf_put(b, j->b ? "true" : "false", j->b ? 4 : 5); break;
    case J_NUM:
        if (j->num == floor(j->num) && fabs(j->num) < 1e15) snprintf(tmp, sizeof tmp, "%lld", (long long)j->num);
        else snprintf(tmp, sizeof tmp, "%.17g", j->num);
        buf_put(b, tmp, strlen(tmp));
        break;
    case J_STR: dump_str(b, j->s, j->slen); break;
    case J_ARR:
        buf_put(b, "[", 1);
        for (size_t k = 0; k < j->n; k++) { if (k) buf_put(b, ",", 1); dump(b, j->items[k], sorted); }
        buf_put(b, "]", 1);
        break;
    case J_OBJ: {
        size_t *order = malloc((j->n ? j->n : 1) * sizeof *order);
        for (size_t k = 0; k < j->n; k++) order[k] = k;
        if (sorted) { g_sort_obj = j; qsort(order, j->n, sizeof *order, key_cmp); }
        buf_put(b, "{", 1);
        for (size_t k = 0; k < j->n; k++) {
            if (k) buf_put(b, ",", 1);
            dump_str(b, j->keys[order[k]], j->klens[order[k]]);
            buf_put(b, ":", 1);
            dump(b, j->items[order[k]], sorted);
        }
        buf_put(b, "}", 1);
        free(order);
        break;
    }
    }
}

char *json_dump(const Json *j, int sorted) {
    Buf b = {0};
    buf_put(&b, "", 0);
    dump(&b, j, sorted);
    return b.d;
}
```

- **Recursive descent** maps each JSON production onto a function. Errors record only the *first* failure position, so the reported offset points at the real culprit rather than a downstream symptom.
- **One tagged node type** (`t` selects the meaningful fields) gives a uniform tree that frees recursively. Strings carry an explicit length, so `\u0000` survives.
- **Unicode done properly**: `\uD83E\uDD16` (🤖) is a surrogate pair combined into one code point and stored as 4-byte UTF-8. Lone surrogates are rejected rather than silently producing invalid UTF-8.
- **Strict numbers**: the grammar is checked by hand before `strtod`, because `strtod` alone would accept `+1`, `01`, `1.` and `inf`, all of which are illegal in JSON.
- **Bounded recursion**: the 512-level depth limit keeps hostile input (`[[[[…`) from overflowing the C stack, which is a real-world denial-of-service vector.
- **Canonical output** (stable number formatting, optional sorted keys) makes dumps comparable byte for byte. The 100,000-object test checks that parse → dump → parse → dump is a fixed point.
