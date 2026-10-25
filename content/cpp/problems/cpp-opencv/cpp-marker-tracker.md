---
id: cpp-marker-tracker
title: Coloured Marker Tracker in OpenCV C++
difficulty: Hard
order: 1
tags: OpenCV, cv::Mat, HSV, contours, moments, minAreaRect, projectPoints, ROI
libs: opencv
time_limit: 4
---
## Statement
A docking robot finds coloured floor markers in camera frames. Implement with the **OpenCV C++ API**:

```cpp
struct Marker { double cx, cy, area, angle_deg; };

std::vector<Marker> find_markers(const cv::Mat& bgr, const cv::Scalar& hsv_lo, const cv::Scalar& hsv_hi,
                                 double min_area);
    // HSV inRange -> MORPH_OPEN with a 3x3 rectangular kernel -> external contours with contourArea >= min_area.
    // cx, cy: centroid from cv::moments; area: contourArea; angle_deg: cv::minAreaRect(contour).angle.
    // Sort by area descending.

cv::Mat crop_and_mark(const cv::Mat& bgr, const cv::Rect& roi);
    // Return an INDEPENDENT copy of the region (clamped to the image), with a 1-pixel white border drawn on the copy.
    // The input image must not change.

std::vector<cv::Point2d> project(const std::vector<cv::Point3d>& pts, double fx, double fy, double cx, double cy);
    // cv::projectPoints with zero rotation/translation and no distortion.
```

## Starter
```cpp
#include <opencv2/core.hpp>
#include <opencv2/imgproc.hpp>
#include <opencv2/calib3d.hpp>
#include <vector>

struct Marker { double cx, cy, area, angle_deg; };

std::vector<Marker> find_markers(const cv::Mat& bgr, const cv::Scalar& lo, const cv::Scalar& hi, double min_area) {
    return {};
}
cv::Mat crop_and_mark(const cv::Mat& bgr, const cv::Rect& roi) {
    cv::Mat r = bgr(roi);
    cv::rectangle(r, cv::Rect(0, 0, r.cols, r.rows), cv::Scalar(255, 255, 255), 1);
    return r;
}
std::vector<cv::Point2d> project(const std::vector<cv::Point3d>& pts, double fx, double fy, double cx, double cy) {
    return std::vector<cv::Point2d>(pts.size());
}
```

## Driver
```cpp
#include <cstdio>
#include <iostream>
#include <string>

static cv::Mat scene(int seed) {
    cv::RNG rng(seed);
    cv::Mat img(240, 320, CV_8UC3, cv::Scalar(70, 80, 75));
    cv::Mat noise(img.size(), CV_8UC3);
    rng.fill(noise, cv::RNG::UNIFORM, 0, 20);
    img += noise;
    auto blue = cv::Scalar(200, 60, 20);
    cv::RotatedRect r1({80, 70}, {60, 24}, 30.0f), r2({230, 160}, {40, 40}, 0.0f), r3({250, 40}, {6, 6}, 0.0f);
    for (auto& r : {r1, r2, r3}) {
        cv::Point2f p[4]; r.points(p);
        std::vector<cv::Point> poly(p, p + 4);
        cv::fillConvexPoly(img, poly, blue);
    }
    cv::circle(img, {160, 200}, 18, cv::Scalar(30, 30, 220), -1);          // red distractor
    for (int i = 0; i < 40; ++i) img.at<cv::Vec3b>(rng.uniform(0, 240), rng.uniform(0, 320)) = cv::Vec3b(200, 60, 20);
    return img;
}

int main() {
    std::string cmd;
    while (std::cin >> cmd) {
        if (cmd == "markers") {
            cv::Mat img = scene(1);
            auto ms = find_markers(img, {100, 150, 100}, {130, 255, 255}, 100.0);
            std::printf("found %zu\n", ms.size());
            for (auto& m : ms) std::printf("  c=(%.1f, %.1f) area=%.0f angle=%.1f\n", m.cx, m.cy, m.area, m.angle_deg);
            auto red = find_markers(img, {0, 150, 100}, {10, 255, 255}, 100.0);
            std::printf("red markers: %zu, area %.0f\n", red.size(), red.empty() ? 0.0 : red[0].area);
        } else if (cmd == "crop") {
            cv::Mat img = scene(2), before = img.clone();
            cv::Mat c = crop_and_mark(img, cv::Rect(300, 220, 50, 50));     // runs off the image: clamp
            bool unchanged = cv::norm(img, before, cv::NORM_L1) == 0;
            cv::Vec3b corner = c.at<cv::Vec3b>(0, 0);
            std::printf("crop %dx%d, input unchanged: %s, corner white: %s, independent: %s\n", c.cols, c.rows,
                        unchanged ? "yes" : "no", corner == cv::Vec3b(255, 255, 255) ? "yes" : "no",
                        c.data != img.data && (c.datastart < img.datastart || c.datastart >= img.dataend) ? "yes" : "no");
        } else if (cmd == "project") {
            auto px = project({{0, 0, 2}, {0.5, -0.25, 2.5}, {-1, 0.2, 4}}, 500, 500, 320, 240);
            for (auto& p : px) std::printf("(%.2f, %.2f) ", p.x, p.y);
            std::printf("\n");
        }
    }
}
```

