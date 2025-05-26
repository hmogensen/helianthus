#!/usr/bin/env python3
import configparser
import os
from pathlib import Path

from download_images import download_remote_files

video_settings_path = "video-settings.txt"

tags = ["garden-lowres", "tradgard-torpet"]#"sunflowers-lowres", "scaffolding"]

if not os.path.exists(video_settings_path):
    raise FileNotFoundError(f"Settings file {video_settings_path} does not exist")
config = configparser.ConfigParser()
config.read(video_settings_path)

for image_folder in tags:

    download_remote_files(image_folder=image_folder, filter="*.png", ignore_existing=True,
                          local_top_dir=Path("/home/username/data/"),
                          remote_top_dir=Path("/home/username/repos/timelapse"),
                          remote_login="username@192.168.0.XXX")
    
    download_remote_files(image_folder=image_folder, filter="*.png", ignore_existing=True,
                          local_top_dir=Path("/home/username/data/"),
                          remote_top_dir=Path("/home/username/data"),
                          remote_login="username@192.168.0.XXX")
    
    download_remote_files(image_folder=image_folder, filter="*.mp4", ignore_existing=False,
                          local_top_dir=Path("/home/username/data/"),
                          remote_top_dir=Path("/home/username/repos"),
                          remote_login="username@192.168.0.XXX")