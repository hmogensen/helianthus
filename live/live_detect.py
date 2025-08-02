import cv2
import time

from queue import Queue, Empty
from threading import Event, Thread

from shared.parse_camera_settings import parse_camera_settings
from .image_filter import ImageFilter

cam_stream = "tapo.lowres"
filter = ImageFilter(vflip=True)


def camera_stream(
    dispatch_queue: Queue, terminate: Event, cam_stream: str, filter: ImageFilter
):

    rtsp_url = parse_camera_settings(cam_stream)

    cap = cv2.VideoCapture(rtsp_url)

    if not cap.isOpened():
        raise Exception("Could not open RTSP stream")

    while True:
        ret, frame = cap.read()

        if not ret:
            raise Exception("Could not grab frame")

        frame = filter.apply(frame)

        while not dispatch_queue.empty():
            try:
                dispatch_queue.get_nowait()
            except Empty:
                break
        print("Dispatching frame")
        dispatch_queue.put_nowait(frame)

        if terminate.is_set():
            dispatch_queue.put(None)
            print("Camera stream terminated")
            break

    cap.release()
    cv2.destroyAllWindows()


def processing_stream(incoming_frames: Queue):
    while True:
        frame = incoming_frames.get()
        if frame is None:
            break
        else:
            print(frame.shape)
            # Do processing
    print("Processing thread terminated")


frame_queue = Queue(maxsize=1)
terminate_event = Event()

cam_thread = Thread(
    target=camera_stream, args=(frame_queue, terminate_event, cam_stream, filter)
)
classifier_thread = Thread(target=processing_stream, args=(frame_queue,))

cam_thread.start()
classifier_thread.start()

try:
    while not terminate_event.is_set():
        time.sleep(0.1)
except KeyboardInterrupt:
    print("Ctrl+C pressed, terminating...")
    terminate_event.set()

cam_thread.join()
classifier_thread.join()
