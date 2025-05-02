import cv2
import os
import glob
import subprocess

# Define locations
locations = ['scaffolding', 'garden-lowres'] #, 'sunflowers-lowres']

# Collect all data with rsync for both locations
for location in locations:
    print(location)
    files_before = set(glob.glob(f"~/data/{location}/{location}*.png"))

    # Copy files with rsync
    rsync_command = f"rsync -av --ignore-existing username@192.168.0.46:/home/username/repos/timelapse/{location}/* ~/data/{location}"
    subprocess.run(rsync_command, shell=True)

    files_after = set(glob.glob(f"~/data/{location}/{location}*.png"))

    new_files = len(files_after) - len(files_before)

    print(new_files)
    if new_files:
        print(f"New frames received for {location}: {len(new_files)} files")
        # Delete files on remote after successful download
        ssh_command = f"ssh username@192.168.0.46 'rm -f /home/username/repos/timelapse/{location}/*.png'"
        subprocess.run(ssh_command, shell=True)

        # If current video exists, rename it to backup (overwriting existing backup)
        video_name = f'{location}.mp4'
        backup_video_name = f'{location}_backup.mp4'
        
        if os.path.exists(video_name):
            print(f"Renaming current {video_name} to {backup_video_name}")
            os.replace(video_name, backup_video_name)

def get_img_shape(img):
    frame = cv2.imread(img)
    return frame.shape[:2]

def read_and_resize(image, target_width, target_height):
    frame = cv2.imread(image)
    if frame.shape[0] != target_height or frame.shape[1] != target_width:
        frame = cv2.resize(frame, (target_width, target_height))
    return frame

# Process each location automatically
for location in locations:
    # Parameters
    image_folder = f'/home/username/data/{location}/'
    video_name = f'{location}.mp4'
    fps = 24

    print(f"Processing {location}...")
    
    # Get all PNG files, sorted
    images = sorted(glob.glob(os.path.join(image_folder, f'{location}*.png')))
    
    # Get first image dimensions
    height1, width1 = get_img_shape(images[0])
    height2, width2 = get_img_shape(images[-1])
    height = min(height1, height2)
    width = min(width1, width2)
    
    # Create video writer
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video = cv2.VideoWriter(video_name, fourcc, fps, (width, height))
    
    # Add each image to video
    for i, image_fpath in enumerate(images):
        print(f"{i} / {len(images)}: {image_fpath}")
        frame = read_and_resize(image_fpath, width, height)
        video.write(frame)
    
    # Release resources
    video.release()
    
    print(f"Completed video for {location}")
