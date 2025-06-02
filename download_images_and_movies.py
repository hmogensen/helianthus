#!/usr/bin/env python3
import os
from pathlib import Path

from download_remote_files import download_remote_files

tags = ["garden-lowres", "tradgard-torpet"]#"sunflowers-lowres", "scaffolding"]
top_dir = Path(os.path.expanduser("~"))
active_dir = top_dir / "repos/timelapse"
data_dir = top_dir / "data"

remote_login = "username@192.168.0.XXX" # Replace with correct IP address
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