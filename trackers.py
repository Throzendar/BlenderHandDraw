import cv2
import rects
import utils

class Face():
    def __init__(self):
        self.faceRect = None

class FaceTracker():

    def __init__(self, scaleFactor=1.1, minNeighbors=2):
        self.scaleFactor = scaleFactor
        self.minNeighbors = minNeighbors
        self._faces = []

        self._faceClassifier = cv2.CascadeClassifier('cascades/haarcascade_frontalface_default.xml')

    @property
    def faces(self):
        return self._faces

    def update(self, image):
        self._faces = []

        if utils.isGray(image):
            image = cv2.equalizeHist(image)
        else:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            cv2.equalizeHist(image, image)

        minSize = utils.widthHeightDividedBy(image, 8)

        faceRects = self._faceClassifier.detectMultiScale(image, self.scaleFactor, self.minNeighbors, 0, minSize)

        if faceRects is not None:
            for faceRect in faceRects:
                face = Face()
                face.faceRect = faceRect

                self._faces.append(face)

    def _detectOneObject(self, classifier, image, rect, imageSizeToMinSizeRatio):
        x, y, w, h = rect
        minSize = utils.widthHeightDividedBy(image, imageSizeToMinSizeRatio)
        subImage = image[y:y + h, x:x + w]

        subRects = classifier.detectMutliScale(subImage, self.scaleFactor, self.minNeighbors, 0, minSize)

        if len(subRects) == 0:
            return None

        subX, subY, subW, subH = subRects[0]
        return (x + subX, y + subY, subW, subH)

    def drawDebugRects(self, image):

        if utils.isGray(image):
            faceColor = 255
        else:
            faceColor = (255, 255, 255)

        for face in self.faces:
            rects.outlineRect(image, face.faceRect, faceColor)
