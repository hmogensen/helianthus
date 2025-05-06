import cv2
import os
import glob
import subprocess
import configparser

# Define locations
locations = ['scaffolding', 'garden-lowres', 'sunflowers-lowres']
generate_video = []

top_local_dir = f"/home/username/data"

top_remote_dir = f"/home/username/repos/timelapse"

remote_login = "username@192.168.0.46"

video_ext = "mp4"

video_settings_path = "video-settings.txt"

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

    video_base = f"{location}-{fps}fps"

    video_path = f"{video_base}.{video_ext}"
    video_backup_path = f"{video_base}.prev.{video_ext}"

    return local_dir, local_fpath, remote_fpath, video_path, video_backup_path, fps


for loc in locations:
    print(f"Trawl for images: {loc}")

    l_dir, l_fpath, r_fpath, video_path, video_backup_path, _ = get_file_paths(loc)

    old_file_list = set(glob.glob(l_fpath))

    rsync_cmd = f"rsync -av --ignore-existing username@192.168.0.46:{r_fpath} {l_dir}"
    subprocess.run(rsync_cmd, shell=True)
    os.sync()

    updated_file_list = set(glob.glob(l_fpath))

    added_files = updated_file_list - old_file_list

    print(f"Added files: {len(added_files)}")

    if len(added_files) > 0 or not os.path.exists(video_path):

        generate_video.append(loc)
        
        rm_cmd = f"ssh {remote_login} 'rm -f {r_fpath}'"
        subprocess.run(rm_cmd, shell=True)

        if os.path.exists(video_path):
            os.replace(video_path, video_backup_path)


def get_img_shape(img):
    frame = cv2.imread(img)
    return frame.shape[:2]

def read_and_resize(image, target_width, target_height):
    frame = cv2.imread(image)
    if frame.shape[0] != target_height or frame.shape[1] != target_width:
        frame = cv2.resize(frame, (target_width, target_height))
    return frame

for loc in generate_video:
    print(f"Generate video: {loc}")
    l_dir, l_fpath, r_fpath, video_path, video_backup_path, fps = get_file_paths(loc)

    
    
    images = sorted(glob.glob(l_fpath))
    
    height1, width1 = get_img_shape(images[0])
    height2, width2 = get_img_shape(images[-1])
    height = min(height1, height2)
    width = min(width1, width2)
    
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video = cv2.VideoWriter(video_path, fourcc, fps, (width, height))
    
    for i, image_fpath in enumerate(images):
        print(f"{i} / {len(images)}")
        frame = read_and_resize(image_fpath, width, height)
        video.write(frame)
    
    video.release()
