import argparse
import logging
from queue import Queue, Empty, Full
from threading import Event, Thread
import time

import cv2
import pyttsx3

from shared.parse_camera_settings import parse_camera_settings
from .classifier import Classifier
from .image_filter import ImageFilter

verbosity_levels = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
}

cam_stream = "tapo.lowres"
filter = ImageFilter(vflip=True)
classifier = Classifier()


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

        try:
            dispatch_queue.put_nowait(frame)
            logging.debug("Dispatching frame")
        except Full:
            logging.debug("Dispatch queue is full")
            try:
                dispatch_queue.get_nowait()
                dispatch_queue.put_nowait(frame)
                logging.debug("Replacing frame")
            except Empty:
                logging.debug("Race condition - queue empty")
                break

        if terminate.is_set():
            dispatch_queue.put(None)
            logging.info("Camera stream terminated")
            break

    cap.release()
    cv2.destroyAllWindows()


def processing_stream(incoming_frames: Queue, classifier: Classifier):
    while True:
        frame = incoming_frames.get()
        if frame is None:
            break
        else:
            cls = classifier.classify(frame)
            logging.debug(f"Classification: {cls}")
            for obj in cls:
                msg = f"{obj} detected"
                logging.info(msg)
                pyttsx3.speak(msg)
    logging.info("Processing thread terminated")


def main():
    frame_queue = Queue(maxsize=1)
    terminate_event = Event()

    cam_thread = Thread(
        target=camera_stream, args=(frame_queue, terminate_event, cam_stream, filter)
    )
    classifier_thread = Thread(target=processing_stream, args=(frame_queue, classifier))

    cam_thread.start()
    classifier_thread.start()

    try:
        while not terminate_event.is_set():
            time.sleep(0.1)
    except KeyboardInterrupt:
        logging.info("Ctrl+C pressed, terminating...")
        terminate_event.set()

    cam_thread.join()
    classifier_thread.join()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Real-time classification of objects from network camera stream"
    )
    parser.add_argument(
        "--verbosity",
        "-v",
        choices=verbosity_levels.keys(),
        default="info",
        help=f"Set verbosity level: {verbosity_levels}",
    )
    args = parser.parse_args()

    verbosity = args.verbosity.lower()
    level = verbosity_levels.get(verbosity, logging.INFO)
    logging.basicConfig(
        level=level, format="%(asctime)s - %(levelname)s - %(threadName)s - %(message)s"
    )
    main()
