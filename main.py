import cv2
import time
import math
import numpy as np
import serial
from mediapipe.python.solutions import face_mesh as mp_face_mesh

# -----------------------------
# SERIAL SETTINGS
# -----------------------------
SERIAL_PORT = "COM5"
BAUD_RATE = 9600

# -----------------------------
# SERIAL CONNECTION
# -----------------------------
try:
    esp32 = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    time.sleep(2)
    print("ESP Connected ✅")
except Exception as e:
    esp32 = None
    print("ESP NOT connected ❌", e)

# -----------------------------
# SEND DATA
# -----------------------------
last_sent = ""

def send_to_esp(message):
    global last_sent
    if esp32 is not None and last_sent != message:
        try:
            print("Sending:", message)
            esp32.write((message + "\n").encode())
            esp32.flush()
            last_sent = message
        except:
            pass

# -----------------------------
# EAR FUNCTIONS
# -----------------------------
def dist(p1, p2):
    return math.hypot(p1[0]-p2[0], p1[1]-p2[1])

def ear(eye):
    A = dist(eye[1], eye[5])
    B = dist(eye[2], eye[4])
    C = dist(eye[0], eye[3])
    return (A + B) / (2.0 * C) if C != 0 else 0.0

# -----------------------------
# MEDIAPIPE
# -----------------------------
face_mesh = mp_face_mesh.FaceMesh(
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

LEFT = [33,160,158,133,153,144]
RIGHT = [362,385,387,263,373,380]

# -----------------------------
# SETTINGS
# -----------------------------
EAR_THRESHOLD = 0.23

frame_counter = 0
closed_start = None

# -----------------------------
# CAMERA
# -----------------------------
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    results = face_mesh.process(rgb)

    status = "No Face"
    color = (0,255,255)
    avg_ear = 0

    if results.multi_face_landmarks:
        face = results.multi_face_landmarks[0]
        h,w,_ = frame.shape

        left_eye = [(int(face.landmark[i].x*w), int(face.landmark[i].y*h)) for i in LEFT]
        right_eye = [(int(face.landmark[i].x*w), int(face.landmark[i].y*h)) for i in RIGHT]

        # 👁 GREEN POINTS
        for (x,y) in left_eye:
            cv2.circle(frame, (x,y), 2, (0,255,0), -1)
        for (x,y) in right_eye:
            cv2.circle(frame, (x,y), 2, (0,255,0), -1)

        avg_ear = (ear(left_eye) + ear(right_eye)) / 2
        current_time = time.time()

        # -----------------------------
        # SMOOTHING
        # -----------------------------
        if avg_ear < EAR_THRESHOLD:
            frame_counter += 1
        else:
            frame_counter = 0
            closed_start = None

            # ✅ SEND AWAKE ONLY ONCE
            if last_sent != "AWAKE":
                send_to_esp("AWAKE")

        # -----------------------------
        # DROWSINESS LOGIC
        # -----------------------------
        if frame_counter > 3:
            if closed_start is None:
                closed_start = current_time

            duration = current_time - closed_start

            # 🔵 DROWSY
            if 0.2 < duration < 0.5:
                status = "DROWSY"
                color = (255,0,0)
                send_to_esp("SHORT")

            # 🔴 DEEP SLEEP
            elif 0.5 <= duration < 1.5:
                status = "DEEP SLEEP"
                color = (0,0,255)
                send_to_esp("LONG")

            # ⚠️ MICROSLEEP
            elif duration >= 1.5:
                status = "MICROSLEEP"
                color = (0,0,150)
                send_to_esp("MICROSLEEP")

        else:
            status = "AWAKE"
            color = (0,255,0)

    # -----------------------------
    # DISPLAY
    # -----------------------------
    cv2.putText(frame, status, (20,40),
                cv2.FONT_HERSHEY_SIMPLEX,1,color,2)

    cv2.putText(frame, f"EAR: {avg_ear:.2f}", (20,80),
                cv2.FONT_HERSHEY_SIMPLEX,0.7,(255,255,255),2)

    cv2.imshow("Drowsiness Detection", frame)

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
if esp32:
    esp32.close()
cv2.destroyAllWindows()