# # Collect all data
# rsync -av --ignore-existing username@192.168.0.46:/home/username/repos/timelapse/garden-lowres/* ~/data/garden-lowres
# rsync -av --ignore-existing username@192.168.0.46:/home/username/repos/timelapse/sunflowers-lowres/* ~/data/sunflowers-lowres

# Create movie

import cv2
import os
import glob

# Parameters
location = 'sunflowers-lowres'
# location = 'garden-lowres'
image_folder = f'/home/username/data/{location}/'
video_name = f'{location}.mp4'
fps = 24

# Get all PNG files, sorted
images = sorted(glob.glob(os.path.join(image_folder, f'{location}*.png')))

# Get first image dimensions
frame = cv2.imread(images[0])
height, width, layers = frame.shape

# Create video writer
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
video = cv2.VideoWriter(video_name, fourcc, fps, (width, height))

# Add each image to video
for i, image in enumerate(images):
    print(f"{i} / {len(images)}")
    video.write(cv2.imread(image))

# Release resources
video.release()