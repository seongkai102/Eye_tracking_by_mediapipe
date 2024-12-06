Eye_tracking_by_mediapipe
Overview
This project tracks eye movements using MediaPipe Face Mesh to map iris positions to monitor coordinates. It adjusts for depth (Z-axis) changes using a non-linear transformation and smooths cursor movements via an exponential moving average (EMA) to ensure comfortable and responsive control.

Process Description
Step 1: Calibration
Extract Iris Center Coordinates:

Using MediaPipe's face_mesh, the coordinates of the left and right irises are extracted.
The average of the two irises is calculated:
𝑥
iris
=
𝑥
right
+
𝑥
left
2
,
𝑦
iris
=
𝑦
right
+
𝑦
left
2
x 
iris
​
 = 
2
x 
right
​
 +x 
left
​
 
​
 ,y 
iris
​
 = 
2
y 
right
​
 +y 
left
​
 
​
 
Set Origin:

For 3 seconds, iris positions are collected while the user focuses on the center of the monitor.
The average of collected values is used as the origin:
origin
𝑥
=
∑
𝑖
=
1
𝑁
𝑥
iris
,
𝑖
𝑁
,
origin
𝑦
=
∑
𝑖
=
1
𝑁
𝑦
iris
,
𝑖
𝑁
,
origin
𝑧
=
∑
𝑖
=
1
𝑁
𝑧
nose
,
𝑖
𝑁
origin 
x
​
 = 
N
∑ 
i=1
N
​
 x 
iris,i
​
 
​
 ,origin 
y
​
 = 
N
∑ 
i=1
N
​
 y 
iris,i
​
 
​
 ,origin 
z
​
 = 
N
∑ 
i=1
N
​
 z 
nose,i
​
 
​
 
Step 2: Depth (Z-Axis) Adjustment
The Z-axis value represents the depth of the face (distance from the camera). To account for varying distances, a non-linear scaling function is applied to adjust the movement sensitivity dynamically.

Depth Difference:

Calculate the difference between the current nose depth and the calibrated depth:
Δ
𝑧
=
origin
𝑧
−
𝑧
nose
Δz=origin 
z
​
 −z 
nose
​
 
Clamping:

Limit the range of 
Δ
𝑧
Δz to prevent extreme sensitivity:
Δ
𝑧
clamped
=
max
⁡
(
min
⁡
(
Δ
𝑧
,
0.2
)
,
−
0.2
)
Δz 
clamped
​
 =max(min(Δz,0.2),−0.2)
Non-Linear Scaling:

Use the logarithmic function to compress depth sensitivity:
scaled_z
=
{
−
2
⋅
log
⁡
(
1
+
∣
Δ
𝑧
clamped
∣
)
,
Δ
𝑧
clamped
<
0
log
⁡
(
1
+
∣
Δ
𝑧
clamped
∣
)
,
Δ
𝑧
clamped
≥
0
scaled_z={ 
−2⋅log(1+∣Δz 
clamped
​
 ∣),
log(1+∣Δz 
clamped
​
 ∣),
​
  
Δz 
clamped
​
 <0
Δz 
clamped
​
 ≥0
​
 
Adjust Range:

Modify the sensitivity range for 
𝑥
x- and 
𝑦
y-axis based on depth:
range
𝑥
,
range
𝑦
=
base_range
⋅
(
1
+
scaled_z
⋅
𝑘
)
range 
x
​
 ,range 
y
​
 =base_range⋅(1+scaled_z⋅k)
where 
𝑘
k is a scaling factor.
Step 3: Mapping to Screen Coordinates
The adjusted iris movement is mapped to the monitor's resolution using linear interpolation:

cursor_x
=
interp
(
−
Δ
𝑥
,
[
−
range
𝑥
,
range
𝑥
]
,
[
0
,
screen_width
]
)
cursor_x=interp(−Δx,[−range 
x
​
 ,range 
x
​
 ],[0,screen_width])
cursor_y
=
interp
(
Δ
𝑦
,
[
−
range
𝑦
,
range
𝑦
]
,
[
0
,
screen_height
]
)
cursor_y=interp(Δy,[−range 
y
​
 ,range 
y
​
 ],[0,screen_height])
Step 4: Smoothing with Exponential Moving Average (EMA)
To avoid jittery cursor movement, we apply exponential moving average smoothing:

smooth_x
=
𝛼
⋅
mean_x
+
(
1
−
𝛼
)
⋅
raw_x
smooth_x=α⋅mean_x+(1−α)⋅raw_x
smooth_y
=
𝛼
⋅
mean_y
+
(
1
−
𝛼
)
⋅
raw_y
smooth_y=α⋅mean_y+(1−α)⋅raw_y
Here:

𝛼
α is the smoothing factor (
0
<
𝛼
≤
1
0<α≤1).
mean_x
mean_x and 
mean_y
mean_y are the averages of recent cursor positions.
Mathematical Proof of Z-Axis Adjustment
Problem:
If the user's distance from the camera changes, the iris movements appear exaggerated or reduced. This results in inaccurate cursor movement.

Solution:
The logarithmic transformation reduces sensitivity for large depth differences while maintaining smoothness for small changes. The function:

𝑓
(
Δ
𝑧
)
=
sign
(
Δ
𝑧
)
⋅
log
⁡
(
1
+
∣
Δ
𝑧
∣
)
f(Δz)=sign(Δz)⋅log(1+∣Δz∣)
is:

Continuous: Ensures no abrupt jumps in sensitivity.
Monotonic: Prevents reversed mappings.
The scaling factor 
𝑘
k ensures sensitivity adjustment remains within usable bounds. By clamping 
Δ
𝑧
Δz, extreme depth differences are controlled.

Results
Calibrated Tracking: The calibration ensures the cursor maps correctly to the monitor's center.
Dynamic Sensitivity: Non-linear Z-axis scaling provides consistent cursor behavior regardless of user distance.
Smooth Movement: EMA eliminates jitter and improves usability.
Usage
Run the script.
Focus on the monitor's center for 3 seconds during calibration.
Move your eyes to control the cursor position.
Dependencies
cv2 (OpenCV)
mediapipe
pyautogui
numpy