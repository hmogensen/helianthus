import cv2
import sys
from PyQt6.QtWidgets import QApplication, QFileDialog


def select_image_with_pyqt6():
    # Create application
    app = QApplication(sys.argv)

    # Open file dialog
    file_filter = "Image Files (*.jpg *.jpeg *.png *.bmp *.tiff *.tif);;All Files (*)"
    image_path, _ = QFileDialog.getOpenFileName(
        None, "Select an Image", "", file_filter
    )

    # Exit if no file selected
    if not image_path:
        print("No image selected.")
        app.quit()
        return None

    # Clean up Qt application
    app.quit()

    # Read image with OpenCV
    img = cv2.imread(image_path)

    if img is None:
        print(f"Error: Could not load image from {image_path}")
        return None

    print(f"Image coordinates: {img.shape}")

    # Store clicked coordinates
    coordinates = []

    def mouse_callback(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            coordinates.append((x, y))
            print(f"Clicked at: ({x}, {y})")
            cv2.circle(img, (x, y), 3, (0, 255, 0), -1)
            cv2.imshow("Selected Image", img)

    # Create window and set mouse callback
    cv2.namedWindow("Selected Image")
    cv2.setMouseCallback("Selected Image", mouse_callback)
    cv2.imshow("Selected Image", img)

    print("Click on the image to get coordinates. Press 'q' to quit.")

    while True:
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break

    cv2.destroyAllWindows()

    return coordinates, image_path


# Usage
if __name__ == "__main__":
    result = select_image_with_pyqt6()

    if result:
        coords, image_path = result
        print(f"\nSelected image: {image_path}")
        print(f"All coordinates: {coords}")
