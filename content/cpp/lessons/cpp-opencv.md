# OpenCV in C++

OpenCV's native API is C++. Python's `cv2` wraps it, so everything from the Python OpenCV lesson carries over, but C++ adds control over memory, performance and integration with real-time robot code. This lesson covers `cv::Mat` (its reference-counted memory model is the key difference from NumPy), element access, the image-processing pipeline in C++, camera input, and interop with Eigen and ROS.

## 1. `cv::Mat`: a reference-counted image

```cpp
#include <opencv2/core.hpp>
#include <opencv2/imgproc.hpp>

cv::Mat img(240, 320, CV_8UC3, cv::Scalar(255, 0, 0));   // rows, cols, type (8-bit unsigned, 3 channels), BGR blue
cv::Mat gray(240, 320, CV_8UC1, cv::Scalar(0));
img.rows, img.cols, img.channels(), img.type(), img.isContinuous();

cv::Mat b = img;                 // SHALLOW copy: shares pixels (reference count++)
cv::Mat c = img.clone();         // deep copy
cv::Mat roi = img(cv::Rect(10, 20, 100, 50));   // view of a sub-region: no copy
roi.setTo(cv::Scalar(0, 255, 0));                // modifies img too!
```

> [!KEY]
> Assignment and copy construction of `cv::Mat` **share data** (like `shared_ptr`). Use `clone()` or `copyTo()` for an independent copy. Functions with `OutputArray` parameters (`cv::cvtColor(src, dst, ...)`) allocate `dst` as needed, and reuse it across iterations if the size and type match. That makes loops allocation-free after the first frame.

| Type macro | Meaning |
|---|---|
| `CV_8UC1` / `CV_8UC3` | 8-bit grey / colour (BGR) |
| `CV_16SC1` | signed 16-bit (gradients) |
| `CV_32FC1` / `CV_32FC3` | float images (normalised maths) |
| `CV_64FC1` | double (camera matrices) |

## 2. Element access

```cpp
gray.at<uchar>(10, 20) = 255;                       // row 10, column 20: checked in debug builds, slow-ish
cv::Vec3b pixel = img.at<cv::Vec3b>(5, 7);          // B, G, R
for (int y = 0; y < gray.rows; ++y) {               // fast: a row pointer per row
    uchar* row = gray.ptr<uchar>(y);
    for (int x = 0; x < gray.cols; ++x) row[x] = static_cast<uchar>(255 - row[x]);
}
gray.forEach<uchar>([](uchar& p, const int*) { p = p > 128 ? 255 : 0; });   // parallel per-pixel
```

`at<T>(row, col)` uses (row, col), but `cv::Point(x, y)` uses (col, row). That's the same trap as in Python. Prefer whole-image functions (`cv::threshold`, `cv::LUT`, arithmetic operators) over per-pixel loops.

## 3. The processing pipeline

```cpp
cv::Mat hsv, mask, edges, blurred;
cv::cvtColor(img, hsv, cv::COLOR_BGR2HSV);
cv::inRange(hsv, cv::Scalar(5, 120, 90), cv::Scalar(22, 255, 255), mask);
cv::Mat k = cv::getStructuringElement(cv::MORPH_ELLIPSE, {5, 5});
cv::morphologyEx(mask, mask, cv::MORPH_OPEN, k);
std::vector<std::vector<cv::Point>> contours;
cv::findContours(mask, contours, cv::RETR_EXTERNAL, cv::CHAIN_APPROX_SIMPLE);
for (const auto& c : contours) {
    double area = cv::contourArea(c);
    cv::Moments m = cv::moments(c);
    if (area > 100 && m.m00 > 0) {
        cv::Point2d centroid(m.m10 / m.m00, m.m01 / m.m00);
        cv::Rect box = cv::boundingRect(c);
    }
}
cv::GaussianBlur(gray, blurred, {5, 5}, 1.5);
cv::Canny(blurred, edges, 50, 150);
```

