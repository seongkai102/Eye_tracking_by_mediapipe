# Eye_tracking_by_mediapipe

## Overview

This project uses **MediaPipe Face Mesh** to track the user's iris movements and map them to monitor coordinates. The sensitivity changes caused by distance (Z-axis) are corrected using nonlinear transformations, and cursor movement is smoothed with Exponential Moving Average (EMA).

---

## Process Explanation

### Step 1: **Calibration**

1. **Extract Iris Center Coordinates**:
   - MediaPipe's `face_mesh` is used to extract the coordinates of the **left and right irises**.
   - The average coordinates of both irises are calculated:
     - `x_iris = (x_right + x_left) / 2`
     - `y_iris = (y_right + y_left) / 2`

2. **Set Reference Point**:
   - **For 3 seconds**, the user looks at the center of the monitor to collect iris coordinates.
   - The average values of the collected coordinates are set as the reference point:
     - `origin_x = sum(x_iris) / N`
     - `origin_y = sum(y_iris) / N`
     - `origin_z = sum(z_nose) / N`

---

### Step 2: **Depth (Z-axis) Compensation**

The Z-axis value represents the depth of the face (distance from the camera). A **nonlinear scaling function** is used to dynamically adjust sensitivity based on distance changes.

1. **Calculate Depth Difference**:
   - `delta_z = origin_z - z_nose`

2. **Clamp Range**:
   - `delta_z_clamped = max(min(delta_z, 0.2), -0.2)`

3. **Nonlinear Scaling**:
   - A logarithmic function is used to compress depth sensitivity:
     - `scaled_z = -2 * log(1 + abs(delta_z_clamped))` (delta_z_clamped < 0)
     - `scaled_z = log(1 + abs(delta_z_clamped))` (delta_z_clamped >= 0)

4. **Adjust Sensitivity**:
   - Sensitivity is adjusted dynamically for the `x` and `y` axes:
     - `range_x, range_y = base_range * (1 + scaled_z * k)`
     - Here, `k` is the scaling factor.

---

### Step 3: **Mapping to Monitor Coordinates**

The corrected iris movement is mapped to monitor resolution using linear interpolation:

- `cursor_x = interp(-delta_x, [-range_x, range_x], [0, screen_width])`
- `cursor_y = interp(delta_y, [-range_y, range_y], [0, screen_height])`

---

### Step 4: **Smoothing with Exponential Moving Average (EMA)**

To make cursor movement smoother, **Exponential Moving Average (EMA)** is applied:

- `smooth_x = alpha * mean_x + (1 - alpha) * raw_x`
- `smooth_y = alpha * mean_y + (1 - alpha) * raw_y`

Where:
- `alpha`: Smoothing factor (0 < alpha <= 1).
- `mean_x`, `mean_y`: Recent average cursor positions.

---

## Mathematical Proof: Z-axis Compensation

### Problem:
Distance changes between the user and the camera cause excessive or insufficient iris movement, leading to inaccurate cursor tracking.

### Solution:
Logarithmic transformation reduces sensitivity to large depth changes while providing smooth responses to smaller changes. Transformation function:
- `f(delta_z) = sign(delta_z) * log(1 + abs(delta_z))`

Key properties of this function:
1. **Continuity**: Ensures smooth sensitivity changes.
2. **Monotonicity**: Retains the order of values after transformation.

The scaling factor `k` ensures sensitivity adjustments remain within a valid range. Additionally, clamping `delta_z` controls extreme depth differences.

---

## Results

- **Accurate Tracking**: Calibration ensures the cursor is correctly mapped to the monitor center.
- **Dynamic Sensitivity**: Nonlinear Z-axis scaling maintains consistent cursor movement at varying distances.
- **Smooth Movement**: EMA eliminates jitter, enhancing user experience.

---

## Warnings
- **Webcam performance** may affect the experience.
- **Monitor size** can sometimes influence the perceived tracking accuracy.

---

## How to Use

1. Run the script.
2. During the calibration phase, focus on the **center of the monitor for 3 seconds**.
3. Control the cursor using iris movement.
4. If the cursor movement feels too fast or slow, adjust the **SENSITIVITY = 0.3312345** variable.

---

## Python Version and Required Libraries

- `Python: 3.8.0`
- `cv2` (OpenCV-python)
- `mediapipe`
- `pyautogui`
- `numpy`

---

This project welcomes enhancements such as sensitivity adjustment, tracking accuracy improvements, or blink detection features!

Copyright ⓒ seongkai102
