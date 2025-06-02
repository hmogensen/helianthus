from dataclasses import dataclass
from numbers import Number
import numpy as np
import cv2

@dataclass
class VideoTemplate:
    # Chronologically sorted list of paths to image files
    images : tuple[str] = None

    # Frames per second
    fps : float = None

    # Expected resolution of raw image
    input_resolution : tuple[int, int] = None 
    
    # If input resolution is not fixed, an exception will be thrown if resolution differs between frames. 
    # If not, opencv would leave out frames with differing resolution without throwing an error
    input_resolution_fixed : bool = False

    # Rotation - applied on raw image after input resolution rectification
    rotation : float = None
    
    # Cropping - applied after rotation
    crop : tuple[int, int, int, int] = None

    # Rotation of image
    rotation : float = False

    # If true, convert to grayscale
    grayscale : bool = False

    # If true, apply histogram equalization
    normalize : bool = False

    # If true, subtract background from frames
    subtract_background : bool = False

    # Lower threshold for object detection filtering
    lower_threshold : Number | np.array = None

    # Upper threshold for object detection filtering
    upper_threshold : Number | np.array = None

    # Resolution of rendered video  
    output_resolution : tuple[int, int] = None

    def generate_writer(self, video_path:str):
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        writer = cv2.VideoWriter(video_path, fourcc, self.fps, self.output_resolution)
        return writer

    def close_writer(self, writer:cv2.VideoWriter, preview=True):
        writer.release()
        if preview:
            cv2.destroyAllWindows()

    def append_video(self, writer:cv2.VideoWriter, preview:bool):
        if self.crop:
            left, top, right, bottom = self.crop

        for image in self.images:
            frame = cv2.imread(image)

            if not self.input_resolution_fixed and list(frame.shape[:2]) != list(self.input_resolution[::-1]):
                raise Exception(f"Inconsistent pre cropped resolution: {frame.shape[:2]} vs {self.input_resolution[::-1]}")

            if self.input_resolution is not None:
                frame = cv2.resize(frame, self.input_resolution)
            
            if self.crop is not None:
                frame = frame[top:bottom, left:right]

            if list(frame.shape[:2]) != list(self.output_resolution[::-1]):
                raise Exception(f"Inconsistent cropped resolution: {frame.shape[:2]} vs {self.output_resolution[::-1]:}")
            
            writer.write(frame)

            if preview:
                cv2.imshow('Preview', frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    return False
            return True
    
    