from timelapse.timelapse_capture import TimelapseCapture
from .test_video_capture import Test_cv2_VideoCapture


class TestTimelapseCapture(TimelapseCapture):

    def __init__(self, test_mode: str = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.test_mode = test_mode

    def _create_capture(self):
        return Test_cv2_VideoCapture(test_mode=self.test_mode)
