---
id: py-cone-detector
title: Colour Cone Detector with OpenCV
difficulty: Hard
order: 1
tags: OpenCV, HSV, inRange, morphology, contours, moments, projectPoints
time_limit: 6
---
## Statement
A robot follows orange traffic cones. Using **OpenCV**, implement:

```python
def detect_cones(bgr, min_area=150):
    """Return a list of (cx, cy, area) for orange blobs, sorted by area descending.
    Pipeline: BGR->HSV; inRange with H in [5, 22], S in [120, 255], V in [90, 255]; morphological OPEN then
    CLOSE with a 5x5 ellipse kernel; external contours; keep contours with cv2.contourArea >= min_area;
    centroid from cv2.moments. cx, cy rounded to 1 decimal, area rounded to integer."""

def steering_error(bgr):
    """Horizontal offset of the largest cone's centroid from the image centre, normalised to [-1, 1]
    ((cx - W/2) / (W/2)), rounded to 3 decimals; None if no cone."""

def project(points_3d, fx, fy, cx, cy):
    """Project (n, 3) camera-frame points with cv2.projectPoints (no rotation/translation, no distortion);
    return a list of [u, v] rounded to 2 decimals."""
```

The driver draws synthetic scenes (cones as filled orange triangles and circles, plus noise, distractors in red and yellow, and salt specks) and checks the detections.

## Starter
```python
import numpy as np

def detect_cones(bgr, min_area=150):
    ys, xs = np.nonzero(bgr[:, :, 2] > 200)
    if len(xs) == 0:
        return []
    return [(round(float(xs.mean()), 1), round(float(ys.mean()), 1), len(xs))]

def steering_error(bgr):
    return None

def project(points_3d, fx, fy, cx, cy):
    return [[0.0, 0.0] for _ in points_3d]
```

## Driver
```python
import sys
import cv2
import numpy as np

ORANGE = (0, 128, 255)     # BGR
def scene(seed, cones, distractors=True, specks=True, size=(240, 320)):
    rng = np.random.default_rng(seed)
    img = np.full((*size, 3), (90, 110, 100), np.uint8)
    img = cv2.add(img, rng.integers(0, 25, img.shape, dtype=np.uint8))
    for kind, x, y, s in cones:
        if kind == "tri":
            pts = np.array([[x, y - s], [x - s // 2, y + s // 2], [x + s // 2, y + s // 2]], np.int32)
            cv2.fillPoly(img, [pts], ORANGE)
        else:
            cv2.circle(img, (x, y), s, ORANGE, -1)
    if distractors:
        cv2.rectangle(img, (10, 10), (40, 40), (0, 0, 220), -1)          # red
        cv2.rectangle(img, (280, 200), (310, 230), (0, 230, 230), -1)    # yellow
    if specks:
        ys, xs = rng.integers(0, size[0], 60), rng.integers(0, size[1], 60)
        img[ys, xs] = ORANGE                                             # isolated orange pixels
    return img

for cmd in sys.stdin.read().split():
    if cmd == "one":
        img = scene(1, [("tri", 160, 120, 40)])
        print("detect:", detect_cones(img), "steer:", steering_error(img))
    elif cmd == "many":
        img = scene(2, [("tri", 60, 150, 30), ("circle", 250, 80, 18), ("tri", 200, 190, 50), ("circle", 120, 60, 5)])
        d = detect_cones(img)
        print("count:", len(d), "detect:", d, "steer:", steering_error(img))
    elif cmd == "none":
        img = scene(3, [])
        print("empty:", detect_cones(img), steering_error(img))
    elif cmd == "edge":
        img = scene(4, [("circle", 5, 120, 20), ("tri", 300, 120, 30)], specks=False)
        print("edge:", detect_cones(img, min_area=100), "steer:", steering_error(img))
    elif cmd == "project":
        pts = np.array([[0.0, 0.0, 2.0], [0.5, -0.25, 2.5], [-1.0, 0.2, 4.0]])
        print("project:", project(pts, 500.0, 500.0, 320.0, 240.0))
```

## Tests
=== sample
one
project
---
detect: [(160.0, 120.1, 1187)] steer: 0.0
project: [[320.0, 240.0], [420.0, 190.0], [195.0, 265.0]]
=== hidden
many
none
edge
---
count: 3 detect: [(200.0, 190.1, 1862), (250.0, 80.0, 952), (60.0, 150.2, 662)] steer: 0.25
empty: [] None
edge: [(10.7, 120.0, 790), (300.0, 120.2, 662)] steer: -0.933

## Hints
- `hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)`; `mask = cv2.inRange(hsv, (5, 120, 90), (22, 255, 255))`.
- `k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))`; open, then close.
- `contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)`; `M = cv2.moments(c)`; `cx = M["m10"] / M["m00"]`.
- `cv2.projectPoints(points.astype(np.float64), np.zeros(3), np.zeros(3), K, np.zeros(5))` returns an array of shape (n, 1, 2).

## Solution
```python
import cv2
import numpy as np

LOW, HIGH = np.array([5, 120, 90]), np.array([22, 255, 255])
KERNEL = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))

def detect_cones(bgr, min_area=150):
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, LOW, HIGH)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, KERNEL)      # remove specks
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, KERNEL)     # fill small holes
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    out = []
    for c in contours:
        area = cv2.contourArea(c)
        if area < min_area:
            continue
        M = cv2.moments(c)
        if M["m00"] == 0:
            continue
        out.append((round(M["m10"] / M["m00"], 1), round(M["m01"] / M["m00"], 1), int(round(area))))
    return sorted(out, key=lambda t: -t[2])

def steering_error(bgr):
    cones = detect_cones(bgr)
    if not cones:
        return None
    half = bgr.shape[1] / 2
    return round((cones[0][0] - half) / half, 3)

def project(points_3d, fx, fy, cx, cy):
    K = np.array([[fx, 0, cx], [0, fy, cy], [0, 0, 1.0]])
    uv, _ = cv2.projectPoints(np.asarray(points_3d, dtype=np.float64), np.zeros(3), np.zeros(3), K, np.zeros(5))
    return np.round(uv.reshape(-1, 2), 2).tolist()
```

This is the classic colour-tracking pipeline:
- **HSV thresholding** isolates orange regardless of brightness. Red and yellow distractors fall outside the hue band.
- **Opening** erases isolated specks, which survive thresholding because they really are orange, and **closing** heals small holes.
- **Contours and moments** give each blob's area and centroid, and an area filter rejects remnants and tiny far-away cones.
- **The steering error** turns the centroid into a normalised control signal, the input to a PID heading controller.
- **`projectPoints`** applies the pinhole model u = fx·X/Z + cx, connecting 3-D cone positions (for example from a map) to where they should appear in the image.
