---
id: c-m4-ekf-localization
title: EKF Localization with Landmark Measurements
difficulty: Expert
order: 3
tags: robotics, extended Kalman filter, linear algebra, numerical methods, structs
time_limit: 4
compare: float
---
## Statement
Capstone in numerical robotics: implement an **Extended Kalman Filter** that localizes a differential-drive robot from noisy odometry and range-bearing observations of known landmarks. This is the classic algorithm from *Probabilistic Robotics* (Thrun, Burgard and Fox), chapter 7. The judge simulates the robot and compares your estimates numerically (tolerance 1e-6).

```c
typedef struct { double x[3]; double P[3][3]; } Ekf;     /* state [px, py, theta], covariance */
```

**`void ekf_init(Ekf *e, double px, double py, double th, double var_xy, double var_th)`**: P is diagonal `(var_xy, var_xy, var_th)`.

**`void ekf_predict(Ekf *e, double v, double w, double dt, double q_v, double q_w)`**, using the **old** θ throughout:
- Motion: `px += v·dt·cos θ`, `py += v·dt·sin θ`, `θ += w·dt`, then wrap θ into **(−π, π]**.
- `F = [[1, 0, −v·dt·sin θ], [0, 1, v·dt·cos θ], [0, 0, 1]]`.
- `G = [[dt·cos θ, 0], [dt·sin θ, 0], [0, dt]]` and `M = diag(q_v, q_w)`.
- `P ← F P Fᵀ + G M Gᵀ`.

**`int ekf_update(Ekf *e, double lx, double ly, double range, double bearing, double r_r, double r_b, double gate)`**, for a landmark at (lx, ly):
- `dx = lx − px`, `dy = ly − py`, `q = dx² + dy²`, `ẑ = (√q, wrap(atan2(dy, dx) − θ))`.
- `H = [[−dx/√q, −dy/√q, 0], [dy/q, −dx/q, −1]]`.
- Innovation `y = (range − √q, wrap(bearing − ẑ_b))`.
- `S = H P Hᵀ + diag(r_r, r_b)`.
- If `q < 1e-12` or `det S ≤ 0`, return **-1** without changing anything.
- If `yᵀ S⁻¹ y > gate`, return **1** (an outlier, rejected, no change).
- Otherwise `K = P Hᵀ S⁻¹`, `x ← x + K y` (wrap θ), and use the **Joseph form** `P ← (I − K H) P (I − K H)ᵀ + K R Kᵀ`. Return 0.

`wrap(a)` maps any angle into (−π, π]. (Note that `atan2` already lands in that range.)

## Starter
```c
#include <math.h>
#ifndef M_PI
#define M_PI 3.14159265358979323846   /* not in strict ISO C; keep this */
#endif

typedef struct { double x[3]; double P[3][3]; } Ekf;

void ekf_init(Ekf *e, double px, double py, double th, double var_xy, double var_th) {
    e->x[0] = px; e->x[1] = py; e->x[2] = th;
    for (int i = 0; i < 3; i++) for (int j = 0; j < 3; j++) e->P[i][j] = 0;
    e->P[0][0] = e->P[1][1] = var_xy; e->P[2][2] = var_th;
}
void ekf_predict(Ekf *e, double v, double w, double dt, double q_v, double q_w) {
    (void)q_v; (void)q_w;
    e->x[0] += v * dt * cos(e->x[2]); e->x[1] += v * dt * sin(e->x[2]); e->x[2] += w * dt;   /* no covariance, no wrap */
}
int ekf_update(Ekf *e, double lx, double ly, double range, double bearing, double r_r, double r_b, double gate) {
    (void)e; (void)lx; (void)ly; (void)range; (void)bearing; (void)r_r; (void)r_b; (void)gate;
    return 0;
}
```

