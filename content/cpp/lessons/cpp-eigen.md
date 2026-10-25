# Linear Algebra with Eigen

**Eigen** is the standard C++ linear-algebra library for robotics and vision: ROS (tf2_eigen), MoveIt, Ceres, g2o, GTSAM, PCL, Pinocchio and Drake all build on it. It's header-only, uses expression templates to fuse operations without temporaries, vectorises with SIMD, and offers fixed-size matrices that live on the stack for tiny, fast 3×3 rotations. This lesson covers matrices and vectors, fixed versus dynamic sizes, arithmetic and expression templates, decompositions and solvers, the geometry module (rotations, quaternions, isometries), and the alignment and `auto` pitfalls that every Eigen user hits.

## 1. Matrices and vectors

```cpp
#include <Eigen/Dense>
#include <iostream>
using namespace Eigen;

Matrix3d R = Matrix3d::Identity();            // fixed 3x3 double: stack allocated, unrolled loops
Vector3d p(1.0, 2.0, 3.0);
MatrixXd A = MatrixXd::Random(100, 50);       // dynamic size: heap allocated
VectorXd b = VectorXd::Zero(100);
Matrix<float, 6, 6> P = Matrix<float, 6, 6>::Identity() * 0.1f;   // e.g. a 6-DoF covariance

A.rows(), A.cols(), A(0, 1), p.x(), p.norm(), p.normalized(), p.dot(p), p.cross(Vector3d::UnitZ());
A.transpose(), A.block(0, 0, 3, 3), A.col(2), A.row(0).sum(), A.topLeftCorner<2, 2>();
std::cout << R << "\n";
```

| Type | Meaning |
|---|---|
| `Matrix3d`, `Matrix4f`, `Vector3d` | fixed size (d = double, f = float) |
| `MatrixXd`, `VectorXd` | dynamic size |
| `Matrix<T, Rows, Cols>` | general |
| `Array` (`.array()`) | elementwise semantics (`*` is elementwise) |
| `Map<MatrixXd>` | view existing memory (a C array, a ROS message buffer) without copying |

> [!KEY]
> Eigen matrices are **column-major** by default, and `*` is the **matrix product**. For elementwise operations, use `.array()` (`a.array() * b.array()`, `.array().square()`) or `.cwiseProduct()`. Fixed sizes up to about 4×4 are dramatically faster (no heap, fully unrolled). Use them for poses, rotations and small covariances.

## 2. Arithmetic and expression templates

```cpp
VectorXd x = VectorXd::Random(1000), y = VectorXd::Random(1000);
VectorXd z = 2.0 * x + 3.0 * y - x;            // ONE fused loop, no temporaries (expression templates)
MatrixXd C = A.transpose() * A;                // 50x50 Gram matrix
double s = (x.array() * y.array()).sum();      // same as x.dot(y)
x = x.cwiseMax(0.0);                           // ReLU
```

> [!DANGER]
> Never use `auto` to hold an Eigen expression: `auto e = A * B;` stores an unevaluated expression that references `A` and `B` (and possibly temporaries already destroyed), so it re-computes on every use or dangles. Write the concrete type (`MatrixXd e = A * B;`) or call `.eval()`.

**Aliasing**: `A = A.transpose();` is wrong for non-square A, because it reads while writing. Use `A.transposeInPlace()`, or `A = A.transpose().eval();`. Matrix products are evaluated into a temporary by default (safe), and `C.noalias() = A * B;` skips that temporary when you know there's no aliasing.

## 3. Solving linear systems and decompositions

```cpp
Matrix3d M; M << 4, -2, 1,  -2, 4, -2,  1, -2, 4;   // symmetric positive definite
Vector3d rhs(11, -16, 17);
Vector3d sol = M.ldlt().solve(rhs);                // Cholesky-type: SPD/semi-definite, fast and robust
Vector3d sol2 = M.colPivHouseholderQr().solve(rhs); // general, robust
Vector3d sol3 = M.partialPivLu().solve(rhs);        // general square, invertible, fast

MatrixXd X = MatrixXd::Random(200, 3);
VectorXd yv = X * Vector3d(1.0, -2.0, 0.5) + 0.01 * VectorXd::Random(200);
Vector3d w = X.colPivHouseholderQr().solve(yv);     // least squares for tall matrices

SelfAdjointEigenSolver<Matrix3d> es(M);             // symmetric eigendecomposition (covariance, inertia)
es.eigenvalues(); es.eigenvectors();
JacobiSVD<MatrixXd> svd(X, ComputeThinU | ComputeThinV);   // SVD: rank, pseudo-inverse, null space
```

| Decomposition | Requirement | Speed | Notes |
|---|---|---|---|
| `llt()` | SPD | fastest | Kalman/least-squares normal equations |
| `ldlt()` | positive or negative semi-definite | very fast | robust Cholesky variant |
| `partialPivLu()` | invertible square | fast | |
| `householderQr()` / `colPivHouseholderQr()` | any | medium | least squares; column pivoting reveals rank |
| `JacobiSVD` / `BDCSVD` | any | slow / large | most accurate; pseudo-inverse |

