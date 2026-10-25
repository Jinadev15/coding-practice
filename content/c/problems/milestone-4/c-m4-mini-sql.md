---
id: c-m4-mini-sql
title: A Mini SQL Engine
difficulty: Expert
order: 2
tags: tokenizer, recursive descent, expression trees, dynamic memory, sorting, capstone
time_limit: 5
---
## Statement
Capstone: build a small in-memory SQL database, from the tokenizer to the query executor. It's the same architecture as SQLite (tokenizer → parser → AST → executor), in miniature.

API: `Db *db_open(void)`, `void db_exec(Db *db, const char *script, FILE *out)` (executes every `;`-terminated statement in `script`, writing results to `out`), and `void db_close(Db *db)`.

**Lexical rules**
- Keywords are case-insensitive: `CREATE TABLE INSERT INTO VALUES SELECT FROM WHERE ORDER BY ASC DESC LIMIT DELETE UPDATE SET AND OR NOT INT TEXT`.
- Identifiers are `[A-Za-z_][A-Za-z0-9_]*` (case-sensitive) and must not be keywords.
- Integer literals are `-?[0-9]+`. Text literals are `'...'`, with `''` standing for one quote.
- Symbols are `( ) , ; * = != <> < <= > >=`.

**Statements and their output** (one result per statement)

| Statement | Output |
|---|---|
| `CREATE TABLE t (a INT, b TEXT, ...)` | `ok` |
| `INSERT INTO t VALUES (v, ...)` | `ok` |
| `SELECT * \| a, b FROM t [WHERE e] [ORDER BY c [ASC\|DESC]] [LIMIT n]` | A header line of column names joined by `\|`, then one line per row (values joined by `\|`, text raw), then `(k rows)` |
| `DELETE FROM t [WHERE e]` | `deleted k` |
| `UPDATE t SET c = lit [, c = lit ...] [WHERE e]` | `updated k` |

- `WHERE` expressions use comparisons `column op literal`, combined with `NOT` > `AND` > `OR` (from highest precedence) and parentheses. Text compares with `strcmp`.
- Rows keep insertion order. `ORDER BY` is **stable**, and `LIMIT` applies after ordering.

**Errors**: print exactly one line, and the statement has no effect. These checks run in this order:
1. Any malformed statement, including an unterminated string, gives `error: syntax error`. Skip to the next `;`.
2. `error: no such table t`, `error: table t exists`, `error: duplicate column c`, `error: no such column c`.
3. `error: expected N values` (INSERT with the wrong count).
4. `error: type mismatch for column c` (a literal of the wrong type in INSERT, UPDATE or WHERE). Semantic checks follow source order.

Empty statements (`;`) produce no output. Text after the last `;` is ignored.

## Starter
```c
#define _POSIX_C_SOURCE 200809L   /* strdup, strcasecmp */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct Db { int dummy; } Db;

Db *db_open(void) { return calloc(1, sizeof(Db)); }
void db_exec(Db *db, const char *script, FILE *out) {
    (void)db;
    for (const char *p = script; *p; p++) if (*p == ';') fprintf(out, "ok\n");
}
void db_close(Db *db) { free(db); }
```

## Driver
```c
#include <stdio.h>
#include <string.h>

static char *read_block(void) {                       /* reads stdin lines until a line "@@" */
    size_t cap = 1 << 16, n = 0; char *buf = malloc(cap), line[4096];
    buf[0] = 0;
    while (fgets(line, sizeof line, stdin)) {
        if (!strcmp(line, "@@\n") || !strcmp(line, "@@")) break;
        size_t k = strlen(line);
        if (n + k + 1 > cap) { cap = (n + k + 1) * 2; buf = realloc(buf, cap); }
        memcpy(buf + n, line, k + 1); n += k;
    }
    return buf;
}

int main(void) {
    char cmd[32];
    while (scanf("%31s", cmd) == 1) {
        int c; while ((c = getchar()) != '\n' && c != EOF) {}
        if (!strcmp(cmd, "script")) {
            Db *db = db_open();
            char *s = read_block();
            db_exec(db, s, stdout);
            free(s); db_close(db);
        } else if (!strcmp(cmd, "big")) {
            Db *db = db_open();
            size_t cap = 4 << 20, n = 0; char *s = malloc(cap);
            n += (size_t)sprintf(s + n, "CREATE TABLE parts (id INT, kind TEXT, qty INT, cost INT);\n");
            unsigned x = 17; const char *kinds[] = {"motor", "battery", "sensor", "frame", "cable"};
            for (int i = 0; i < 20000; i++) {
                x = x * 1103515245u + 12345u;
                n += (size_t)sprintf(s + n, "INSERT INTO parts VALUES (%d, '%s', %u, %u);\n", i, kinds[(x >> 16) % 5], (x >> 8) % 50, (x >> 4) % 1000);
            }
            n += (size_t)sprintf(s + n, "UPDATE parts SET qty = 0 WHERE kind = 'cable' AND cost > 900;\n"
                                        "DELETE FROM parts WHERE qty = 0 OR (kind = 'frame' AND NOT cost < 500);\n"
                                        "SELECT id, kind, cost FROM parts WHERE kind = 'motor' AND qty >= 45 ORDER BY cost DESC LIMIT 5;\n"
                                        "SELECT kind FROM parts WHERE id < 0;\n"
                                        "SELECT * FROM parts ORDER BY qty LIMIT 3;\n");
            db_exec(db, s, stdout);
            free(s); db_close(db);
        }
    }
    return 0;
}
```

