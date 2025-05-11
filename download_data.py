#!/usr/bin/env python3

import argparse
import cv2
import os
import glob
import subprocess
import configparser

# Define locations
locations = ['sunflowers-lowres', 'scaffolding', 'garden-lowres']
generate_video = []

top_local_dir = f"/home/username/data"

top_remote_dir = f"/home/username/repos/timelapse"

remote_login = "username@192.168.0.46"

video_ext = "mp4"

video_settings_path = "video-settings.txt"

def parse_args():
    parser = argparse.ArgumentParser(description='Process timelapse images.')
    parser.add_argument('--rm-remote', action='store_true', 
                        help='Delete files on the remote device after syncing')
    parser.add_argument('--no-trawl', action='store_true',
                        help='Skip trawling for new images')
    
    return parser.parse_args()

def get_file_paths(location):
    local_dir = f"{top_local_dir}/{location}"
    local_fpath = f"{local_dir}/{location}*.png"

    remote_dir = f"{top_remote_dir}/{location}"
    remote_fpath = f"{remote_dir}/{location}*"

    if not os.path.exists(video_settings_path):
        raise FileNotFoundError(f"Settings file {video_settings_path} does not exist")
    config = configparser.ConfigParser()
    config.read(video_settings_path)
    fps = int(config[location]["fps"])

    crop_coords = None
    if "crop" in config[location]:
        crop_str = config[location]["crop"]
        crop_coords = [int(x) for x in crop_str.split(',')]

    video_base = f"{location}-{fps}fps"

    video_path = f"{video_base}.{video_ext}"
    video_backup_path = f"{video_base}.prev.{video_ext}"

    resolution = None
    if "resolution" in config[location]:
        resolution_str = config[location]["resolution"]
        resolution = [int(x) for x in resolution_str.split(',')]

    return local_dir, local_fpath, remote_fpath, video_path, video_backup_path, fps, crop_coords, resolution

args = parse_args()

for loc in locations:
    if args.no_trawl:
        generate_video.append(loc)
        break

    print(f"Trawl for images: {loc}")

    l_dir, l_fpath, r_fpath, video_path, video_backup_path, _, _, _ = get_file_paths(loc)

    old_file_list = set(glob.glob(l_fpath))

    rsync_cmd = f"rsync -av --ignore-existing {remote_login}:{r_fpath} {l_dir}"
    subprocess.run(rsync_cmd, shell=True)
    os.sync()

    updated_file_list = set(glob.glob(l_fpath))

    added_files = updated_file_list - old_file_list

    print(f"Added files: {len(added_files)}")

    if len(updated_file_list) > 0 and (len(added_files) > 0 or not os.path.exists(video_path)):

        generate_video.append(loc)

        if args.rm_remote:
            rm_cmd = f"ssh {remote_login} 'rm -f {r_fpath}'"
            subprocess.run(rm_cmd, shell=True)

        if os.path.exists(video_path):
            os.replace(video_path, video_backup_path)


def get_img_shape(img):
    frame = cv2.imread(img)
    return frame.shape[:2]

def read_and_resize(image, writer_res, explicit_res, crop_coords):
    frame = cv2.imread(image)
    if explicit_res is not None:
        res = (explicit_res[1], explicit_res[0])
    else:
        if frame.shape[0] != writer_res[0] or frame.shape[1] != writer_res[1]:
            raise Exception(f"Illegal resolution: {frame.shape[:2]}")
        res = (writer_res[1], writer_res[0])
    
    frame = cv2.resize(frame, res)

    if crop_coords is not None:
        left, top, right, bottom = crop_coords
        frame = frame[top:bottom, left:right]

    return frame

for loc in generate_video:
    print(f"Generate video: {loc}")
    l_dir, l_fpath, r_fpath, video_path, video_backup_path, fps, crop_coords, pre_crop_explicit_res = get_file_paths(loc)

    images = sorted(glob.glob(l_fpath))

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')

    if pre_crop_explicit_res is not None:
        pre_crop_output_res = pre_crop_explicit_res
    else:
        pre_crop_output_res = cv2.imread(images[0]).shape[:2]
    print(video_path)
    print(fourcc)
    print(fps)
    print(pre_crop_output_res)

    if crop_coords is not None:
        left, top, right, bottom = crop_coords
        post_height = bottom - top
        post_width = right - left
        writer_resolution = (post_width, post_height)
    else:
        writer_resolution = (pre_crop_output_res[1], pre_crop_output_res[0])

    video = cv2.VideoWriter(video_path, fourcc, fps, writer_resolution)

    for i, image_fpath in enumerate(images):
        
        frame = read_and_resize(image_fpath, pre_crop_output_res, pre_crop_explicit_res, crop_coords)
        video.write(frame)

        cv2.imshow('Creating Video', frame)
        
        # Check if user wants to quit (press 'q')
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break  

    video.release()
    cv2.destroyAllWindows()
