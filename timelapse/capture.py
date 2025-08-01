from .mock_timelapse_camera import MockNetworkCamera
from .timelapse_capture import TimelapseCapture
from shared.parse_camera_settings import parse_camera_settings


def create_network_camera(
    cam_stream: str,
    description: str,
    flush_frames: int,
    image_interval_s: float,
    test: bool = False,
):

    rtsp_url = parse_camera_settings(cam_stream)
    input_args = {
        "url": rtsp_url,
        "description": description,
        "flush_frames": flush_frames,
        "image_interval_s": image_interval_s,
    }
    if test:
        cam = MockNetworkCamera(**input_args)
    else:
        cam = TimelapseCapture(**input_args)
    return cam


def record_timelapse(cam: TimelapseCapture, persistent: bool, snapshot: bool):
    if snapshot:
        cam.snapshot_capture()
    else:
        cam.start_capture(continuous_capture=persistent)

    return cam
