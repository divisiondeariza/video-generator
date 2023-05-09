import numpy as np
from PIL import Image
import cv2


def get_canny_image(image):
    image = np.array(image)
    low_threshold = 100
    high_threshold = 200
    image = cv2.Canny(image, low_threshold, high_threshold)
    image = image[:, :, None]
    image = np.concatenate([image]*3, axis=2)
    canny_image = Image.fromarray(image)
    return canny_image

def squarify_image(image, side=512):
    size = (side, side)
    image.thumbnail(size, Image.Resampling.LANCZOS)
    bg_color = (0, 0, 0)  # Black
    background = Image.new("RGBA", size, bg_color)
    thumbnail_width, thumbnail_height = image.size
    position = (
        (size[0] - thumbnail_width) // 2,
        (size[1] - thumbnail_height) // 2,
    )
    background.paste(image, position)
    return background

