import cv2
import rects
import utils

class Pointer():
    def __init__(self):
        self.rect = None

class PointerTracker():

    def __init__(self, scaleFactor=1.1, minNeighbors=2):
        self.scaleFactor = scaleFactor
        self.minNeighbors = minNeighbors
        self._pointers = []

        self._classifier = cv2.CascadeClassifier('cascades/haarcascade_fist.xml')

    @property
    def pointers(self):
        return self._pointers

    def update(self, image):
        self._pointers = []

        if utils.isGray(image):
            image = cv2.equalizeHist(image)
        else:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            cv2.equalizeHist(image, image)

        minSize = utils.widthHeightDividedBy(image, 8)

        pointer_rects = self._classifier.detectMultiScale(image, self.scaleFactor, self.minNeighbors, 0, minSize)

        if pointer_rects is not None:
            for rect in pointer_rects:
                pointer = Pointer()
                pointer.rect = rect

                self._pointers.append(pointer)

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
