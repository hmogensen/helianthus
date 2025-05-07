#!/usr/bin/env python3

import cv2
import os
import glob
import subprocess
import configparser

image_dir = f"/home/username/data/garden-lowres/"
image_search_path = f"{image_dir}/*.png"

video_dir = f"/home/username/repos/timelapse"
video_search_path = f"{video_dir}/*.mp4"

remote_login = "username@192.168.0.XXX"

old_image_list = set(glob.glob(image_search_path))
rsync_cmd = f"sudo rsync -av --ignore-existing {remote_login}:{image_search_path} {image_dir}"
subprocess.run(rsync_cmd, shell=True)
os.sync()
updated_images_list = set(glob.glob(image_search_path))
added_images = updated_images_list - old_image_list
print(f"Added files: {len(added_images)}")

rsync_cmd = f"sudo rsync -av {remote_login}:{video_search_path} {video_dir}"
subprocess.run(rsync_cmd, shell=True)
os.sync()
