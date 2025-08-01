import cv2
import numpy as np
from tqdm import tqdm
from ultralytics import YOLO

from video.video_toml import parse_video_settings

model = YOLO("yolov8n.pt")
YOLO_HUMAN_CLASS = 0
YOLO_CONF_THRESHOLD = 0.5

tag = "garden-lowres"
template = parse_video_settings(tag)


def detect_humans(results):
    if results[0].boxes is None:
        return []
    person_boxes = results[0].boxes[
        (results[0].boxes.cls == YOLO_HUMAN_CLASS)
        & (results[0].boxes.conf > YOLO_CONF_THRESHOLD)
    ]
    return person_boxes


for frame, t in tqdm(
    template.process_frames(ts=True),
    desc="Processing frames",
    total=len(template.images),
):
    results = model(frame, verbose=False)
    person_boxes = detect_humans(results)

    if len(person_boxes) > 0:

        for box in person_boxes:
            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)
            confidence = box.conf[0].cpu().numpy()
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(
                frame,
                f"Person {confidence:.2f}",
                (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 255, 0),
                1,
            )

        print("Human detected")
        cv2.imshow("Human", frame)
        cv2.waitKey(1)
cv2.destroyAllWindows()

print("done")
