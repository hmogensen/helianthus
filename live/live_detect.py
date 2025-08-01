import cv2
import time

from queue import Queue
from threading import Event, Thread

from shared.parse_camera_settings import parse_camera_settings

cam_stream = "tapo.lowres"

def camera_stream(dispatch_queue:Queue, terminate:Event, cam_stream:str):
    
    rtsp_url = parse_camera_settings(cam_stream)

    cap = cv2.VideoCapture(rtsp_url)

    if not cap.isOpened():
        raise Exception("Could not open RTSP stream")

    while True:
        ret, frame = cap.read()

        if not ret:
            raise Exception("Could not grab frame")
        
        print("Dispatching frame")
        dispatch_queue.put(frame)

        if terminate.is_set():
            dispatch_queue.put(None)
            print("Camera stream terminated")
            break

    cap.release()
    cv2.destroyAllWindows()

def processing_stream(incoming_stream:Queue):
    while True:
        task = incoming_stream.get()
        if task is None:
            break
        else:
            print(task.shape)
            # Do processing
    print("Processing thread terminated")

data_queue = Queue()
terminate_event = Event()

cam_thread = Thread(target=camera_stream, args=(data_queue, terminate_event, cam_stream))
processing_thread = Thread(target=processing_stream, args=(data_queue,))

cam_thread.start()
processing_thread.start()

try:
    while not terminate_event.is_set():
        time.sleep(0.1)
except KeyboardInterrupt:
    print("Ctrl+C pressed, terminating...")
    terminate_event.set()

cam_thread.join()
processing_thread.join()

