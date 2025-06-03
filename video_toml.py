from dataclasses import dataclass, fields
from pathlib import Path
import os
import toml
from glob import glob
import numpy as np
from numbers import Number
import cv2

from video_template import VideoTemplate

@dataclass
class VideoToml:
    # If 'copy' field has a value, it means current template will inherit from parent template 
    # and then overwrite wherever current template has a value.
    # Included here for clarity, but intentionally commented out
    # copy : str
    # Directory containing images
    dir : Path = None
    # Frames per second
    fps : Number = None
    # Set resolution
    resolution : tuple[Number, Number] = None
    # Resolution of final movie
    output_resolution : tuple[Number, Number] = None
    # Cropping if applicable
    crop : tuple[Number, Number, Number, Number]= None
    # Rotation of image
    rotation : Number = None
    # Grayscale (0 or 1)
    gray : int = None
    # Histogram normalization (0 or 1)
    normalize : int = None 
    # Subtract background (0 or 1)
    subtract : int = None
    # # Thresholding values for filtering - 0, 1, 2, 3 or 6 element vector
    # threshold : Number | np.array = None

    # Parse attributes to generate template with settings for video generation
    def get_video_template(self, top_dir:Path=None):

        top_dir = top_dir or Path(os.path.expanduser("~")) / "data"

        pattern = str(top_dir / self.dir/ '*.png')
        images = sorted(glob(pattern))
        
        fps = self.fps
        crop = self.crop
        rotation = self.rotation
        input_resolution = self.resolution
        output_resolution = self.output_resolution
        grayscale = self.gray
        normalize = self.normalize
        subtract_background = self.subtract
        # threshold = self.threshold

        input_resolution_fixed = input_resolution is not None
        if not input_resolution_fixed:
            input_resolution = cv2.imread(images[0]).shape[:2][::-1]

        if not output_resolution:
            if crop:
                left, top, right, bottom = crop
                output_resolution = (right-left, bottom-top)
            else:
                output_resolution = input_resolution

        # if threshold is None:
        #     lower_threshold = -np.inf
        #     upper_threshold = np.inf
        # if isinstance(threshold, Number):
        #     lower_threshold = threshold
        #     upper_threshold = np.inf
        # elif isinstance(threshold, list):
        #     if len(threshold) == 2:
        #         lower_threshold, upper_threshold = threshold
        #     elif threshold == 3:
        #         lower_threshold = np.array(threshold)
        #         upper_threshold = np.full_like(lower_threshold, fill_value=np.inf)
        #     elif threshold == 6:
        #         lower_threshold = np.array(threshold[:3])
        #         upper_threshold = np.array(threshold[3:])
        #     else:
        #         raise Exception(f"Illegal dimension of threshold array: {len(threshold)}. Allowed dimensions are 0, 1, 2, 3 or 6")
            
        return VideoTemplate(images=images, 
                    fps=fps, 
                    input_resolution=input_resolution, 
                    input_resolution_fixed=input_resolution_fixed,
                    crop=crop,
                    rotation=rotation,
                    grayscale=grayscale,
                    normalize=normalize,
                    subtract_background=subtract_background,
            #        lower_threshold=lower_threshold,
            #        upper_threshold=upper_threshold,
                    output_resolution=output_resolution
                    )


# Read settings file - separate function to allow for recursive calls if 'copy' field is used to indicate inheritance
def _read_toml(video_id:str, recursion_list):

    video_settings_path = 'video-settings.toml'
    assert os.path.isfile(video_settings_path)

    if recursion_list is None:
        recursion_list = []
    if video_id in recursion_list:
        raise RecursionError(f"Circular reference for video template {video_id}")
    recursion_list.append(video_id)

    with open(video_settings_path, 'r') as f:
        settings = toml.load(f)[video_id]

    parent = settings.get('copy')
    if parent is None:
        video_toml = VideoToml()
    else:
        video_toml = _read_toml(video_id=parent, recursion_list=recursion_list)
    
    for field in fields(VideoToml):
        value = settings.get(field.name)
        if value is not None:
            setattr(video_toml, field.name, value)
    return video_toml

# Use to read file with video settings
def parse_video_settings(video_id:str, top_dir:Path=None, recursion_list=None):

    video_toml = _read_toml(video_id=video_id, recursion_list=None)
    
    return video_toml.get_video_template(top_dir=top_dir)

    
