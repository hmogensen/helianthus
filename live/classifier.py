from ultralytics import YOLO


class Classifier:

    def __init__(self, confidence_threshold: float = 0.5):
        self.confidence_threshold = confidence_threshold
        self.model = YOLO("yolov8n.pt")

    def classify(self, frame):
        results = self.model(frame, verbose=False)
        boxes = results[0].boxes
        if boxes is None:
            return []
        boxes = boxes[boxes.conf > self.confidence_threshold]
        if len(boxes) == 0:
            return []
        return boxes.cls.unique().tolist()
