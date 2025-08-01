import cv2
import numpy as np
import time
from .network_camera import NetworkCamera


class MockVideoCapture:

    def __init__(self):
        self.frame_count = 0
        self.is_opened = True

    def grab(self):
        if not self.is_opened:
            return False
        return False

    def read(self):
        if not self.is_opened:
            return False, None

        height, width = 480, 640
        frame = np.zeros((height, width, 3), dtype=np.uint8)

        # Add gradient background
        for i in range(height):
            frame[i, :] = [i * 255 // height, 100, (height - i) * 255 // height]

        # Add frame counter
        cv2.putText(
            frame,
            f"Frame {self.frame_count}",
            (50, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (255, 255, 255),
            2,
        )

        # Add timestamp
        timestamp_text = time.strftime("%H:%M:%S")
        cv2.putText(
            frame,
            timestamp_text,
            (50, 100),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2,
        )

        self.frame_count += 1
        return True, frame

    def isOpened(self):
        return self.is_opened

    def release(self):
        self.is_opened = False


class MockNetworkCamera(NetworkCamera):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _create_capture(self):
        return MockVideoCapture()
