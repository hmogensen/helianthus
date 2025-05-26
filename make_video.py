import cv2
from glob import glob
from pathlib import Path
import os 

top_dir = Path("/home/username/data/")

def make_video(video_path, image_folder, fps, resolution=None, crop=None, preview=False):
    pattern = str(top_dir / image_folder / "*.png")
    image_files = sorted(glob(pattern))

    if resolution is not None:
        original_resolution = resolution
    else:
         original_resolution = cv2.imread(image_files[0]).shape[:2][::-1]

    if crop is not None:
        left, top, right, bottom = crop
        writer_resolution = (right-left, bottom-top)
    else:
        writer_resolution = original_resolution
    
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video = cv2.VideoWriter(video_path, fourcc, fps, writer_resolution)
    for image in image_files:
        frame = cv2.imread(image)

        if resolution is not None:
            frame = cv2.resize(frame, resolution)
        
        if list(frame.shape[:2]) != list(original_resolution[::-1]):
            raise Exception(f"Inconsistent pre cropped resolution: {frame.shape[:2]} vs {original_resolution[::-1]:}")
        
        if crop is not None:
            frame = frame[top:bottom, left:right]

        if list(frame.shape[:2]) != list(writer_resolution[::-1]):
            raise Exception(f"Inconsistent cropped resolution: {frame.shape[:2]} vs {writer_resolution[::-1]:}")
        
        video.write(frame)

        if preview:
            cv2.imshow('Preview', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break 
    
    video.release()
    if preview:
        cv2.destroyAllWindows()

video_settings_path = "video-settings.txt"
video_ext = "mp4"
import configparser
import sys

def return_value_or_none(subset, key):
    if key in subset:
        return [int(x) for x in subset[key].split(',')]
    
if __name__ == "__main__":

    tag = sys.argv[1]
    
    if not os.path.exists(video_settings_path):
        raise FileNotFoundError(f"Settings file {video_settings_path} does not exist")
    config = configparser.ConfigParser()
    config.read(video_settings_path)

    subset = config[tag]
    dir = subset["dir"]
    fps = int(subset["fps"])

    resolution = return_value_or_none(subset, "resolution")
    crop = return_value_or_none(subset, "crop")

    video_base = f"{tag}-{fps}fps"
    video_path = f"{video_base}.{video_ext}"
    video_backup_path = f"{video_base}.prev.{video_ext}"

    if os.path.exists(video_path):
        os.replace(video_path, video_backup_path)

    make_video(video_path=video_path, image_folder=dir, fps=fps, resolution=resolution, crop=crop, preview=True)



