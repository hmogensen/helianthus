from tqdm import tqdm
import numpy as np
import cv2
import h5py
from datetime import datetime
import os
import sys

from video.video_settings_parser import parse_video_settings


def extract_brightness(frame):
    return np.mean(frame)


def extract_sky_brightness(frame, sky_region_ratio=0.3):
    height = frame.shape[0]
    sky_region = frame[: int(height * sky_region_ratio), :]
    return np.mean(sky_region)


def extract_hsv_brightness(frame):
    if len(frame.shape) == 3:
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        return np.mean(hsv[:, :, 2])
    else:
        return np.mean(frame)


def extract_bright_pixel_ratio(frame, threshold=200):
    if len(frame.shape) == 3:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    else:
        gray = frame
    bright_pixels = np.sum(gray > threshold)
    total_pixels = gray.shape[0] * gray.shape[1]
    return bright_pixels / total_pixels


def store_sunlight_analysis_hdf5(timestamps, results, template_name, output_file):
    # Convert timestamps to Unix timestamps (floats)
    if hasattr(timestamps[0], "timestamp"):
        # If datetime objects
        timestamp_data = np.array([t.timestamp() for t in timestamps])
    else:
        # If already numeric
        timestamp_data = np.array(timestamps, dtype=float)

    with h5py.File(output_file, "w") as f:

        f.create_dataset("timestamps", data=np.array(timestamp_data))

        f.create_dataset(
            "avg_brightness", data=np.array([r["avg_brightness"] for r in results])
        )
        f.create_dataset(
            "sky_brightness", data=np.array([r["sky_brightness"] for r in results])
        )
        f.create_dataset(
            "hsv_brightness", data=np.array([r["hsv_brightness"] for r in results])
        )
        f.create_dataset(
            "bright_ratio", data=np.array([r["bright_ratio"] for r in results])
        )
        f.create_dataset(
            "median_intensity", data=np.array([r["median_intensity"] for r in results])
        )
        f.create_dataset(
            "mean_intensity", data=np.array([r["mean_intensity"] for r in results])
        )

        f.attrs["creation_date"] = datetime.now().isoformat()
        f.attrs["n_frames"] = len(timestamp_data)
        f.attrs["description"] = "Comprehensive sunlight analysis from timelapse"
        f.attrs["template_name"] = template_name


tag = "garden-lowres"
metrics_file = tag + ".h5"
template = parse_video_settings(tag)

timestamps = []
results = []

for frame, t in tqdm(
    template.process_frames(ts=True),
    desc="Processing frames",
    total=len(template.images),
):
    timestamps.append(t)

    frame_results = {
        "avg_brightness": extract_brightness(frame),
        "sky_brightness": extract_sky_brightness(frame),
        "hsv_brightness": extract_hsv_brightness(frame),
        "bright_ratio": extract_bright_pixel_ratio(frame),
        "median_intensity": np.median(frame),
        "mean_intensity": np.mean(frame),
    }
    results.append(frame_results)

store_sunlight_analysis_hdf5(timestamps, results, tag, metrics_file)
