"""
gesture_lock.py
---------------
Layer 1: Biometric gesture lock (Streamlit-compatible version).

Original design used a blocking cv2.VideoCapture + cv2.imshow loop,
which works for a local desktop script but CANNOT run inside Streamlit:
  - Streamlit reruns the whole script on every interaction (no `while True`)
  - cv2.imshow() opens a native OS window, which fails on headless
    servers like Streamlit Community Cloud

This version uses st.camera_input() to grab a single frame from the
browser's webcam (works locally AND on Streamlit Cloud), then runs
MediaPipe hand-landmark detection on that single frame.

Required gesture: show exactly 2 fingers (index + middle) in the captured
photo to unlock the dashboard.

If MediaPipe / OpenCV are not installed, or no camera is available,
the system falls back to a Demo Bypass button.
"""

import numpy as np

# Try to import camera libraries -- gracefully fall back if unavailable
try:
    import cv2
    import mediapipe as mp
    CAMERA_AVAILABLE = True
except ImportError:
    CAMERA_AVAILABLE = False


def count_raised_fingers(hand_landmarks):
    """
    Counts how many fingers are raised on the detected hand.
    Uses landmark positions: fingertip vs knuckle Y-coordinate.
    If fingertip is ABOVE knuckle (lower Y value) = finger is up.
    """
    tips = [8, 12, 16, 20]    # index, middle, ring, pinky tip landmarks
    bases = [6, 10, 14, 18]   # corresponding knuckle landmarks
    count = 0
    for tip, base in zip(tips, bases):
        if hand_landmarks.landmark[tip].y < hand_landmarks.landmark[base].y:
            count += 1
    return count


def check_gesture_in_image(image_bytes):
    """
    Runs MediaPipe hand detection on a single captured image (from
    st.camera_input) and returns (authenticated: bool, finger_count: int,
    annotated_frame_rgb: np.ndarray | None).

    Authentication passes if exactly 2 fingers are detected.
    """
    if not CAMERA_AVAILABLE:
        return False, 0, None

    # Decode image bytes -> OpenCV BGR frame
    file_bytes = np.asarray(bytearray(image_bytes), dtype=np.uint8)
    frame = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
    if frame is None:
        return False, 0, None

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    mp_hands = mp.solutions.hands
    mp_draw = mp.solutions.drawing_utils

    finger_count = 0
    with mp_hands.Hands(
        static_image_mode=True,
        max_num_hands=1,
        min_detection_confidence=0.6,
    ) as hands_detector:
        result = hands_detector.process(rgb)

        if result.multi_hand_landmarks:
            for hand_lm in result.multi_hand_landmarks:
                mp_draw.draw_landmarks(rgb, hand_lm, mp_hands.HAND_CONNECTIONS)
                finger_count = count_raised_fingers(hand_lm)

    authenticated = (finger_count == 2)
    return authenticated, finger_count, rgb


def run_gesture_authentication_ui(st):
    """
    Renders the Layer 1 biometric gesture lock inside a Streamlit app.

    `st` is the streamlit module, passed in to avoid importing it here
    (keeps this module independently testable).

    Returns True once the user is authenticated (via gesture or Demo
    Bypass), False otherwise. Call this at the top of dashboard.py and
    st.stop() if it returns False.
    """
    st.markdown("### 🔒 Layer 1 — Biometric Gesture Lock")
    st.caption(
        "Show exactly **2 fingers** (index + middle) to the camera to "
        "unlock the NeuralWatch dashboard."
    )

    if not CAMERA_AVAILABLE:
        st.warning(
            "Camera libraries (opencv-python / mediapipe) are not installed "
            "in this environment. Use Demo Bypass to continue."
        )
        return st.button("🔓 Demo Bypass (Judges / No Webcam)", type="primary")

    col1, col2 = st.columns([2, 1])

    with col1:
        img_file = st.camera_input("Show 2 fingers to the camera")

    with col2:
        st.markdown("&nbsp;")
        bypass = st.button("🔓 Demo Bypass (Judges / No Webcam)")

    if bypass:
        return True

    if img_file is not None:
        authenticated, finger_count, annotated = check_gesture_in_image(
            img_file.getvalue()
        )

        if annotated is not None:
            st.image(annotated, caption=f"Fingers detected: {finger_count}")

        if authenticated:
            st.success("✅ ACCESS GRANTED — gesture verified")
            return True
        else:
            st.error(
                f"❌ Access denied. Detected {finger_count} finger(s) — "
                f"need exactly 2."
            )
            return False

    return False
