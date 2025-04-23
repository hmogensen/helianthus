import cv2
import time
import logging
import os
import numpy as np

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class NetworkCamera:

    def __init__(self, *, url:str, location:str, flush_frames:int, image_interval_s:float):
        self.url = url
        self.location = location
        self.is_connected = False
        self.cap = None
        self.flush_frames = flush_frames
        self.image_interval_s = image_interval_s

        self.nbr_of_failed_captures = 0
        self.delay_start_s = 0
        self.last_frame = None

        os.makedirs(self.location, exist_ok=True)

    def start_capture(self, persistent=True):
        if persistent:
            self.persistent_capture()
        else:
            self.intermittent_capture()

    def persistent_capture(self):
        self.open_capture()
        while True:
            try:
                success = self.capture_image()
                if success:
                    self.nbr_of_failed_captures = 0
                    self.delay_start_s = 0
                    time.sleep(self.image_interval_s)
                else:
                    self.nbr_of_failed_captures += 1
                    self.restart()
            except Exception as exc:
                logger.exception("Exception during persistent capture")
                self.restart()

    def intermittent_capture(self):
        while True:
            try:
                self.capture_single_image()
                time.sleep(self.image_interval_s)
            except Exception as exc:
                logger.exception("Exception during intermittent capture")
                time.sleep(10)

    def capture_image(self):
        if self.flush_frames:
            time.sleep(1)
            for i in range(self.flush_frames):
                success = self.cap.grab()
                if not success:
                    logger.debug(f"Flushing error {i} / self.flush_frames")
            time.sleep(1)

        success, frame = self.cap.read()
        if success:
            if self.last_frame is not None and np.array_equal(frame, self.last_frame):
                logger.error("Captured frame is identical to previous frame")
                raise ValueError("Buffer error: Identical consecutive frames detected")

            timestamp = time.strftime("%Y-%m-%d-%H-%M-%S")
            filename = os.path.join(self.location, f"{self.location}-{timestamp}.png")
            cv2.imwrite(filename, frame)
            self.last_frame = frame
            logger.info(f"Saved image: {filename}")
        else:
            logger.error("Image capturing error")
        return success

    def open_capture(self):
        self.cap = cv2.VideoCapture(self.url)
        self.last_frame = None
        if not self.cap.isOpened():
            logger.error("Error opening rtsp stream")
            self.is_connected = False
        else:
            logger.debug("Opening capture successful")
            self.is_connected = True

    def release_capture(self):
        if self.cap is not None:
            try:
                self.cap.release()
                logger.debug("Releasing capture successful")
            except Exception as exc:
                logger.exception("Exception thrown releasing capture")
        self.cap = None
        self.is_connected = False

    def restart(self):
        if self.nbr_of_failed_captures == 3:
            self.delay_start_s = 30
        elif self.nbr_of_failed_captures > 3:
            self.delay_start_s = min(2*self.delay_start_s, 600)

        if self.delay_start_s:
            logger.info(f"{self.nbr_of_failed_captures} consecutive failed captures. Waiting {self.delay_start_s} seconds")
            time.sleep(self.delay_start_s)
        
        self.release_capture()
        time.sleep(10)
        self.open_capture()

    def capture_single_image(self):
        # May put more strain on camera hardware if used excessively
        self.open_capture()
        self.capture_image()
        self.release_capture()
