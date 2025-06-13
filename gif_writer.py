from dataclasses import dataclass
from numbers import Number
from pathlib import Path

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