## Driver
```c
#include <stdio.h>
#include <string.h>

static unsigned long long rs = 88172645463325252ull;
static double urand(void) { rs ^= rs << 13; rs ^= rs >> 7; rs ^= rs << 17; return ((rs >> 11) + 0.5) / 9007199254740992.0; }
static double gauss(void) { double u = urand(), v = urand(); return sqrt(-2 * log(u)) * cos(2 * M_PI * v); }
static double wrapd(double a) { while (a > M_PI) a -= 2 * M_PI; while (a <= -M_PI) a += 2 * M_PI; return a; }

static void show(const Ekf *e) {
    printf("x %.6f %.6f %.6f P %.6f %.6f %.6f %.6f\n", e->x[0], e->x[1], e->x[2], e->P[0][0], e->P[1][1], e->P[2][2], e->P[0][2]);
}

int main(void) {
    char cmd[16];
    while (scanf("%15s", cmd) == 1) {
        if (!strcmp(cmd, "predict")) {
            Ekf e; ekf_init(&e, 0, 0, 0, 0.01, 0.001);
            show(&e);
            ekf_predict(&e, 1.0, 0.5, 0.1, 0.04, 0.01); show(&e);
            for (int i = 0; i < 9; i++) ekf_predict(&e, 1.0, 0.5, 0.1, 0.04, 0.01);
            show(&e);
            Ekf w; ekf_init(&w, 0, 0, 3.0, 0.1, 0.1); ekf_predict(&w, 0, 2.0, 0.2, 0, 0);
            printf("wrapped theta %.6f\n", w.x[2]);
            ekf_predict(&w, 0, -40.0, 0.1, 0, 0); printf("wrapped theta %.6f\n", w.x[2]);
        } else if (!strcmp(cmd, "update")) {
            Ekf e; ekf_init(&e, 1.0, 2.0, 0.3, 0.25, 0.05);
            int r = ekf_update(&e, 5.0, 4.0, 4.3, 0.17, 0.01, 0.002, 9.21); printf("rc %d ", r); show(&e);
            r = ekf_update(&e, 1.0, 9.0, 7.1, 1.25, 0.01, 0.002, 9.21); printf("rc %d ", r); show(&e);
            r = ekf_update(&e, 5.0, 4.0, 40.0, 0.17, 0.01, 0.002, 9.21); printf("outlier rc %d ", r); show(&e);
            r = ekf_update(&e, e.x[0], e.x[1], 0.0, 0.0, 0.01, 0.002, 9.21); printf("degenerate rc %d\n", r);
            Ekf b; ekf_init(&b, 0, 0, M_PI - 0.01, 0.1, 0.1);
            r = ekf_update(&b, -3.0, -0.2, 3.0, -M_PI + 0.08, 0.01, 0.002, 100.0); printf("bearing wrap rc %d ", r); show(&b);
        } else if (!strcmp(cmd, "sim")) {
            int steps; if (scanf("%d", &steps) != 1) return 1;
            const double L[][2] = {{5, 5}, {-5, 5}, {-5, -5}, {5, -5}, {0, 8}, {8, 0}};
            double tx = 0, ty = -4, tth = 0;                     /* true pose */
            Ekf e; ekf_init(&e, 0.3, -4.2, 0.05, 0.1, 0.02);
            int acc = 0, rej = 0; double err2 = 0;
            const double dt = 0.1, sv = 0.05, sw = 0.02, sr = 0.1, sb = 0.03;
            for (int k = 1; k <= steps; k++) {
                double v = 1.0, w = 0.25 * sin(k * 0.01) + 0.25;
                tx += v * dt * cos(tth); ty += v * dt * sin(tth); tth = wrapd(tth + w * dt);
                double vm = v + sv * gauss(), wm = w + sw * gauss();
                ekf_predict(&e, vm, wm, dt, sv * sv, sw * sw);
                if (k % 5 == 0) {
                    for (int l = 0; l < 6; l++) {
                        double dx = L[l][0] - tx, dy = L[l][1] - ty, rr = sqrt(dx * dx + dy * dy);
                        if (rr > 9) continue;
                        double z_r = rr + sr * gauss(), z_b = wrapd(atan2(dy, dx) - tth + sb * gauss());
                        if (k % 97 == 0 && l == 0) z_r += 5.0;           /* inject outliers */
                        int rc = ekf_update(&e, L[l][0], L[l][1], z_r, z_b, sr * sr, sb * sb, 13.8);
                        if (rc == 0) acc++; else if (rc == 1) rej++;
                    }
                }
                double ex = e.x[0] - tx, ey = e.x[1] - ty;
                err2 += ex * ex + ey * ey;
                if (k % (steps / 4) == 0) { printf("k %d ", k); show(&e); }
            }
            printf("accepted %d rejected %d rms %.6f true %.6f %.6f %.6f\n", acc, rej, sqrt(err2 / steps), tx, ty, tth);
        }
    }
    return 0;
}
```

