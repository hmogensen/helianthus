import cv2


class ImageFilter:
    def __init__(
        self,
        crop=None,
        gray=False,
        vflip=False,
    ):
        self.crop = crop
        self.gray = gray
        self.vflip = vflip

    def apply(self, frame):
        if self.crop:
            frame = frame[self.crop[2] : self.crop[3], self.crop[0] : self.crop[1]]
        if self.gray:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        if self.vflip:
            frame = frame[::-1]
        return frame