As in NumPy: **solve, don't invert** (`M.inverse() * b` is slower and less accurate, though fine for fixed 3×3 or 4×4).

## 4. Geometry: rotations and transforms

```cpp
#include <Eigen/Geometry>

AngleAxisd aa(M_PI / 2, Vector3d::UnitZ());          // 90° about z
Matrix3d Rz = aa.toRotationMatrix();
Quaterniond q(aa);                                    // (w, x, y, z) constructor order!  q.w(), q.vec()
Quaterniond q2 = Quaterniond::FromTwoVectors(Vector3d::UnitX(), Vector3d::UnitY());
Quaterniond mid = q.slerp(0.5, Quaterniond::Identity());   // interpolate
Vector3d ypr = Rz.eulerAngles(2, 1, 0);               // ZYX order: yaw, pitch, roll (ranges: [0,π] for the first angle!)

Isometry3d T_map_base = Isometry3d::Identity();       // rigid transform (rotation + translation)
T_map_base.rotate(AngleAxisd(M_PI / 2, Vector3d::UnitZ()));
T_map_base.pretranslate(Vector3d(2.0, 1.0, 0.0));
Isometry3d T_base_laser = Isometry3d::Identity();
T_base_laser.translation() << 0.2, 0.0, 0.3;
Vector3d p_map = T_map_base * T_base_laser * Vector3d(1.0, 0.0, 0.0);   // compose, then apply
Isometry3d T_inv = T_map_base.inverse();              // uses Rᵀ, not a general inverse
```

> [!WARNING]
> - **Quaternion constructor order**: `Quaterniond(w, x, y, z)` takes w first, but the *storage* order (and `coeffs()`, and ROS messages) is (x, y, z, w). Mixing these up is a classic bug.
> - Normalise quaternions after integrating angular velocity (`q.normalize()`).
> - Use `Isometry3d` for rigid transforms. `Affine3d` allows scaling and shear, and its inverse is more expensive.

## 5. Interop and performance

- `Map<const VectorXd> v(ptr, n);` wraps existing data (std::vector, PCL clouds, ROS buffers) without copying.
- `tf2_eigen` converts between ROS `geometry_msgs` and Eigen types (`tf2::transformToEigen`).
- Compile with `-O2 -march=native` for SIMD, and with `-DNDEBUG` to remove the bounds asserts (keep them in debug builds).
- **Alignment**: since C++17, Eigen's fixed-size vectorisable types are correctly aligned in `std::vector` and with `new`. The old `EIGEN_MAKE_ALIGNED_OPERATOR_NEW` and `aligned_allocator` rules matter only for pre-C++17 code, which you'll still see in older codebases.

## 6. Exam-ready answers

> [!EXAM]
> **Expression templates in Eigen.** Eigen overloads arithmetic operators to return lightweight expression objects that describe a computation rather than performing it; the expression is evaluated only when assigned to a concrete matrix, at which point the whole expression is compiled into a single loop (with SIMD vectorisation and, for small fixed sizes, full unrolling) without allocating temporaries for intermediate results. This makes high-level code such as `z = 2*x + 3*y − x` as efficient as a hand-written loop. The cost is that storing an expression in an `auto` variable keeps unevaluated references that may dangle or be recomputed, and aliasing between source and destination must be handled explicitly (for example with `.eval()` or `transposeInPlace()`).

## 7. Cheat sheet

| Need | Eigen |
|---|---|
| small fixed matrix | `Matrix3d`, `Vector3d` |
| big dynamic | `MatrixXd A(r, c)` |
| elementwise | `.array()`, `.cwiseProduct()` |
| solve SPD | `A.ldlt().solve(b)` |
| least squares | `A.colPivHouseholderQr().solve(b)` |
| eigen (symmetric) | `SelfAdjointEigenSolver<Matrix3d>` |
| rotation | `AngleAxisd(angle, axis)`, `Quaterniond(w, x, y, z)` |
| rigid transform | `Isometry3d`, `T * p`, `T.inverse()` |
| wrap memory | `Map<VectorXd>(ptr, n)` |
| avoid | `auto` for expressions, `A = A.transpose()` |

> [!INTERVIEW]
> **"Why is `Matrix3d` faster than `MatrixXd(3, 3)`?"** The fixed size is known at compile time. Storage lives inline on the stack (no heap allocation), loops are fully unrolled, the compiler can keep elements in registers, and SIMD paths are chosen statically. `MatrixXd` heap-allocates and loops over runtime sizes. For a 3×3 rotation product, that's roughly a 5–10× difference. Use fixed sizes for poses and small covariances, and dynamic sizes for data-dependent dimensions.
