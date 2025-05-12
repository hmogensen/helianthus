#!/usr/bin/env python3
import configparser
import os
from pathlib import Path

from download_images import download_remote_files

video_settings_path = "video-settings.txt"

tags = ["sunflowers-lowres", "garden-lowres", "scaffolding"]

if not os.path.exists(video_settings_path):
    raise FileNotFoundError(f"Settings file {video_settings_path} does not exist")
config = configparser.ConfigParser()
config.read(video_settings_path)

for tag in tags:
    subset = config[tag]
    image_folder = subset["dir"]
    download_remote_files(image_folder=image_folder, filter="*.png", ignore_existing=True)