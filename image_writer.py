import cv2
import os
import time

class ImageWriter:
    def __init__(self, description:str):
        self.description = description
        os.makedirs(self.description, exist_ok=True)
    
    # Write image to disc
    def write(self, frame): 
        timestamp = time.strftime("%Y-%m-%d-%H-%M-%S")
        filename = os.path.join(self.description, f"{self.description}-{timestamp}.png")
        cv2.imwrite(filename, frame)
        

