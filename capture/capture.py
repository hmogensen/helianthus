import os
import toml

from .camera_manager import camera_settings_path  # , get_credentials
from .interim_password_manager import get_credentials
from .mock_network_camera import MockNetworkCamera
from .network_camera import NetworkCamera


def create_network_camera(
    cam_stream: str,
    description: str,
    flush_frames: int,
    image_interval_s: float,
    test: bool = False,
):

    if not os.path.isfile(camera_settings_path):
        raise FileNotFoundError(f"File {camera_settings_path} not found")
    with open(camera_settings_path, "r") as f:
        config = toml.load(f)

    if "." in cam_stream:
        camera_type, stream_type = cam_stream.split(".", 1)
    else:
        camera_type = cam_stream
        stream_type = None

    if camera_type not in config:
        raise ValueError(
            f"Camera type '{camera_type}' not found in {camera_settings_path}"
        )

    cam_ip = config[camera_type]["ip"]
    if stream_type and stream_type in config[camera_type]:
        stream_path = config[camera_type][stream_type]["stream_path"]
    elif "stream_path" in config[camera_type]:
        stream_path = config[camera_type]["stream_path"]
    else:
        raise ValueError(f"Stream '{stream_type}' not found for camera '{camera_type}'")
    username, password = get_credentials(camera_type)
    if not username or not password:
        raise ValueError(
            f"No credentials found for camera '{camera_type}'. Use: python camera_manager.py save {camera_type}"
        )

    if "port" in config[camera_type]:
        port = config[camera_type]["port"]
        rtsp_url = f"rtsp://{username}:{password}@{cam_ip}:{port}/{stream_path}"
    else:
        rtsp_url = f"rtsp://{username}:{password}@{cam_ip}/{stream_path}"

    input_args = {
        "url": rtsp_url,
        "description": description,
        "flush_frames": flush_frames,
        "image_interval_s": image_interval_s,
    }
    if test:
        cam = MockNetworkCamera(**input_args)
    else:
        cam = NetworkCamera(**input_args)
    return cam


def record_timelapse(cam: NetworkCamera, persistent: bool, snapshot: bool):
    if snapshot:
        cam.snapshot_capture()
    else:
        cam.start_capture(continuous_capture=persistent)

    return cam
