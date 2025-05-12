#!/usr/bin/env python3

import argparse
import configparser
import os

from download_images import download_remote_files, clear_remote_images
from make_video import make_video

video_settings_path = "video-settings.txt"
video_ext = "mp4"

tags = ["sunflowers-lowres", "garden-lowres", "scaffolding"]

def parse_args():
    parser = argparse.ArgumentParser(description='Process timelapse images.')
    parser.add_argument('--rm-remote', action='store_true', 
                        help='Delete files on the remote device after syncing')
    parser.add_argument('--preview', action='store_true',
                        help='Show video preview during creation')
    
    return parser.parse_args()


def return_value_or_none(subset, key):
    if key in subset:
        return [int(x) for x in subset[key].split(',')]
    
if __name__ == "__main__":
    
    args = parse_args()
    
    if not os.path.exists(video_settings_path):
        raise FileNotFoundError(f"Settings file {video_settings_path} does not exist")
    config = configparser.ConfigParser()
    config.read(video_settings_path)

    for tag in tags:
        subset = config[tag]
        dir = subset["dir"]
        download_remote_files(image_folder=dir, filter="*.png", ignore_existing=True)
        if args.rm_remote:
            clear_remote_images(image_folder=dir)
    
    for tag in tags:
        subset = config[tag]
        dir = subset["dir"]
        fps = int(subset["fps"])

        resolution = return_value_or_none(subset, "resolution")
        crop = return_value_or_none(subset, "crop")

        video_base = f"{tag}-{fps}fps"
        video_path = f"{video_base}.{video_ext}"
        video_backup_path = f"{video_base}.prev.{video_ext}"

        if os.path.exists(video_path):
            os.replace(video_path, video_backup_path)

        make_video(video_path=video_path, image_folder=dir, fps=fps, resolution=resolution, crop=crop, preview=args.preview)

