from pathlib import Path
from tqdm import tqdm
import cv2
from functools import cached_property
from datetime import datetime
import re

from gif_writer import GIF_Writer


def filename_to_date(filename):
    pattern = r'(\d{4}-\d{2}-\d{2}-\d{2}-\d{2}-\d{2})'
    match = re.search(pattern, filename)
    if match:
        date_str = match.group(1)
        return datetime.strptime(date_str, '%Y-%m-%d-%H-%M-%S')
    raise Exception(f"Cannot parse date from file name: {filename}")

class VideoTemplate:
    """
    Template for video processing configuration.
    
    Attributes:
        images: Chronologically sorted list of paths to image files
        fps: Frames per second
        input_resolution: Expected resolution of raw image
        input_resolution_fixed: If True, throws exception when resolution differs 
            between frames. If False, OpenCV silently drops mismatched frames
        rotation: Rotation angle in degrees, applied after input resolution rectification
        crop: Cropping bounds as (left, top, right, bottom), applied after rotation
        grayscale: If True, convert frames to grayscale
        normalize: If True, apply histogram equalization
        subtract_background: If True, subtract background from frames
        output_resolution: Target resolution for rendered video
    """
    
    def __init__(self, 
                 images: tuple[str] = None,
                 fps: float = None,
                 input_resolution: tuple[int, int] = None,
                 input_resolution_fixed: bool = False,
                 rotation: float = None,
                 crop: tuple[int, int, int, int] = None,
                 grayscale: bool = False,
                 normalize: bool = False,
                 subtract_background: bool = False,
                 output_resolution: tuple[int, int] = None):
        
        self.images = images
        self.fps = fps
        self.input_resolution = input_resolution
        self.input_resolution_fixed = input_resolution_fixed
        self.rotation = rotation
        self.crop = crop
        self.grayscale = grayscale
        self.normalize = normalize
        self.subtract_background = subtract_background
        self.output_resolution = output_resolution
    
    # # Lower threshold for object detection filtering
    # lower_threshold : Number | np.array = None

    # # Upper threshold for object detection filtering
    # upper_threshold : Number | np.array = None

    def _clear_cache(self):
        for attr in ('_rotation_matrix', '_rotation_frame_dim'):
            if hasattr(self, attr):
                delattr(self, attr)

    def __setattr__(self, name, value):
        if name in ('rotation', 'images'):
            self._clear_cache()
        super().__setattr__(name, value)
    
    @cached_property
    def _rotation_frame_dim(self):
        if self.rotation is not None:
            frame = cv2.imread(self.images[0])
            height, width = frame.shape[:2]
            return width, height
        return None

    @cached_property
    def _rotation_matrix(self):
        if self.rotation is not None:
            width, height = self._rotation_frame_dim
            center = (width // 2, height // 2)
            return cv2.getRotationMatrix2D(center, self.rotation, 1.0)
        return None

    def process_frames(self, ts=False):
        """Iterator that yields processed frames one by one"""
        for image in self.images:
            frame = cv2.imread(image)

            if not self.input_resolution_fixed and list(frame.shape[:2]) != list(self.input_resolution[::-1]):
                raise Exception(f"Inconsistent pre cropped resolution: {frame.shape[:2]} vs {self.input_resolution[::-1]}")

            if self.input_resolution is not None:
                frame = cv2.resize(frame, self.input_resolution)

            if self.rotation is not None and self.rotation != 0:
                frame = cv2.warpAffine(frame, self._rotation_matrix, self._rotation_frame_dim)
            
            if self.crop is not None:
                left_crop, top_crop, right_crop, bottom_crop = self.crop
                frame = frame[top_crop:bottom_crop, left_crop:right_crop]

            if self.output_resolution:
                frame = cv2.resize(frame, self.output_resolution)
            
            if list(frame.shape[:2]) != list(self.output_resolution[::-1]):
                raise Exception(f"Inconsistent cropped resolution: {frame.shape[:2]} vs {self.output_resolution[::-1]:}")
            
            if self.grayscale:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
            
            if self.normalize:
                if len(frame.shape) == 3:
                    for i in range(frame.shape[2]):
                        frame[:, :, i] = cv2.equalizeHist(frame[:, :, i])
                else:
                    frame = cv2.equalizeHist(frame)
                    frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
            
            if ts:
                retval = (frame, filename_to_date(image))
            else:
                retval = frame
            yield retval

    def render_video(self, video_path:Path, preview:bool):

        if str(video_path).endswith('.gif'):
            writer = GIF_Writer(video_path, self.fps, self.output_resolution)
        else:
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            # fourcc = cv2.VideoWriter_fourcc(*'H264')
            writer = cv2.VideoWriter(video_path, fourcc, self.fps, self.output_resolution)

        success = True
    
        for frame in tqdm(self.process_frames(), desc="Processing images", total=len(self.images)):
            writer.write(frame)

            if preview:
                cv2.imshow('Preview', frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    success = False
                    break
        
        writer.release()
        if preview:
            cv2.destroyAllWindows()
        return success

    