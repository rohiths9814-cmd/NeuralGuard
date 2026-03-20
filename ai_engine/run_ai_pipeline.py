from ultralytics import YOLO
import cv2
import os

print("🚀 NeuralGuard AI Engine Starting...")

# -------- PATH CONFIG --------
VIDEO_INPUT = "test_video.mp4"
OUTPUT_DIR = "../demo_assets/demo_videos"
OUTPUT_FILE = "ai_output_day1.mp4"

os.makedirs(OUTPUT_DIR, exist_ok=True)
OUTPUT_PATH = os.path.join(OUTPUT_DIR, OUTPUT_FILE)

# -------- LOAD MODEL --------
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

while True:
    ret, frame = cap.read()
    if not ret:
        print("✅ Video processing completed")
        break

    results = model(frame)

    annotated_frame = results[0].plot()

    out.write(annotated_frame)

    cv2.imshow("NeuralGuard Vision", annotated_frame)

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
out.release()
cv2.destroyAllWindows()

print(f"🎬 Output saved at: {OUTPUT_PATH}")