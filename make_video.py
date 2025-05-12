import cv2
from glob import glob
from pathlib import Path

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

        

        
        

