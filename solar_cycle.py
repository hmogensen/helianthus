from tqdm import tqdm
import numpy as np
import matplotlib.pyplot as plt
from video_toml import parse_video_settings

template = parse_video_settings("garden-gray")

time = []
light_intensity = []

for frame, t in tqdm(template.process_frames(ts=True), 
                  desc="Processing images", 
                  total=len(template.images)):
    time.append(t)
    light_intensity.append(np.median(frame))

plt.plot(time, light_intensity, '.')
plt.show()