## Tests
=== sample
predict
update
---
x 0.000000 0.000000 0.000000 P 0.010000 0.010000 0.001000 0.000000
x 0.100000 0.000000 0.050000 P 0.010400 0.010010 0.001100 0.000000
x 0.964772 0.220813 0.500000 P 0.013801 0.011460 0.002000 -0.000360
wrapped theta -2.883185
wrapped theta -0.600000
rc 0 x 1.150504 2.069096 0.295076 P 0.048002 0.163163 0.011240 0.019380
rc 0 x 1.225044 1.904920 0.343094 P 0.013694 0.008639 0.001351 0.002031
outlier rc 1 x 1.225044 1.904920 0.343094 P 0.013694 0.008639 0.001351 0.002031
degenerate rc -1
bearing wrap rc 0 x 0.055367 -0.921513 -0.375981 P 0.009450 0.089857 0.011553 -0.001957
=== hidden
sim 400
---
k 100 x -0.045501 1.272773 -2.618279 P 0.000504 0.000407 0.000046 0.000009
k 200 x 2.381596 0.659253 2.265918 P 0.000433 0.000541 0.000052 -0.000045
k 300 x 1.181250 -3.781699 -0.090736 P 0.000580 0.000637 0.000062 0.000024
k 400 x 6.581593 3.304236 1.553934 P 0.000433 0.000507 0.000056 -0.000064
accepted 328 rejected 0 rms 0.055766 true 6.542796 3.311549 1.558244
=== hidden
sim 4000
---
k 1000 x -7.033738 18.385069 -1.824038 P 0.025627 0.107332 0.002054 0.002440
k 2000 x 0.045544 18.969430 1.209347 P 0.016230 0.016337 0.001033 -0.000003
k 3000 x 5.752815 11.955351 1.699402 P 0.001568 0.000916 0.000107 -0.000279
k 4000 x -0.276211 1.228203 -2.626403 P 0.000493 0.000387 0.000045 0.000009
accepted 1637 rejected 4 rms 0.103694 true -0.291160 1.226716 -2.637526

## Hints
- Write tiny helpers: `mat3_mul`, `mat3_transpose` and `wrap`. Fixed-size arrays (`double A[3][3]`) keep everything on the stack.
- `S` is 2×2: `det = S00·S11 − S01·S10`, and `S⁻¹ = [[S11, −S01], [−S10, S00]] / det`.
- `K` is 3×2, `K = (P Hᵀ) S⁻¹`. Compute `PHt = P·Hᵀ` (3×2) once and reuse it for `S = H·PHt + R`.
- `wrap(a)`: `a = fmod(a + π, 2π)`; if `a <= 0`, add 2π; then return `a − π`. This handles large angles too.
- Joseph form: with `A = I − K H` (3×3), `P = A P Aᵀ + K R Kᵀ`. It keeps P symmetric and positive semi-definite despite rounding errors.

