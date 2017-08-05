import cv2
from trackers import FaceTracker

faceTracker = FaceTracker()

vc = cv2.VideoCapture(0)

if vc.isOpened():
    rval, frame = vc.read()
else:
    rval = False

if rval:
    image = frame
    cv2.imwrite('prev.png', image)
    #image = cv2.imread('Pic.jpg')
    faceTracker.update(image)
    faceTracker.drawDebugRects(image)
    cv2.imwrite('Faces.png', image)
else:
    print('Shit...')
