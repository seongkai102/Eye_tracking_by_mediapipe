import cv2
import numpy as np
import mediapipe as mp
import pyautogui
from collections import deque
import math
import time

def get_average_iris_center(landmarks, image_shape):
    right_iris = landmarks[RIGHT_IRIS_CENTER_IDX]
    left_iris = landmarks[LEFT_IRIS_CENTER_IDX]
    avg_x = ((right_iris.x + left_iris.x) / 2) * image_shape[1]
    avg_y = ((right_iris.y + left_iris.y) / 2) * image_shape[0]
    return avg_x, avg_y

def adjust_range_by_distance(delta_z, base_range_x=1.0, base_range_y=1.0):
    scaling_factor = 0.02
    clamped_delta_z = max(min(delta_z, 0.2), -0.2)

    if clamped_delta_z < 0:
        scaled_delta_z = math.log1p(abs(clamped_delta_z)) * (-2)
    else:
        scaled_delta_z = math.log1p(abs(clamped_delta_z))

    factor = 1 + (-scaled_delta_z) * scaling_factor
    return base_range_x * factor, base_range_y * factor


pyautogui.FAILSAFE = False

mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(
    static_image_mode=False,
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.3,
    min_tracking_confidence=0.5
)

RIGHT_IRIS_CENTER_IDX = 470
LEFT_IRIS_CENTER_IDX = 475
NOSE_LANDMARK = 6

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 1)
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1) 

screen_width, screen_height = pyautogui.size()

origin_x, origin_y, origin_z = 0, 0, 0
x_values = deque(maxlen=10)
y_values = deque(maxlen=10)
z_values = deque(maxlen=10)

# 개수 늘릴수록 정확도 증가 그러나 감도(민감도)는 감소
mouse_x_history = deque(maxlen=9)
mouse_y_history = deque(maxlen=9)

SMOOTHING_ALPHA = 1

# 기준점 설정
def center():
    start_time = None
    while True:
        
        global origin_x, origin_y, origin_z
        success, image = cap.read()
        if not success:
            raise Exception("카메라를 열 수 없습니다.")

        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(rgb_image)

        if results.multi_face_landmarks:
            if start_time is None:  # 시작 시간 설정
                start_time = time.time()

            elapsed_time = time.time() - start_time
            if elapsed_time <= 3:  # 3초 동안만 데이터 추가
                landmarks = results.multi_face_landmarks[0].landmark
                current_x, current_y = get_average_iris_center(landmarks, image.shape)
                current_z = landmarks[NOSE_LANDMARK].z

                x_values.append(current_x)
                y_values.append(current_y)
                z_values.append(current_z)

                if len(x_values) == x_values.maxlen:
                    origin_x = sum(x_values) / len(x_values)
                    origin_y = sum(y_values) / len(y_values)
                    origin_z = sum(z_values) / len(z_values)
                    print(origin_x, origin_y, origin_z)
                    break
            else:
                print("3초가 지났습니다. 데이터 추가 중지.")
                break

        if cv2.waitKey(10) & 0xFF == 27:
            break

def eye_track():
    # 메인 실행
    while cap.isOpened():
        success, image = cap.read()
        if not success:
            break

        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(rgb_image)

        if results.multi_face_landmarks:
            landmarks = results.multi_face_landmarks[0].landmark
            current_x, current_y = get_average_iris_center(landmarks, image.shape)
            current_z = landmarks[NOSE_LANDMARK].z

            delta_z = origin_z - current_z
            range_x, range_y = adjust_range_by_distance(delta_z)

            SENSITIVITY_FACTOR = 0.3312345   # 감도 조절 인자 (0과 1 사이의 값)

            delta_x = (current_x - origin_x) * SENSITIVITY_FACTOR
            delta_y = (current_y - origin_y) * SENSITIVITY_FACTOR

            raw_mouse_x = np.interp(-delta_x, [-range_x, range_x], [-1, screen_width])
            raw_mouse_y = np.interp(delta_y, [-range_y, range_y], [0, screen_height])

            mouse_x_history.append(raw_mouse_x)
            mouse_y_history.append(raw_mouse_y)

            smoothed_mouse_x = SMOOTHING_ALPHA * np.mean(mouse_x_history) + (1 - SMOOTHING_ALPHA) * raw_mouse_x
            smoothed_mouse_y = SMOOTHING_ALPHA * np.mean(mouse_y_history) + (1 - SMOOTHING_ALPHA) * raw_mouse_y

            pyautogui.moveTo(smoothed_mouse_x, smoothed_mouse_y)

            cv2.imshow('show', image)
            if smoothed_mouse_x == -1.0:
                print(1)
                break

        else:
            cv2.imshow('show', image)

        if cv2.waitKey(1) & 0xFF == 27:  # ESC 키를 누르면 종료
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    center()
    eye_track()