import cv2
import os
import glob
import subprocess

# Define locations
locations = ['scaffolding', 'garden-lowres', 'sunflowers-lowres']

# Collect all data with rsync for both locations
for location in locations:
    # Copy files with rsync
    rsync_command = f"rsync -av --ignore-existing username@192.168.0.46:/home/username/repos/timelapse/{location}/* ~/data/{location}"
    subprocess.run(rsync_command, shell=True)

    # Delete files on remote after successful download
    ssh_command = f"ssh username@192.168.0.46 'rm -f /home/username/repos/timelapse/{location}/*.png'"
    subprocess.run(ssh_command, shell=True)

def get_img_shape(img):
    frame = cv2.imread(img)
    return frame.shape[:2]

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
    for i, image in enumerate(images):
        print(f"{i} / {len(images)}")
        video.write(cv2.imread(image))
    
    # Release resources
    video.release()
    
    print(f"Completed video for {location}")

print("All videos created successfully!")