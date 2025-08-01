import cv2
import time
import logging
from .image_writer import ImageWriter

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)

logger = logging.getLogger(__name__)


class TimelapseCapture:

    def __init__(
        self, *, url: str, description: str, flush_frames: int, image_interval_s: float
    ):

        self.url = url
        self.cap = None

        self.is_connected = False
        self.flush_frames = flush_frames
        self.image_interval_s = image_interval_s

        self.nbr_of_failed_captures = 0
        self.delay_start_s = 0

        self.image_writer = ImageWriter(description=description)

    # Override to use mockup HW
    def _create_capture(self):
        return cv2.VideoCapture(self.url)

    # Use for capturing several images
    # continuous_capture means that the video capture stream is being kept open,
    #   if False the video_stream is reopened every time an image is captures
    def start_capture(self, continuous_capture=True):
        if continuous_capture:
            self._continuous_capture()
        else:
            self._intermittent_capture()

    # Capture single snapshot
    def snapshot_capture(self):
        while True:
            try:
                self._restart()
                # Check if restart was successful before proceeding in loop
                if self.is_connected:
                    success = self._capture_image()
                    # Only wait if image capture was successful
                    if success:
                        self._release_capture()
                        return

            except Exception as exc:
                logger.exception("Exception during intermittent capture")
                time.sleep(600)

            if self.nbr_of_failed_captures > 5:
                logger.exception("Cannot capture image. Aborting")
                return

    def _continuous_capture(self):
        # Open stream
        while not self.is_connected:
            try:
                self._restart()
            except Exception as exc:
                logger.exeption("Exception when opening stream")

        # Capture timelapse images
        while True:
            try:
                success = self._capture_image()
                if success:
                    self.nbr_of_failed_captures = 0
                    self.delay_start_s = 0
                    time.sleep(self.image_interval_s)
                else:
                    self.nbr_of_failed_captures += 1
                    self._restart()
            except Exception as exc:
                logger.exception("Exception during persistent capture")
                self._restart()

    def _intermittent_capture(self):
        while True:
            try:
                self._restart()
                # Check if restart was successful before proceeding in loop
                if self.is_connected:
                    success = self._capture_image()
                    # Only wait if image capture was successful
                    if success:
                        self._release_capture()
                        time.sleep(self.image_interval_s)
            except Exception as exc:
                logger.exception("Exception during intermittent capture")
                time.sleep(10)

    def _capture_image(self):
        # Workaround for tapo camera
        if self.flush_frames:
            time.sleep(1)
            for i in range(self.flush_frames):
                success = self.cap.grab()
                if not success:
                    logger.debug(f"Flushing error {i} / self.flush_frames")
            time.sleep(1)

        # Capture frame
        success, frame = self.cap.read()

        if success:
            self.image_writer.write(frame)
            logger.info("Saved image")
        else:
            logger.error("Image capturing error")
        return success

    def _open_capture(self):
        self.cap = self._create_capture()

        if not self.cap.isOpened():
            logger.error("Error opening rtsp stream")
            self.is_connected = False
        else:
            logger.debug("Opening capture successful")
            self.is_connected = True

    def _release_capture(self):
        if self.cap is not None:
            try:
                self.cap.release()
                logger.debug("Releasing capture successful")
            except Exception as exc:
                logger.exception("Exception thrown releasing capture")
        self.cap = None
        self.is_connected = False

    def _restart(self):
        # Count number of failed restarts to determine waiting time
        if self.nbr_of_failed_captures == 3:
            self.delay_start_s = 30
        elif self.nbr_of_failed_captures > 3:
            self.delay_start_s = min(2 * self.delay_start_s, 600)
        # If previous restarts failed, wait a bit longer
        if self.delay_start_s:
            logger.info(
                f"{self.nbr_of_failed_captures} consecutive failed captures. Waiting {self.delay_start_s} seconds"
            )
            time.sleep(self.delay_start_s)

        # Restart capture
        self._release_capture()
        time.sleep(10)
        self._open_capture()