## 4. Camera input and video

```cpp
#include <opencv2/videoio.hpp>
cv::VideoCapture cap(0);                         // or a file / GStreamer pipeline / RTSP URL
cap.set(cv::CAP_PROP_FRAME_WIDTH, 640);
cv::Mat frame;
while (cap.read(frame)) {                        // frame buffer reused each iteration
    // process ...
}
```

On robots, camera frames usually arrive as ROS `sensor_msgs/Image` messages instead: **cv_bridge** converts them to and from `cv::Mat`.

## 5. Geometry and calibration

```cpp
#include <opencv2/calib3d.hpp>
cv::Mat K = (cv::Mat_<double>(3, 3) << 500, 0, 320, 0, 500, 240, 0, 0, 1);
std::vector<cv::Point3d> obj{{0, 0, 2}, {0.5, -0.25, 2.5}};
std::vector<cv::Point2d> px;
cv::projectPoints(obj, cv::Vec3d(0, 0, 0), cv::Vec3d(0, 0, 0), K, cv::noArray(), px);   // (320,240), (420,190)
// cv::solvePnP(objectPoints, imagePoints, K, dist, rvec, tvec);   // pose from 2-D/3-D correspondences
// cv::calibrateCamera(objPts, imgPts, size, K, dist, rvecs, tvecs);
```

## 6. Interop with Eigen and performance

```cpp
#include <opencv2/core/eigen.hpp>      // include after <Eigen/Dense>
// Eigen::Matrix3d Ke; cv::cv2eigen(K, Ke); cv::eigen2cv(Ke, K);
```

Performance habits:
- Pre-allocate outputs and reuse them across frames.
- Avoid per-pixel `at<>` in hot loops.
- Use `cv::UMat` for transparent OpenCL acceleration, and the `cv::cuda` modules where available.
- Build with optimisations, and use `cv::setNumThreads` to control parallelism.
- Process only regions of interest (`cv::Rect` views are free).

## 7. Exam-ready answers

> [!EXAM]
> **The cv::Mat memory model.** A `cv::Mat` consists of a header (dimensions, type, step) and a pointer to a reference-counted pixel buffer. Copying or assigning a Mat copies only the header and increments the reference count, so several Mats can share and modify the same pixels; regions of interest created with `operator()(Rect)` are likewise views into the parent's data. Independent copies require `clone()` or `copyTo()`. Output arrays passed to OpenCV functions are (re)allocated with `create()` only when their size or type differs, which allows processing loops to reuse buffers without per-frame allocation. The buffer is freed when the last Mat referencing it is destroyed.

## 8. Cheat sheet

| Need | C++ |
|---|---|
| new image | `cv::Mat m(rows, cols, CV_8UC3, cv::Scalar(b, g, r))` |
| deep copy | `m.clone()` |
| sub-region view | `m(cv::Rect(x, y, w, h))` |
| pixel | `m.at<cv::Vec3b>(row, col)` |
| fast rows | `m.ptr<uchar>(row)` |
| convert colour | `cv::cvtColor(src, dst, cv::COLOR_BGR2HSV)` |
| contours | `cv::findContours(mask, contours, RETR_EXTERNAL, CHAIN_APPROX_SIMPLE)` |
| projection | `cv::projectPoints(obj, rvec, tvec, K, dist, px)` |
| Eigen interop | `cv::cv2eigen`, `cv::eigen2cv` |
| link | `find_package(OpenCV)`; `${OpenCV_LIBS}` |

> [!INTERVIEW]
> **"You store camera frames in a `std::vector<cv::Mat>` buffer and every entry ends up showing the latest frame. Why?"** `cap.read(frame)` reuses the same pixel buffer, and `push_back(frame)` copies only the header, so every element shares one buffer that gets overwritten. Push `frame.clone()` instead (or read into a fresh Mat each time). It's the reference-counted shallow-copy semantics.
