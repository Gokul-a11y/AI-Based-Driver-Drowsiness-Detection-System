import cv2
import numpy as np
from tensorflow.keras.models import load_model

# =========================
# LOAD MODEL
# =========================
model = load_model("drowsiness_model.h5")

# =========================
# FACE DETECTOR
# =========================
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

# =========================
# CAMERA
# =========================
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("❌ Camera not working")
    exit()

# =========================
# SETTINGS
# =========================
drowsy_count = 0
THRESHOLD_FRAMES = 5   # stability
PRED_THRESHOLD = 0.2   # 🔥 IMPORTANT FIX

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    status = "No Face"

    for (x, y, w, h) in faces:
        face = frame[y:y+h, x:x+w]

        # preprocess
        face = cv2.resize(face, (64, 64))
        face = face / 255.0
        face = np.reshape(face, (1, 64, 64, 3))

        prediction = model.predict(face, verbose=0)[0][0]

        # DEBUG (see values)
        print("Prediction:", prediction)

        # =========================
        # FINAL FIXED LOGIC
        # =========================
        if prediction < PRED_THRESHOLD:
            drowsy_count += 1
        else:
            drowsy_count = 0

        if drowsy_count >= THRESHOLD_FRAMES:
            status = "DROWSY"
            color = (0, 0, 255)
        else:
            status = "AWAKE"
            color = (0, 255, 0)

        # draw box
        cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
        cv2.putText(frame, status, (x, y-10),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

    cv2.imshow("Drowsiness Detection", frame)

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()