from ultralytics import YOLO
import cv2
import os
import sys
from detection.unattended_logic import check_unattended
from utils.alert_sender import send_alert

print("🚀 NeuralGuard AI Engine Starting...")

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
VIDEO_INPUT = os.path.join(CURRENT_DIR, "test_video.mp4")

OUTPUT_DIR = os.path.join(CURRENT_DIR, "..", "demo_assets", "demo_videos")
OUTPUT_FILE = "ai_output_day3.mp4"

os.makedirs(OUTPUT_DIR, exist_ok=True)
OUTPUT_PATH = os.path.join(OUTPUT_DIR, OUTPUT_FILE)

model = YOLO("yolov8n.pt")

cap = cv2.VideoCapture(VIDEO_INPUT)

width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = int(cap.get(cv2.CAP_PROP_FPS))

out = cv2.VideoWriter(
    OUTPUT_PATH,
    cv2.VideoWriter_fourcc(*'mp4v'),
    fps,
    (width, height)
)

alert_sent_flag = False

while True:
    ret, frame = cap.read()
    if not ret:
        break

    results = model(frame)
    annotated_frame = results[0].plot()

    boxes = results[0].boxes
    persons = []
    bags = []

    if boxes is not None:
        for box, cls in zip(boxes.xyxy, boxes.cls):
            x1, y1, x2, y2 = map(int, box)
            label = int(cls)

            if label == 0:
                persons.append((x1, y1, x2, y2))

            if label == 24 or label == 26:
                bags.append((x1, y1, x2, y2))

    alerts = check_unattended(bags, persons)

    for alert in alerts:
        cv2.putText(
            annotated_frame,
            alert,
            (50, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 0, 255),
            3
        )

        if not alert_sent_flag:
            send_alert("Unattended Bag")
            alert_sent_flag = True

    out.write(annotated_frame)
    cv2.imshow("NeuralGuard Vision", annotated_frame)

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
out.release()
cv2.destroyAllWindows()

print("✅ AI Pipeline Finished")