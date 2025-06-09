from dataclasses import dataclass
from numbers import Number
from pathlib import Path
from PIL import Image
from tqdm import tqdm
import numpy as np
import cv2

@dataclass
class GIF_Writer:
    video_path : Path
    fps : Number
    output_resolution : tuple[int, int] = None
    frames : list = None

    def __post_init__(self):
        if self.frames is None:
            self.frames = []
    
    def write(self, frame):
        if self.output_resolution:
            frame = cv2.resize(frame, self.output_resolution)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pil_frame = Image.fromarray(rgb_frame)
        self.frames.append(pil_frame)
    
    def release(self):
        duration_ms = int(1000 / self.fps)
        print("Writing video, stand by ...", end=" ")
        self.frames[0].save(
            self.video_path,
            save_all=True,
            append_images=self.frames[1:],
            duration=duration_ms,
            loop=0,
            optimize=True,
            colors=32
        )
        print("Done")

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

    # # Lower threshold for object detection filtering
    # lower_threshold : Number | np.array = None

    # # Upper threshold for object detection filtering
    # upper_threshold : Number | np.array = None

    # Resolution of rendered video  
    output_resolution : tuple[int, int] = None

    def render_video(self, video_path:Path, preview:bool):

        if str(video_path).endswith('.gif'):
            writer = GIF_Writer(video_path, self.fps, self.output_resolution)
        else:
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            # fourcc = cv2.VideoWriter_fourcc(*'H264')
            writer = cv2.VideoWriter(video_path, fourcc, self.fps, self.output_resolution)
        
        if self.crop:
            left_crop, top_crop, right_crop, bottom_crop = self.crop
        
        if self.rotation is not None and self.rotation != 0:
            frame = cv2.imread(self.images[0])
            height, width = frame.shape[:2]
            center = (width // 2, height // 2)
            rotation_matrix = cv2.getRotationMatrix2D(center, self.rotation, 1.0)

        success = True
    
        for image in tqdm(self.images, desc="Processing images"):
            frame = cv2.imread(image)

            if not self.input_resolution_fixed and list(frame.shape[:2]) != list(self.input_resolution[::-1]):
                raise Exception(f"Inconsistent pre cropped resolution: {frame.shape[:2]} vs {self.input_resolution[::-1]}")

            if self.input_resolution is not None:
                frame = cv2.resize(frame, self.input_resolution)

            if self.rotation is not None and self.rotation != 0:
                frame = cv2.warpAffine(frame, rotation_matrix, (width, height))
            
            if self.crop is not None:
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
            
            # if self.lower_threshold is not None or self.upper_threshold is not None:

            #     if isinstance(self.lower_threshold, np.ndarray) and isinstance(self.upper_threshold, np.ndarray):
            #         mask = cv2.inRange(frame, self.lower_threshold, self.upper_threshold)
            #         frame = cv2.bitwise_and(frame, frame, mask=mask)
            #     else:
            #         if len(frame.shape) == 3:
            #             gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            #         else:
            #             gray = frame
                    
            #         if self.lower_threshold is not None and self.upper_threshold is not None:
            #             _, thresh = cv2.threshold(gray, self.lower_threshold, self.upper_threshold, cv2.THRESH_BINARY)
            #         elif self.lower_threshold is not None:
            #             _, thresh = cv2.threshold(gray, self.lower_threshold, 255, cv2.THRESH_BINARY)
            #         elif self.upper_threshold is not None:
            #             _, thresh = cv2.threshold(gray, self.upper_threshold, 255, cv2.THRESH_BINARY_INV)
                    
            #         if len(frame.shape) == 3:
            #             frame = cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR)
            #         else:
            #             frame = thresh

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

    