## Tests
=== sample
script
CREATE TABLE robots (id INT, name TEXT, battery INT);
INSERT INTO robots VALUES (1, 'rover', 80);
INSERT INTO robots VALUES (2, 'arm', 35);
insert into robots values (3, 'drone', 55);
INSERT INTO robots VALUES (4, 'o''brien|bot', 35);
SELECT * FROM robots;
SELECT name, battery FROM robots WHERE battery < 60 ORDER BY battery DESC;
SELECT id FROM robots WHERE NOT (battery = 35 OR name = 'rover') LIMIT 1;
@@
---
ok
ok
ok
ok
ok
id|name|battery
1|rover|80
2|arm|35
3|drone|55
4|o'brien|bot|35
(4 rows)
name|battery
drone|55
arm|35
o'brien|bot|35
(3 rows)
id
3
(1 rows)
=== hidden
script
CREATE TABLE t (a INT, b TEXT);
CREATE TABLE t (x INT);
CREATE TABLE u (x INT, x TEXT);
INSERT INTO t VALUES (1);
INSERT INTO t VALUES ('one', 'x');
INSERT INTO nope VALUES (1, 'x');
INSERT INTO t VALUES (1, 'x'), (2, 'y');
SELECT c FROM t;
SELECT a FROM t WHERE b > 5;
SELECT a FROM t WHERE a = ;
SELECT * FROM t WHERE (a = 1;
SELECT FROM t;
SELECT * FROM t LIMIT -1;
CREATE TABLE select (a INT);
;;
INSERT INTO t VALUES (-7, 'neg');
SELECT * FROM t;
UPDATE t SET b = 'z', a = 9 WHERE a < 0;
UPDATE t SET a = 'bad';
UPDATE t SET q = 1;
SELECT * FROM t;
DELETE FROM t;
SELECT * FROM t;
SELECT 'unterminated FROM t;
@@
---
ok
error: table t exists
error: duplicate column x
error: expected 2 values
error: type mismatch for column a
error: no such table nope
error: syntax error
error: no such column c
error: type mismatch for column b
error: syntax error
error: syntax error
error: syntax error
error: syntax error
error: syntax error
ok
a|b
-7|neg
(1 rows)
updated 1
error: type mismatch for column a
error: no such column q
a|b
9|z
(1 rows)
deleted 1
a|b
(0 rows)
error: syntax error
=== hidden
script
CREATE TABLE log (t INT, level TEXT, msg TEXT);
INSERT INTO log VALUES (5, 'warn', 'wheel slip');
INSERT INTO log VALUES (1, 'info', 'boot');
INSERT INTO log VALUES (3, 'error', 'lidar timeout');
INSERT INTO log VALUES (3, 'info', 'reconnected');
INSERT INTO log VALUES (2, 'warn', 'low battery');
SELECT t, level FROM log ORDER BY t;
SELECT t, msg FROM log ORDER BY t DESC LIMIT 3;
SELECT msg FROM log WHERE level != 'info' AND t >= 3 OR t = 1;
SELECT msg FROM log WHERE level <> 'info' AND (t >= 3 OR t = 1);
SELECT level FROM log ORDER BY level ASC LIMIT 0;
DELETE FROM log WHERE level = 'info';
UPDATE log SET level = 'resolved' WHERE msg = 'wheel slip';
SELECT * FROM log ORDER BY level;
@@
---
ok
ok
ok
ok
ok
ok
t|level
1|info
2|warn
3|error
3|info
5|warn
(5 rows)
t|msg
5|wheel slip
3|lidar timeout
3|reconnected
(3 rows)
msg
wheel slip
boot
lidar timeout
(3 rows)
msg
wheel slip
lidar timeout
(2 rows)
level
(0 rows)
deleted 2
updated 1
t|level|msg
3|error|lidar timeout
5|resolved|wheel slip
2|warn|low battery
(3 rows)
=== hidden
big

## Hints
- Tokenize the whole script first into `{type, text, number}` tokens. An unterminated string becomes a special error token.
- Parse each statement into a small AST, then execute it. If parsing fails, print the syntax error and skip forward past the next `;` token.
- `WHERE`: build an expression tree (`AND`/`OR`/`NOT`/comparison nodes). Resolve column names to indices and check literal types in a separate semantic pass **before** executing, so a bad query changes nothing.
- `ORDER BY`: collect the matching row indices, then do a stable sort. Use merge sort, or `qsort` with the original index as a tie-breaker. Then print the first `LIMIT` rows.
- `UPDATE` must validate every assignment first, then apply them.

## Solution
```c
#define _POSIX_C_SOURCE 200809L   /* strdup, strcasecmp */
#include <ctype.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <strings.h>

/* ---------- tokens ---------- */
enum { T_EOF, T_IDENT, T_KW, T_INT, T_STR, T_SYM, T_BAD };
typedef struct { int type; char *text; long long num; } Tok;

static const char *KW[] = {"CREATE", "TABLE", "INSERT", "INTO", "VALUES", "SELECT", "FROM", "WHERE", "ORDER", "BY", "ASC", "DESC",
                           "LIMIT", "DELETE", "UPDATE", "SET", "AND", "OR", "NOT", "INT", "TEXT"};

static char *dupn(const char *s, size_t n) { char *d = malloc(n + 1); memcpy(d, s, n); d[n] = 0; return d; }

static Tok *tokenize(const char *s, size_t *count) {
    size_t cap = 64, n = 0; Tok *v = malloc(cap * sizeof *v);
    size_t i = 0;
    for (;;) {
        while (s[i] && isspace((unsigned char)s[i])) i++;
        if (n + 1 >= cap) { cap *= 2; v = realloc(v, cap * sizeof *v); }
        Tok t = { T_EOF, NULL, 0 };
        if (!s[i]) { v[n++] = t; break; }
        char c = s[i];
        if (isalpha((unsigned char)c) || c == '_') {
            size_t st = i;
            while (isalnum((unsigned char)s[i]) || s[i] == '_') i++;
            t.text = dupn(s + st, i - st);
            t.type = T_IDENT;
            for (size_t k = 0; k < sizeof KW / sizeof *KW; k++)
                if (!strcasecmp(t.text, KW[k])) { t.type = T_KW; for (char *p = t.text; *p; p++) *p = (char)toupper((unsigned char)*p); }
        } else if (isdigit((unsigned char)c) || (c == '-' && isdigit((unsigned char)s[i + 1]))) {
            size_t st = i++;
            while (isdigit((unsigned char)s[i])) i++;
            t.type = T_INT; t.text = dupn(s + st, i - st); t.num = strtoll(t.text, NULL, 10);
        } else if (c == '\'') {
            size_t cap2 = 16, m = 0; char *buf = malloc(cap2);
            i++;
            int closed = 0;
            while (s[i]) {
                if (s[i] == '\'') { if (s[i + 1] == '\'') { i += 2; c = '\''; } else { i++; closed = 1; break; } }
                else c = s[i++];
                if (m + 2 > cap2) { cap2 *= 2; buf = realloc(buf, cap2); }
                buf[m++] = c;
            }
            buf[m] = 0;
            t.type = closed ? T_STR : T_BAD; t.text = buf;
            if (!closed) { v[n++] = t; v[n++] = (Tok){ T_EOF, NULL, 0 }; break; }
        } else {
            const char *two[] = {"!=", "<>", "<=", ">="};
            int matched = 0;
            for (int k = 0; k < 4; k++) if (!strncmp(s + i, two[k], 2)) { t.type = T_SYM; t.text = dupn(two[k], 2); i += 2; matched = 1; break; }
            if (!matched) {
                if (strchr("(),;*=<>", c)) { t.type = T_SYM; t.text = dupn(&c, 1); i++; }
                else { t.type = T_BAD; t.text = dupn(&c, 1); i++; }
            }
        }
        v[n++] = t;
    }
    *count = n;
    return v;
}

/* ---------- storage ---------- */
enum { TY_INT, TY_TEXT };
typedef struct { long long i; char *s; } Val;
typedef struct { char *name; int ncol; char **cols; int *types; Val **rows; size_t nrows, cap; } Table;
typedef struct Db { Table **t; int n; } Db;

Db *db_open(void) { return calloc(1, sizeof(Db)); }

static void free_row(Table *t, Val *r) { for (int c = 0; c < t->ncol; c++) free(r[c].s); free(r); }
void db_close(Db *db) {
    if (!db) return;
    for (int k = 0; k < db->n; k++) {
        Table *t = db->t[k];
        for (size_t r = 0; r < t->nrows; r++) free_row(t, t->rows[r]);
        for (int c = 0; c < t->ncol; c++) free(t->cols[c]);
        free(t->rows); free(t->cols); free(t->types); free(t->name); free(t);
    }
    free(db->t); free(db);
}
static Table *find_table(Db *db, const char *name) { for (int k = 0; k < db->n; k++) if (!strcmp(db->t[k]->name, name)) return db->t[k]; return NULL; }
static int find_col(const Table *t, const char *name) { for (int c = 0; c < t->ncol; c++) if (!strcmp(t->cols[c], name)) return c; return -1; }

/* ---------- parser ---------- */
typedef struct { Tok *v; size_t i; int err; } Ps;
static Tok *peek(Ps *p) { return &p->v[p->i]; }
static int is_kw(Tok *t, const char *k) { return t->type == T_KW && !strcmp(t->text, k); }
static int is_sym(Tok *t, const char *s) { return t->type == T_SYM && !strcmp(t->text, s); }
static int accept_kw(Ps *p, const char *k) { if (is_kw(peek(p), k)) { p->i++; return 1; } return 0; }
static int accept_sym(Ps *p, const char *s) { if (is_sym(peek(p), s)) { p->i++; return 1; } return 0; }
static void expect_kw(Ps *p, const char *k) { if (!accept_kw(p, k)) p->err = 1; }
static void expect_sym(Ps *p, const char *s) { if (!accept_sym(p, s)) p->err = 1; }
static char *expect_ident(Ps *p) { Tok *t = peek(p); if (t->type != T_IDENT) { p->err = 1; return NULL; } p->i++; return t->text; }
static Tok *expect_lit(Ps *p) { Tok *t = peek(p); if (t->type != T_INT && t->type != T_STR) { p->err = 1; return NULL; } p->i++; return t; }

enum { E_CMP, E_AND, E_OR, E_NOT };
enum { OP_EQ, OP_NE, OP_LT, OP_LE, OP_GT, OP_GE };
typedef struct Expr { int kind, op, col; char *colname; Tok *lit; struct Expr *a, *b; } Expr;

static void free_expr(Expr *e) { if (e) { free_expr(e->a); free_expr(e->b); free(e); } }
static Expr *parse_or(Ps *p);
static Expr *parse_primary(Ps *p) {
    if (p->err) return NULL;
    if (accept_kw(p, "NOT")) { Expr *e = calloc(1, sizeof *e); e->kind = E_NOT; e->a = parse_primary(p); return e; }
    if (accept_sym(p, "(")) { Expr *e = parse_or(p); expect_sym(p, ")"); return e; }
    Expr *e = calloc(1, sizeof *e); e->kind = E_CMP;
    e->colname = expect_ident(p);
    Tok *t = peek(p);
    static const char *ops[] = {"=", "!=", "<", "<=", ">", ">="};
    e->op = -1;
    if (t->type == T_SYM) {
        if (!strcmp(t->text, "<>")) e->op = OP_NE;
        for (int k = 0; k < 6; k++) if (!strcmp(t->text, ops[k])) e->op = k;
    }
    if (e->op < 0) p->err = 1; else p->i++;
    e->lit = expect_lit(p);
    return e;
}
static Expr *parse_and(Ps *p) {
    Expr *e = parse_primary(p);
    while (!p->err && accept_kw(p, "AND")) { Expr *n = calloc(1, sizeof *n); n->kind = E_AND; n->a = e; n->b = parse_primary(p); e = n; }
    return e;
}
static Expr *parse_or(Ps *p) {
    Expr *e = parse_and(p);
    while (!p->err && accept_kw(p, "OR")) { Expr *n = calloc(1, sizeof *n); n->kind = E_OR; n->a = e; n->b = parse_and(p); e = n; }
    return e;
}

/* semantic check: resolve columns and check types; returns error message buffer or NULL */
static int check_expr(Expr *e, const Table *t, char *msg) {
    if (!e) return 1;
    if (e->kind == E_CMP) {
        e->col = find_col(t, e->colname);
        if (e->col < 0) { sprintf(msg, "no such column %s", e->colname); return 0; }
        if ((t->types[e->col] == TY_INT) != (e->lit->type == T_INT)) { sprintf(msg, "type mismatch for column %s", e->colname); return 0; }
        return 1;
    }
    return check_expr(e->a, t, msg) && check_expr(e->b, t, msg);
}
static int eval(const Expr *e, const Table *t, const Val *row) {
    if (!e) return 1;
    switch (e->kind) {
    case E_AND: return eval(e->a, t, row) && eval(e->b, t, row);
    case E_OR: return eval(e->a, t, row) || eval(e->b, t, row);
    case E_NOT: return !eval(e->a, t, row);
    }
    int c = t->types[e->col] == TY_INT ? (row[e->col].i > e->lit->num) - (row[e->col].i < e->lit->num) : strcmp(row[e->col].s, e->lit->text);
    switch (e->op) {
    case OP_EQ: return c == 0; case OP_NE: return c != 0; case OP_LT: return c < 0;
    case OP_LE: return c <= 0; case OP_GT: return c > 0; default: return c >= 0;
    }
}

static const Table *g_sort_table; static int g_sort_col, g_sort_desc;
typedef struct { Val *row; size_t idx; } RowRef;
static int row_cmp(const void *x, const void *y) {
    const RowRef *a = x, *b = y;
    int c = g_sort_table->types[g_sort_col] == TY_INT
        ? (a->row[g_sort_col].i > b->row[g_sort_col].i) - (a->row[g_sort_col].i < b->row[g_sort_col].i)
        : strcmp(a->row[g_sort_col].s, b->row[g_sort_col].s);
    if (g_sort_desc) c = -c;
    return c ? c : (a->idx > b->idx) - (a->idx < b->idx);      /* stable */
}

static void print_val(FILE *out, const Table *t, const Val *row, int c) {
    if (t->types[c] == TY_INT) fprintf(out, "%lld", row[c].i); else fputs(row[c].s, out);
}

/* executes one statement starting at p->i; on syntax error sets p->err */
static void statement(Db *db, Ps *p, FILE *out) {
    char msg[128] = "";
    if (accept_kw(p, "CREATE")) {
        expect_kw(p, "TABLE"); char *name = expect_ident(p); expect_sym(p, "(");
        char *cols[64]; int types[64], nc = 0;
        do {
            if (p->err || nc == 64) { p->err = 1; break; }
            cols[nc] = expect_ident(p);
            if (accept_kw(p, "INT")) types[nc] = TY_INT; else if (accept_kw(p, "TEXT")) types[nc] = TY_TEXT; else p->err = 1;
            nc++;
        } while (!p->err && accept_sym(p, ","));
        expect_sym(p, ")"); expect_sym(p, ";");
        if (p->err) return;
        if (find_table(db, name)) { fprintf(out, "error: table %s exists\n", name); return; }
        for (int a = 0; a < nc; a++) for (int b = 0; b < a; b++) if (!strcmp(cols[a], cols[b])) { fprintf(out, "error: duplicate column %s\n", cols[a]); return; }
        Table *t = calloc(1, sizeof *t);
        t->name = strdup(name); t->ncol = nc; t->cols = malloc(sizeof(char *) * (size_t)nc); t->types = malloc(sizeof(int) * (size_t)nc);
        for (int c = 0; c < nc; c++) { t->cols[c] = strdup(cols[c]); t->types[c] = types[c]; }
        db->t = realloc(db->t, sizeof *db->t * (size_t)(db->n + 1)); db->t[db->n++] = t;
        fprintf(out, "ok\n");
    } else if (accept_kw(p, "INSERT")) {
        expect_kw(p, "INTO"); char *name = expect_ident(p); expect_kw(p, "VALUES"); expect_sym(p, "(");
        Tok *vals[64]; int nv = 0;
        do { if (p->err || nv == 64) { p->err = 1; break; } vals[nv++] = expect_lit(p); } while (!p->err && accept_sym(p, ","));
        expect_sym(p, ")"); expect_sym(p, ";");
        if (p->err) return;
        Table *t = find_table(db, name);
        if (!t) { fprintf(out, "error: no such table %s\n", name); return; }
        if (nv != t->ncol) { fprintf(out, "error: expected %d values\n", t->ncol); return; }
        for (int c = 0; c < nv; c++)
            if ((t->types[c] == TY_INT) != (vals[c]->type == T_INT)) { fprintf(out, "error: type mismatch for column %s\n", t->cols[c]); return; }
        Val *row = calloc((size_t)t->ncol, sizeof *row);
        for (int c = 0; c < nv; c++) { if (t->types[c] == TY_INT) row[c].i = vals[c]->num; else row[c].s = strdup(vals[c]->text); }
        if (t->nrows == t->cap) { t->cap = t->cap ? t->cap * 2 : 16; t->rows = realloc(t->rows, sizeof *t->rows * t->cap); }
        t->rows[t->nrows++] = row;
        fprintf(out, "ok\n");
    } else if (accept_kw(p, "SELECT")) {
        char *sel[64]; int ns = 0, star = 0;
        if (accept_sym(p, "*")) star = 1;
        else do { if (p->err || ns == 64) { p->err = 1; break; } sel[ns++] = expect_ident(p); } while (!p->err && accept_sym(p, ","));
        expect_kw(p, "FROM"); char *name = expect_ident(p);
        Expr *where = NULL; char *ocol = NULL; int desc = 0; long long limit = -1;
        if (!p->err && accept_kw(p, "WHERE")) where = parse_or(p);
        if (!p->err && accept_kw(p, "ORDER")) { expect_kw(p, "BY"); ocol = expect_ident(p); if (!accept_kw(p, "ASC") && accept_kw(p, "DESC")) desc = 1; }
        if (!p->err && accept_kw(p, "LIMIT")) { Tok *l = peek(p); if (l->type != T_INT || l->num < 0) p->err = 1; else { limit = l->num; p->i++; } }
        expect_sym(p, ";");
        if (p->err) { free_expr(where); return; }
        Table *t = find_table(db, name);
        int idx[64], nidx = 0, oc = -1;
        if (!t) { fprintf(out, "error: no such table %s\n", name); free_expr(where); return; }
        if (star) { for (int c = 0; c < t->ncol; c++) idx[nidx++] = c; }
        else for (int k = 0; k < ns; k++) { idx[nidx] = find_col(t, sel[k]); if (idx[nidx] < 0) { fprintf(out, "error: no such column %s\n", sel[k]); free_expr(where); return; } nidx++; }
        if (!check_expr(where, t, msg)) { fprintf(out, "error: %s\n", msg); free_expr(where); return; }
        if (ocol && (oc = find_col(t, ocol)) < 0) { fprintf(out, "error: no such column %s\n", ocol); free_expr(where); return; }
        RowRef *m = malloc(sizeof *m * (t->nrows ? t->nrows : 1)); size_t nm = 0;
        for (size_t r = 0; r < t->nrows; r++) if (eval(where, t, t->rows[r])) { m[nm].row = t->rows[r]; m[nm].idx = r; nm++; }
        if (oc >= 0) { g_sort_table = t; g_sort_col = oc; g_sort_desc = desc; qsort(m, nm, sizeof *m, row_cmp); }
        if (limit >= 0 && (size_t)limit < nm) nm = (size_t)limit;
        for (int k = 0; k < nidx; k++) fprintf(out, "%s%s", k ? "|" : "", t->cols[idx[k]]);
        fputc('\n', out);
        for (size_t r = 0; r < nm; r++) { for (int k = 0; k < nidx; k++) { if (k) fputc('|', out); print_val(out, t, m[r].row, idx[k]); } fputc('\n', out); }
        fprintf(out, "(%zu rows)\n", nm);
        free(m); free_expr(where);
    } else if (accept_kw(p, "DELETE")) {
        expect_kw(p, "FROM"); char *name = expect_ident(p);
        Expr *where = NULL;
        if (!p->err && accept_kw(p, "WHERE")) where = parse_or(p);
        expect_sym(p, ";");
        if (p->err) { free_expr(where); return; }
        Table *t = find_table(db, name);
        if (!t) { fprintf(out, "error: no such table %s\n", name); free_expr(where); return; }
        if (!check_expr(where, t, msg)) { fprintf(out, "error: %s\n", msg); free_expr(where); return; }
        size_t w = 0, del = 0;
        for (size_t r = 0; r < t->nrows; r++) { if (eval(where, t, t->rows[r])) { free_row(t, t->rows[r]); del++; } else t->rows[w++] = t->rows[r]; }
        t->nrows = w;
        fprintf(out, "deleted %zu\n", del);
        free_expr(where);
    } else if (accept_kw(p, "UPDATE")) {
        char *name = expect_ident(p); expect_kw(p, "SET");
        char *acol[64]; Tok *aval[64]; int na = 0;
        do { if (p->err || na == 64) { p->err = 1; break; } acol[na] = expect_ident(p); expect_sym(p, "="); aval[na] = expect_lit(p); na++; } while (!p->err && accept_sym(p, ","));
        Expr *where = NULL;
        if (!p->err && accept_kw(p, "WHERE")) where = parse_or(p);
        expect_sym(p, ";");
        if (p->err) { free_expr(where); return; }
        Table *t = find_table(db, name);
        if (!t) { fprintf(out, "error: no such table %s\n", name); free_expr(where); return; }
        int ac[64];
        for (int k = 0; k < na; k++) {
            ac[k] = find_col(t, acol[k]);
            if (ac[k] < 0) { fprintf(out, "error: no such column %s\n", acol[k]); free_expr(where); return; }
            if ((t->types[ac[k]] == TY_INT) != (aval[k]->type == T_INT)) { fprintf(out, "error: type mismatch for column %s\n", acol[k]); free_expr(where); return; }
        }
        if (!check_expr(where, t, msg)) { fprintf(out, "error: %s\n", msg); free_expr(where); return; }
        size_t upd = 0;
        for (size_t r = 0; r < t->nrows; r++) {
            if (!eval(where, t, t->rows[r])) continue;
            for (int k = 0; k < na; k++) {
                Val *v = &t->rows[r][ac[k]];
                if (t->types[ac[k]] == TY_INT) v->i = aval[k]->num; else { free(v->s); v->s = strdup(aval[k]->text); }
            }
            upd++;
        }
        fprintf(out, "updated %zu\n", upd);
        free_expr(where);
    } else {
        p->err = 1;
    }
}

void db_exec(Db *db, const char *script, FILE *out) {
    size_t n;
    Tok *v = tokenize(script, &n);
    Ps p = { v, 0, 0 };
    while (peek(&p)->type != T_EOF) {
        if (accept_sym(&p, ";")) continue;                     /* empty statement */
        size_t start = p.i;
        int has_semi = 0;
        for (size_t k = start; v[k].type != T_EOF; k++) if (is_sym(&v[k], ";")) { has_semi = 1; break; }
        if (!has_semi) {                                       /* trailing text without ';' is ignored... */
            for (size_t k = start; v[k].type != T_EOF; k++)
                if (v[k].type == T_BAD) { fprintf(out, "error: syntax error\n"); break; }   /* ...unless it is malformed */
            break;
        }
        p.err = 0;
        statement(db, &p, out);
        if (p.err) {
            fprintf(out, "error: syntax error\n");
            p.i = start;
            while (peek(&p)->type != T_EOF && !is_sym(peek(&p), ";")) p.i++;
            accept_sym(&p, ";");
        }
    }
    for (size_t k = 0; k < n; k++) free(v[k].text);
    free(v);
}
```

- **The classic pipeline**: a tokenizer turns text into tokens, a recursive-descent parser checks the grammar (with precedence `NOT > AND > OR` encoded in the call structure), a semantic pass resolves names and types, and the executor runs. Each stage fails cleanly with its own error class.
- **Parse fully, check, then execute**: errors are detected before any row changes, so a failed `UPDATE` (an unknown column in its third assignment, or a type mismatch in `WHERE`) leaves the table untouched. That's statement-level atomicity.
- **Error recovery** skips to the next `;`, so one bad statement doesn't derail the rest of the script, just like the SQLite shell.
- **Expression trees** evaluate `WHERE` per row with short-circuit `AND`/`OR`. The column indices are resolved once, not per row.
- **Stable ordering** uses the original row index as the final tie-breaker, so equal keys keep insertion order, which `qsort` alone doesn't guarantee.
