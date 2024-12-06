
# Eye_tracking_by_mediapipe

## 개요

이 프로젝트는 **MediaPipe Face Mesh**를 활용하여 사용자의 홍채 움직임을 추적하고 이를 모니터 좌표로 맵핑합니다. 카메라와의 거리(Z축)에 따른 민감도 변화를 비선형 변환으로 보정하고, 지수 이동 평균(EMA)을 통해 커서의 움직임을 부드럽게 조정합니다.

---

## 과정 설명

### 1단계: **캘리브레이션**

1. **홍채 중심 좌표 추출**:
   - MediaPipe의 `face_mesh`를 이용해 **좌우 홍채**의 좌표를 추출합니다.
   - 두 홍채의 평균값을 계산합니다:
     \[
     x_{	ext{iris}} = rac{x_{	ext{right}} + x_{	ext{left}}}{2}, \quad 
     y_{	ext{iris}} = rac{y_{	ext{right}} + y_{	ext{left}}}{2}
     \]

2. **기준점 설정**:
   - **3초 동안** 사용자가 모니터 중심을 응시하며 홍채 좌표를 수집합니다.
   - 수집된 좌표의 평균값을 기준점으로 설정합니다:
     \[
     	ext{origin}_x = rac{\sum_{i=1}^N x_{	ext{iris}, i}}{N}, \quad 
     	ext{origin}_y = rac{\sum_{i=1}^N y_{	ext{iris}, i}}{N}, \quad
     	ext{origin}_z = rac{\sum_{i=1}^N z_{	ext{nose}, i}}{N}
     \]

---

### 2단계: **깊이(Z축) 보정**

Z축 값은 얼굴의 깊이(카메라로부터의 거리)를 나타냅니다. 거리 변화에 따라 민감도를 동적으로 조정하기 위해 **비선형 스케일링** 함수를 사용합니다.

1. **깊이 차이 계산**:
   - 현재 코의 깊이와 캘리브레이션된 깊이 간의 차이를 계산합니다:
     \[
     \Delta z = 	ext{origin}_z - z_{	ext{nose}}
     \]

2. **범위 제한**:
   - 극단적인 민감도를 방지하기 위해 \(\Delta z\)의 범위를 제한합니다:
     \[
     \Delta z_{	ext{clamped}} = \max(\min(\Delta z, 0.2), -0.2)
     \]

3. **비선형 스케일링**:
   - 로그 함수를 사용해 깊이 민감도를 압축합니다:
     \[
     	ext{scaled\_z} = 
     egin{cases} 
     -2 \cdot \log(1 + |\Delta z_{	ext{clamped}}|), & \Delta z_{	ext{clamped}} < 0 \\
     \log(1 + |\Delta z_{	ext{clamped}}|), & \Delta z_{	ext{clamped}} \geq 0 
     \end{cases}
     \]

4. **민감도 조정**:
   - 깊이에 따라 \(x\)- 및 \(y\)-축 민감도를 조정합니다:
     \[
     	ext{range}_x, 	ext{range}_y = 	ext{base\_range} \cdot (1 + 	ext{scaled\_z} \cdot k)
     \]
     여기서 \(k\)는 스케일링 계수입니다.

---

### 3단계: **모니터 좌표로 맵핑**

보정된 홍채 움직임을 선형 보간법을 이용해 모니터 해상도에 매핑합니다:

\(
	ext{cursor\_x} = 	ext{interp}(-\Delta x, [-	ext{range}_x, 	ext{range}_x], [0, 	ext{screen\_width}])
\)
\(
	ext{cursor\_y} = 	ext{interp}(\Delta y, [-	ext{range}_y, 	ext{range}_y], [0, 	ext{screen\_height}])
\)

---

### 4단계: **지수 이동 평균(EMA)을 이용한 움직임 부드럽게 하기**

커서의 움직임을 부드럽게 만들기 위해 **지수 이동 평균(EMA)**을 적용합니다:

\(
	ext{smooth\_x} = lpha \cdot 	ext{mean\_x} + (1 - lpha) \cdot 	ext{raw\_x}
\)
\(
	ext{smooth\_y} = lpha \cdot 	ext{mean\_y} + (1 - lpha) \cdot 	ext{raw\_y}
\)

여기서:
- \(lpha\): 부드럽게 조정하는 계수 (\(0 < lpha \leq 1\)).
- \(	ext{mean\_x}, 	ext{mean\_y}\): 최근 커서 위치의 평균.

---

## 수학적 증명: Z축 보정

### 문제:
사용자의 카메라와의 거리가 변하면 홍채 움직임이 과도하게 커지거나 작아져서 커서 이동이 부정확해질 수 있습니다.

### 해결:
로그 변환은 큰 깊이 변화에 대한 민감도를 줄이고, 작은 변화에는 부드러운 반응을 제공합니다. 함수:
\(
f(\Delta z) = 	ext{sign}(\Delta z) \cdot \log(1 + |\Delta z|)
\)
는 다음과 같은 특성을 가집니다:
1. **연속성**: 민감도 변화가 갑작스럽지 않습니다.
2. **단조성**: 변환 후에도 값의 순서가 유지됩니다.

스케일링 계수 \(k\)를 통해 민감도 조정이 유효 범위 내에 머물도록 합니다. 또한, \(\Delta z\)를 제한하여 극단적인 깊이 차이를 제어합니다.

---

## 결과

- **정확한 트래킹**: 캘리브레이션을 통해 커서가 정확히 모니터 중심에 맵핑됩니다.
- **동적 민감도**: Z축 비선형 스케일링을 통해 다양한 거리에서도 커서 이동이 일관됩니다.
- **부드러운 움직임**: EMA로 커서의 떨림을 제거하고 사용자 경험을 향상시킵니다.

---

## 사용 방법

1. 스크립트를 실행합니다.
2. 캘리브레이션 단계에서 **3초간 모니터 중앙**을 응시합니다.
3. 홍채 움직임으로 커서를 조작합니다.

---

## 의존성

- `cv2` (OpenCV)
- `mediapipe`
- `pyautogui`
- `numpy`

---

프로젝트의 민감도 조정, 추적 정확도 개선 또는 블링크 감지와 같은 추가 기능을 환영합니다!