## Tests
=== sample
markers
project
---
found 2
  c=(230.0, 160.0) area=1600 angle=90.0
  c=(80.0, 70.0) area=1396 angle=30.0
red markers: 1, area 952
(320.00, 240.00) (420.00, 190.00) (195.00, 265.00) 
=== hidden
crop
markers
---
crop 20x20, input unchanged: yes, corner white: yes, independent: yes
found 2
  c=(230.0, 160.0) area=1600 angle=90.0
  c=(80.0, 70.0) area=1396 angle=30.0
red markers: 1, area 952

## Hints
- `cv::cvtColor(bgr, hsv, cv::COLOR_BGR2HSV)`; `cv::inRange(hsv, lo, hi, mask)`; `cv::morphologyEx(mask, mask, cv::MORPH_OPEN, cv::getStructuringElement(cv::MORPH_RECT, {3, 3}))`.
- `cv::findContours(mask, contours, cv::RETR_EXTERNAL, cv::CHAIN_APPROX_SIMPLE)`; `cv::Moments m = cv::moments(c)`; `cv::minAreaRect(c).angle`.
- **Crop**: clamp with `roi & cv::Rect(0, 0, bgr.cols, bgr.rows)`, then `bgr(r).clone()`. The starter's view modifies the caller's image.
- **Project**: `cv::Mat K = (cv::Mat_<double>(3, 3) << fx, 0, cx, 0, fy, cy, 0, 0, 1);` and `cv::projectPoints(pts, cv::Vec3d(0, 0, 0), cv::Vec3d(0, 0, 0), K, cv::noArray(), out);`.

## Solution
```cpp
#include <opencv2/core.hpp>
#include <opencv2/imgproc.hpp>
#include <opencv2/calib3d.hpp>
#include <algorithm>
#include <vector>

struct Marker { double cx, cy, area, angle_deg; };

std::vector<Marker> find_markers(const cv::Mat& bgr, const cv::Scalar& lo, const cv::Scalar& hi, double min_area) {
    cv::Mat hsv, mask;
    cv::cvtColor(bgr, hsv, cv::COLOR_BGR2HSV);
    cv::inRange(hsv, lo, hi, mask);
    cv::morphologyEx(mask, mask, cv::MORPH_OPEN, cv::getStructuringElement(cv::MORPH_RECT, {3, 3}));
    std::vector<std::vector<cv::Point>> contours;
    cv::findContours(mask, contours, cv::RETR_EXTERNAL, cv::CHAIN_APPROX_SIMPLE);
    std::vector<Marker> out;
    for (const auto& c : contours) {
        double area = cv::contourArea(c);
        if (area < min_area) continue;
        cv::Moments m = cv::moments(c);
        if (m.m00 == 0) continue;
        out.push_back({m.m10 / m.m00, m.m01 / m.m00, area, cv::minAreaRect(c).angle});
    }
    std::sort(out.begin(), out.end(), [](const Marker& a, const Marker& b) { return a.area > b.area; });
    return out;
}

cv::Mat crop_and_mark(const cv::Mat& bgr, const cv::Rect& roi) {
    cv::Rect r = roi & cv::Rect(0, 0, bgr.cols, bgr.rows);       // clamp to the image
    cv::Mat out = bgr(r).clone();                                 // deep copy: never touch the caller's pixels
    cv::rectangle(out, cv::Rect(0, 0, out.cols, out.rows), cv::Scalar(255, 255, 255), 1);
    return out;
}

std::vector<cv::Point2d> project(const std::vector<cv::Point3d>& pts, double fx, double fy, double cx, double cy) {
    cv::Mat K = (cv::Mat_<double>(3, 3) << fx, 0, cx, 0, fy, cy, 0, 0, 1);
    std::vector<cv::Point2d> out;
    cv::projectPoints(pts, cv::Vec3d(0, 0, 0), cv::Vec3d(0, 0, 0), K, cv::noArray(), out);
    return out;
}
```

- **The detection chain** (HSV threshold, morphological opening, external contours, moments) is the C++ twin of the Python pipeline. `minAreaRect` adds the marker's orientation, which a docking controller uses to align the robot's heading.
- **`cv::Mat` semantics**: `bgr(roi)` is a *view*, so the starter scribbles on the caller's image and returns memory owned by it. `clone()` gives an independent buffer. The `&` intersection clamps a partly off-image ROI, which would otherwise throw.
- **`projectPoints`** implements the pinhole model through OpenCV's calibrated-camera API, the same call used to overlay predicted marker positions or to compute reprojection errors.
