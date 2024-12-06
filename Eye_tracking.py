# Copyright ⓒ seongkai102

import cv2
import numpy as np
import mediapipe as mp
import pyautogui
from collections import deque
import math
import time

def get_average_iris_position(landmarks, frame_shape):
    right_eye_center = landmarks[RIGHT_EYE_IDX]
    left_eye_center = landmarks[LEFT_EYE_IDX]
    avg_x = ((right_eye_center.x + left_eye_center.x) / 2) * frame_shape[1]
    avg_y = ((right_eye_center.y + left_eye_center.y) / 2) * frame_shape[0]
    return avg_x, avg_y

def calculate_range_adjustment(depth_difference, base_x_range=1.0, base_y_range=1.0):
    adjustment_factor = 0.02
    clamped_depth_difference = max(min(depth_difference, 0.2), -0.2)

    if clamped_depth_difference < 0:
        scaled_depth_difference = math.log1p(abs(clamped_depth_difference)) * (-2)
    else:
        scaled_depth_difference = math.log1p(abs(clamped_depth_difference))

    scale = 1 + (-scaled_depth_difference) * adjustment_factor
    return base_x_range * scale, base_y_range * scale


pyautogui.FAILSAFE = False

mp_face_mesh = mp.solutions.face_mesh
face_detection = mp_face_mesh.FaceMesh(
    static_image_mode=False,
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.3,
    min_tracking_confidence=0.5
)

RIGHT_EYE_IDX = 470
LEFT_EYE_IDX = 475
NOSE_IDX = 6

camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)
camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
camera.set(cv2.CAP_PROP_AUTO_EXPOSURE, 1)
camera.set(cv2.CAP_PROP_BUFFERSIZE, 1) 

screen_width, screen_height = pyautogui.size()

calibrated_x, calibrated_y, calibrated_depth = 0, 0, 0
x_coords = deque(maxlen=10)
y_coords = deque(maxlen=10)
depth_coords = deque(maxlen=10)

mouse_x_movements = deque(maxlen=9)
mouse_y_movements = deque(maxlen=9)

SMOOTHING_WEIGHT = 1

def calibrate_center():
    start_time = None
    while True:
        
        global calibrated_x, calibrated_y, calibrated_depth
        success, frame = camera.read()
        if not success:
            raise Exception("no camera")

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_detection.process(rgb_frame)

        if results.multi_face_landmarks:
            if start_time is None:  # start time set
                start_time = time.time()

            elapsed_time = time.time() - start_time
            if elapsed_time <= 3:  # data append for a 3 second
                face_landmarks = results.multi_face_landmarks[0].landmark
                current_x, current_y = get_average_iris_position(face_landmarks, frame.shape)
                current_depth = face_landmarks[NOSE_IDX].z

                x_coords.append(current_x)
                y_coords.append(current_y)
                depth_coords.append(current_depth)

                if len(x_coords) == x_coords.maxlen:
                    calibrated_x = sum(x_coords) / len(x_coords)
                    calibrated_y = sum(y_coords) / len(y_coords)
                    calibrated_depth = sum(depth_coords) / len(depth_coords)
                    print(calibrated_x, calibrated_y, calibrated_depth)
                    break
            else:
                print("stop")
                break

        if cv2.waitKey(10) & 0xFF == 27:
            break

def track_eye_movement():
    while camera.isOpened():
        success, frame = camera.read()
        if not success:
            break

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_detection.process(rgb_frame)

        if results.multi_face_landmarks:
            face_landmarks = results.multi_face_landmarks[0].landmark
            current_x, current_y = get_average_iris_position(face_landmarks, frame.shape)
            current_depth = face_landmarks[NOSE_IDX].z

            depth_difference = calibrated_depth - current_depth
            x_range, y_range = calculate_range_adjustment(depth_difference)

            SENSITIVITY = 0.3312345  # 감도 조절 인자 (range : 0~1)

            x_offset = (current_x - calibrated_x) * SENSITIVITY
            y_offset = (current_y - calibrated_y) * SENSITIVITY

            raw_mouse_x = np.interp(-x_offset, [-x_range, x_range], [-1, screen_width])
            raw_mouse_y = np.interp(y_offset, [-y_range, y_range], [0, screen_height])

            mouse_x_movements.append(raw_mouse_x)
            mouse_y_movements.append(raw_mouse_y)

            smoothed_mouse_x = SMOOTHING_WEIGHT * np.mean(mouse_x_movements) + (1 - SMOOTHING_WEIGHT) * raw_mouse_x
            smoothed_mouse_y = SMOOTHING_WEIGHT * np.mean(mouse_y_movements) + (1 - SMOOTHING_WEIGHT) * raw_mouse_y

            pyautogui.moveTo(smoothed_mouse_x, smoothed_mouse_y)

            cv2.imshow('show', frame)
            if smoothed_mouse_x == -1.0:
                print(1)
                break

        else:
            cv2.imshow('show', frame)

        if cv2.waitKey(1) & 0xFF == 27:  # ESC 키를 누르면 종료
            break

    camera.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    calibrate_center()
    track_eye_movement()