## Solution
```c
#include <math.h>
#ifndef M_PI
#define M_PI 3.14159265358979323846   /* not in strict ISO C; keep this */
#endif

typedef struct { double x[3]; double P[3][3]; } Ekf;

static double wrap(double a) {
    a = fmod(a + M_PI, 2.0 * M_PI);
    if (a <= 0) a += 2.0 * M_PI;
    return a - M_PI;                                   /* (-pi, pi] */
}

static void mul33(const double A[3][3], const double B[3][3], double C[3][3]) {
    double T[3][3];
    for (int i = 0; i < 3; i++)
        for (int j = 0; j < 3; j++) {
            double s = 0;
            for (int k = 0; k < 3; k++) s += A[i][k] * B[k][j];
            T[i][j] = s;
        }
    for (int i = 0; i < 3; i++) for (int j = 0; j < 3; j++) C[i][j] = T[i][j];
}

static void transpose33(const double A[3][3], double T[3][3]) {
    for (int i = 0; i < 3; i++) for (int j = 0; j < 3; j++) T[i][j] = A[j][i];
}

void ekf_init(Ekf *e, double px, double py, double th, double var_xy, double var_th) {
    e->x[0] = px; e->x[1] = py; e->x[2] = wrap(th);
    for (int i = 0; i < 3; i++) for (int j = 0; j < 3; j++) e->P[i][j] = 0;
    e->P[0][0] = e->P[1][1] = var_xy;
    e->P[2][2] = var_th;
}

void ekf_predict(Ekf *e, double v, double w, double dt, double q_v, double q_w) {
    const double th = e->x[2], c = cos(th), s = sin(th);
    e->x[0] += v * dt * c;
    e->x[1] += v * dt * s;
    e->x[2] = wrap(th + w * dt);
    double F[3][3] = {{1, 0, -v * dt * s}, {0, 1, v * dt * c}, {0, 0, 1}}, Ft[3][3], FP[3][3];
    transpose33(F, Ft);
    mul33(F, e->P, FP);
    mul33(FP, Ft, e->P);
    const double G[3][2] = {{dt * c, 0}, {dt * s, 0}, {0, dt}};
    for (int i = 0; i < 3; i++)
        for (int j = 0; j < 3; j++) e->P[i][j] += G[i][0] * q_v * G[j][0] + G[i][1] * q_w * G[j][1];   /* G M G^T */
}

int ekf_update(Ekf *e, double lx, double ly, double range, double bearing, double r_r, double r_b, double gate) {
    const double dx = lx - e->x[0], dy = ly - e->x[1], q = dx * dx + dy * dy;
    if (q < 1e-12) return -1;
    const double r = sqrt(q);
    const double H[2][3] = {{-dx / r, -dy / r, 0}, {dy / q, -dx / q, -1}};
    const double y[2] = { range - r, wrap(bearing - wrap(atan2(dy, dx) - e->x[2])) };
    double PHt[3][2];                                   /* P H^T */
    for (int i = 0; i < 3; i++)
        for (int j = 0; j < 2; j++) {
            double s = 0;
            for (int k = 0; k < 3; k++) s += e->P[i][k] * H[j][k];
            PHt[i][j] = s;
        }
    double S[2][2];
    for (int i = 0; i < 2; i++)
        for (int j = 0; j < 2; j++) {
            double s = 0;
            for (int k = 0; k < 3; k++) s += H[i][k] * PHt[k][j];
            S[i][j] = s;
        }
    S[0][0] += r_r; S[1][1] += r_b;
    const double det = S[0][0] * S[1][1] - S[0][1] * S[1][0];
    if (!(det > 0)) return -1;
    const double Si[2][2] = {{S[1][1] / det, -S[0][1] / det}, {-S[1][0] / det, S[0][0] / det}};
    const double d2 = y[0] * (Si[0][0] * y[0] + Si[0][1] * y[1]) + y[1] * (Si[1][0] * y[0] + Si[1][1] * y[1]);
    if (d2 > gate) return 1;                            /* Mahalanobis gate: outlier */
    double K[3][2];
    for (int i = 0; i < 3; i++)
        for (int j = 0; j < 2; j++) K[i][j] = PHt[i][0] * Si[0][j] + PHt[i][1] * Si[1][j];
    for (int i = 0; i < 3; i++) e->x[i] += K[i][0] * y[0] + K[i][1] * y[1];
    e->x[2] = wrap(e->x[2]);
    double A[3][3], At[3][3], AP[3][3];                 /* Joseph form */
    for (int i = 0; i < 3; i++)
        for (int j = 0; j < 3; j++) A[i][j] = (i == j) - (K[i][0] * H[0][j] + K[i][1] * H[1][j]);
    transpose33(A, At);
    mul33(A, e->P, AP);
    mul33(AP, At, e->P);
    for (int i = 0; i < 3; i++)
        for (int j = 0; j < 3; j++) e->P[i][j] += K[i][0] * r_r * K[j][0] + K[i][1] * r_b * K[j][1];
    return 0;
}
```

- **Predict**: the nonlinear motion model is linearised by its Jacobian F around the current estimate. The odometry noise, defined in control space (v, ω), is mapped into state space through G. Uncertainty grows with every step.
- **Update**: the range-bearing model's Jacobian H links the pose to the expected measurement, and the Kalman gain weighs the innovation by the relative confidence of prediction (P) and sensor (R).
- **Angles are the classic EKF bug**: the bearing innovation must be wrapped. Otherwise a measurement of −179° against a prediction of +179° looks like a 358° error. The `bearing wrap` test is exactly that case.
- **Mahalanobis gating** (`yᵀS⁻¹y` against a χ² threshold: 13.8 is the 99.9% quantile for 2 degrees of freedom) rejects the injected outliers, which would otherwise yank the estimate off course.
- **The Joseph form** keeps P symmetric and positive definite under floating-point error. The short form `(I − KH)P` slowly loses symmetry over thousands of updates.
- The 4,000-step simulation shows the filter's RMS position error staying around the sensor noise level, while pure odometry would drift without bound.
