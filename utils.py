def isGray(image):
    return image.ndim < 3

def widthHeightDividedBy(image, divisor):
    h, w = image.shape[:2]
    return (int(w / divisor), int(h / divisor))
