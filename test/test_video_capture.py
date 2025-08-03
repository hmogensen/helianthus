import cv2
import numpy as np
import time

"""
Override cv2.VideoCapture
"""


class Test_cv2_VideoCapture:

    def __init__(self, *args, test_mode: str = None, **kwargs):
        self.test_mode = test_mode or "gradient"
        self.frame_count = 0
        self.is_opened = True

        if test_mode == "humanoids":
            import requests
            import os

            image_url = "https://images.unsplash.com/photo-1511632765486-a01980e01a18?w=640&h=480&fit=crop"
            try:
                response = requests.get(
                    image_url,
                    timeout=15,
                    headers={
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                    },
                )
                if response.status_code == 200:
                    temp_path = "temp_humans.jpg"
                    with open(temp_path, "wb") as f:
                        f.write(response.content)

                    img = cv2.imread(temp_path)
                    if img is not None:
                        # Resize to match our frame size
                        img = cv2.resize(img, (640, 480))
                        self.frame = img

                        os.remove(temp_path)

                    if os.path.exists(temp_path):
                        os.remove(temp_path)

            except Exception as e:
                print(f"Failed to download image {image_url}: {e}")

    def grab(self):
        if not self.is_opened:
            return False
        return False

    def read(self):
        if not self.is_opened:
            return False, None

        height, width = 480, 640
        frame = np.zeros((height, width, 3), dtype=np.uint8)

        if self.test_mode == "gradient":
            # Add gradient background
            for i in range(height):
                frame[i, :] = [i * 255 // height, 100, (height - i) * 255 // height]
        elif self.test_mode == "humanoids":
            frame = self.frame
        else:
            raise Exception(f"Illegal test mode option: {self.test_mode}")

        cv2.putText(
            frame,
            f"Frame {self.frame_count}",
            (50, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (255, 255, 255),
            2,
        )

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
