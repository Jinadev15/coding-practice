# Computer Vision with OpenCV

OpenCV is the most widely used computer-vision library: camera capture, image processing, feature detection, geometry and calibration, from hobby robots to industrial inspection. In Python, OpenCV images are **NumPy arrays**, so everything from the NumPy lessons applies directly. This lesson covers the image representation (and OpenCV's BGR quirk), colour spaces, filtering, thresholding, edges, contours, morphology, geometric transforms, and camera calibration basics: the pipeline behind line followers, object detection by colour, fiducial tracking and visual odometry front ends.

## 1. Images are arrays

```python
import cv2
import numpy as np

img = np.zeros((240, 320, 3), dtype=np.uint8)   # height x width x channels
img[:, :160] = (255, 0, 0)                      # left half BLUE: OpenCV uses BGR order!
cv2.rectangle(img, (200, 60), (280, 180), (0, 255, 0), thickness=-1)   # filled green box
cv2.circle(img, (80, 120), 30, (0, 0, 255), 2)
img.shape, img.dtype                             # (240, 320, 3), uint8
# file and camera I/O:
# img = cv2.imread("frame.png")                  # returns None (no exception!) if the file is missing
# cv2.imwrite("out.png", img)
# cap = cv2.VideoCapture(0); ok, frame = cap.read()
```

> [!KEY]
> - The shape is **(rows, cols, channels) = (height, width, 3)**, but OpenCV *functions* take points and sizes as **(x, y) = (col, row)**. Mixing these up is the most common bug.
> - Channels are **BGR**, not RGB. Convert with `cv2.cvtColor(img, cv2.COLOR_BGR2RGB)` before passing images to Matplotlib or most deep-learning models.
> - `cv2.imread` returns `None` on failure. Check it.

## 2. Colour spaces and colour segmentation

```python
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)            # single channel
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)              # H in [0, 180), S and V in [0, 255]
mask = cv2.inRange(hsv, np.array([50, 100, 100]), np.array([70, 255, 255]))   # green pixels → 255
green_only = cv2.bitwise_and(img, img, mask=mask)
```

HSV separates **hue** (colour) from brightness, so a threshold on hue survives lighting changes far better than one on raw BGR. That makes it the classic way to detect coloured balls, cones and markers. Red wraps around hue 0/180, so it needs two ranges OR-ed together.

## 3. Filtering

| Filter | Call | Use |
|---|---|---|
| box blur | `cv2.blur(img, (5, 5))` | fast smoothing |
| Gaussian | `cv2.GaussianBlur(img, (5, 5), 1.5)` | noise reduction before edges |
| median | `cv2.medianBlur(img, 5)` | salt-and-pepper noise, keeps edges |
| bilateral | `cv2.bilateralFilter(img, 9, 75, 75)` | smooth while preserving edges |
| custom kernel | `cv2.filter2D(img, -1, kernel)` | any convolution |
| Sobel gradients | `cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=3)` | x derivative |

Use a signed or float output depth (`CV_16S`/`CV_32F`) for derivatives. With `uint8`, negative gradients are clipped to 0.

## 4. Thresholding and edges

```python
_, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
_, otsu = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)        # automatic threshold
adaptive = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
edges = cv2.Canny(cv2.GaussianBlur(gray, (5, 5), 0), 50, 150)                     # hysteresis thresholds
```

**Canny** combines Gaussian smoothing, gradient magnitude and direction, non-maximum suppression (thin edges) and hysteresis (strong edges seed, weak edges extend), which makes it the default edge detector. Lines and circles come from `cv2.HoughLinesP` and `cv2.HoughCircles`.

## 5. Morphology

```python
kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
opened = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)    # erode then dilate: removes specks
closed = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)   # dilate then erode: fills holes
```

Morphology cleans binary masks before contour detection. Dilating an obstacle map by the robot's radius is the configuration-space trick used in 2-D path planning.

## 6. Contours and connected components

```python
contours, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
for c in contours:
    area = cv2.contourArea(c)
    if area < 100:
        continue
    x, y, w, h = cv2.boundingRect(c)
    M = cv2.moments(c)
    cx, cy = M["m10"] / M["m00"], M["m01"] / M["m00"]      # centroid
    (ex, ey), radius = cv2.minEnclosingCircle(c)
    poly = cv2.approxPolyDP(c, 0.02 * cv2.arcLength(c, True), True)   # 4 vertices → likely a rectangle

n, labels, stats, centroids = cv2.connectedComponentsWithStats(mask)  # stats: x, y, w, h, area per blob
```

The "detect a coloured object and steer towards it" pipeline is: HSV `inRange` → morphology → the largest contour → its centroid → the controller's error is the centroid offset from the image centre.

## 7. Geometric transforms

```python
h, w = gray.shape
M = cv2.getRotationMatrix2D((w / 2, h / 2), 30, 1.0)       # 2x3 affine: rotate 30° about the centre
rotated = cv2.warpAffine(gray, M, (w, h))
src = np.float32([[0, 0], [w - 1, 0], [w - 1, h - 1], [0, h - 1]])
dst = np.float32([[20, 10], [w - 30, 0], [w - 1, h - 1], [0, h - 20]])
H = cv2.getPerspectiveTransform(src, dst)                  # 3x3 homography
warped = cv2.warpPerspective(gray, H, (w, h))              # bird's-eye views of the floor or a road
small = cv2.resize(gray, (w // 2, h // 2), interpolation=cv2.INTER_AREA)   # INTER_AREA for shrinking
```

## 8. Camera model and calibration basics

The **pinhole model** projects a 3-D point (X, Y, Z) in camera coordinates to pixel coordinates:

u = fx·X/Z + cx,  v = fy·Y/Z + cy,  with intrinsic matrix K = [[fx, 0, cx], [0, fy, cy], [0, 0, 1]]

Real lenses add **distortion** (radial k1, k2, k3; tangential p1, p2). **Calibration** estimates K and the distortion coefficients from several views of a known pattern (a chessboard):

```python
# pattern_size = (9, 6); objp = 3-D chessboard corners in board units (z = 0)
# found, corners = cv2.findChessboardCorners(gray, pattern_size)
# cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
# rms, K, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)
# undistorted = cv2.undistort(img, K, dist)
pts3d = np.array([[0.0, 0.0, 2.0], [0.5, -0.25, 2.5]])
K = np.array([[500.0, 0, 320], [0, 500.0, 240], [0, 0, 1]])
px, _ = cv2.projectPoints(pts3d, np.zeros(3), np.zeros(3), K, np.zeros(5))   # → [[320, 240], [420, 190]]
```

`cv2.solvePnP` recovers a camera pose from known 3-D/2-D correspondences, which is how fiducial markers (ArUco, AprilTag) give a robot its pose. The RMS reprojection error from calibration should typically be under 0.5 px.

## 9. Exam-ready answers

> [!EXAM]
> **The pinhole camera model and calibration.** In the pinhole model, a point with camera coordinates (X, Y, Z) projects to the image plane at pixel coordinates u = fₓX/Z + cₓ and v = f_yY/Z + c_y, where the intrinsic parameters fₓ, f_y (focal lengths in pixels) and (cₓ, c_y) (principal point) form the camera matrix K; extrinsic parameters (rotation and translation) relate world and camera frames. Real lenses add radial and tangential distortion. Camera calibration estimates the intrinsics and distortion coefficients by observing a planar pattern of known geometry, such as a chessboard, in several poses and minimising the reprojection error between detected and projected corners; the result enables undistortion, metric measurement and pose estimation with methods such as PnP.

## 10. Cheat sheet

| Need | OpenCV |
|---|---|
| colour conversion | `cv2.cvtColor(img, cv2.COLOR_BGR2HSV)` |
| colour mask | `cv2.inRange(hsv, lo, hi)` |
| denoise | `GaussianBlur`, `medianBlur` |
| binarise | `threshold(..., THRESH_OTSU)`, `adaptiveThreshold` |
| edges | `cv2.Canny(blur, 50, 150)` |
| clean mask | `morphologyEx(OPEN / CLOSE)` |
| objects | `findContours`, `boundingRect`, `moments` |
| rotate / warp | `getRotationMatrix2D` + `warpAffine`, `getPerspectiveTransform` + `warpPerspective` |
| 3-D → pixels | `projectPoints(pts, rvec, tvec, K, dist)` |
| pose from points | `solvePnP` |

> [!INTERVIEW]
> **"Your colour-based ball detector fails when clouds pass. How do you make it robust?"** Threshold in HSV on hue (with a reasonably wide saturation and value range) rather than in BGR. Normalise exposure (CLAHE on V), clean the mask with morphological opening, filter blobs by area and circularity, and track over time (a Kalman filter on the centroid) to bridge dropouts. If that's still fragile, move to a learned detector. For a fixed camera, lock its auto-exposure and white balance.
