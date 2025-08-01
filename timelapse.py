import argparse
from capture.capture import create_network_camera, record_timelapse

default_flush_frames = 0
default_image_interval_s = 600

if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Time lapse recording with network cameras"
    )
    parser.add_argument("cam", help="Camera id")
    parser.add_argument(
        "descr",
        type=str,
        help='Location (e.g. "garden") or portrayed object (e.g. "sprouting plant")',
    )
    parser.add_argument("--test", "-t", action="store_true", default=False)
    parser.add_argument(
        "--snapshot",
        "-s",
        action="store_true",
        default=False,
        help="Capture single frame",
    )
    parser.add_argument(
        "--interval",
        "-i",
        type=int,
        default=default_image_interval_s,
        help=f"Interval between image captures in seconds. Default: {default_image_interval_s}",
    )
    parser.add_argument(
        "--restart-every-cycle",
        "-r",
        action="store_true",
        help="Restart the camera connection on every capture cycle",
    )
    parser.add_argument(
        "--flush",
        "-f",
        type=int,
        default=default_flush_frames,
        help=f"Number of frames to flush. Default: {default_flush_frames}",
    )

    args = parser.parse_args()

    cam = create_network_camera(
        cam_stream=args.cam,
        description=args.descr,
        flush_frames=args.flush,
        image_interval_s=args.interval,
        test=args.test,
    )

    record_timelapse(
        cam=cam, persistent=not args.restart_every_cycle, snapshot=args.snapshot
    )
