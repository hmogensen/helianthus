#!/usr/bin/env python3
import configparser
import os
from pathlib import Path

from download_remote_files import download_remote_files

video_settings_path = "video-settings.txt"

tags = ["garden-lowres", "tradgard-torpet"]#"sunflowers-lowres", "scaffolding"]

if not os.path.exists(video_settings_path):
    raise FileNotFoundError(f"Settings file {video_settings_path} does not exist")
config = configparser.ConfigParser()
config.read(video_settings_path)

active_dir = Path("/home/username/repos/timelapse")
data_dir = Path("/home/username/data")
remote_login = "username@192.168.0.XXX"
for image_folder in tags:

    # download images from active directory
    download_remote_files(image_folder=image_folder, filter="*.png", ignore_existing=True,
                          local_top_dir=data_dir,
                          remote_top_dir=active_dir,
                          remote_login=remote_login)
    
    # download images from data directory
    download_remote_files(image_folder=image_folder, filter="*.png", ignore_existing=True,
                          local_top_dir=data_dir,
                          remote_top_dir=data_dir,
                          remote_login=remote_login)
    
    # download movies from remote active directory, and overwrite corresponding file in local data directory
    download_remote_files(image_folder=image_folder, filter="*.mp4", ignore_existing=False,
                          local_top_dir=data_dir,
                          remote_top_dir=active_dir,
                          remote_login=remote_login)