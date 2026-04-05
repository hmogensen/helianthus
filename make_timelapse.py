import argparse
from collections import defaultdict
from datetime import timedelta
from glob import glob
from pathlib import Path
from zoneinfo import ZoneInfo
import cv2

from video.video_template import VideoTemplate, filename_to_date

default_fps = 24
default_timezone = "Europe/Oslo"
default_daily_time = "12:00"


def select_daily_frames(images, target_time: str, timezone: str):
    """Return one image per day: the frame closest to target_time in standard (winter) time.

    Timestamps recorded during DST (summer) are shifted back one hour before
    comparison so the selection is always relative to standard time.
    """
    tz = ZoneInfo(timezone)
    target_h, target_m = (int(x) for x in target_time.split(":"))
    target_seconds = target_h * 3600 + target_m * 60

    by_day = defaultdict(list)
    for img in images:
        dt = filename_to_date(img)
        aware = dt.replace(tzinfo=tz)
        if aware.dst() != timedelta(0):
            dt = dt - timedelta(hours=1)
        by_day[dt.date()].append((dt, img))

    result = []
    for date in sorted(by_day):
        frames = by_day[date]
        closest = min(
            frames,
            key=lambda x: abs(x[0].hour * 3600 + x[0].minute * 60 + x[0].second - target_seconds),
        )
        result.append(closest[1])
    return result


def make_timelapse_from_folder(
    folder: str,
    output: str,
    fps: float,
    preview: bool,
    daily: bool,
    daily_time: str,
    timezone: str,
):
    images = sorted(glob(str(Path(folder) / "*.png")), key=lambda f: filename_to_date(f))

    if not images:
        raise FileNotFoundError(f"No PNG images found in {folder}")

    if daily:
        images = select_daily_frames(images, target_time=daily_time, timezone=timezone)
        print(f"Selected {len(images)} daily frames at {daily_time} ({timezone} standard time)")

    first_frame = cv2.imread(images[0])
    height, width = first_frame.shape[:2]
    resolution = (width, height)

    template = VideoTemplate(
        images=images,
        fps=fps,
        input_resolution=resolution,
        input_resolution_fixed=True,
        output_resolution=resolution,
    )
    template.render_video(video_path=output, preview=preview)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Create a timelapse movie from a folder of timestamped images"
    )
    parser.add_argument("folder", help="Folder containing PNG images")
    parser.add_argument("output", help="Output video file path (e.g. timelapse.mp4)")
    parser.add_argument(
        "--fps",
        "-f",
        type=float,
        default=default_fps,
        help=f"Frames per second. Default: {default_fps}",
    )
    parser.add_argument(
        "--preview",
        "-p",
        action="store_true",
        default=False,
        help="Show preview window while rendering",
    )
    parser.add_argument(
        "--daily",
        "-d",
        action="store_true",
        default=False,
        help="Select one frame per day closest to --time",
    )
    parser.add_argument(
        "--time",
        "-t",
        default=default_daily_time,
        help=f"Target time for daily frame selection (HH:MM, standard/winter time). Default: {default_daily_time}",
    )
    parser.add_argument(
        "--timezone",
        "-z",
        default=default_timezone,
        help=f"Timezone for DST conversion. Default: {default_timezone}",
    )

    args = parser.parse_args()
    make_timelapse_from_folder(
        folder=args.folder,
        output=args.output,
        fps=args.fps,
        preview=args.preview,
        daily=args.daily,
        daily_time=args.time,
        timezone=args.timezone,
    )