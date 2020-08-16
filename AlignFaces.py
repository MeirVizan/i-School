# import the necessary packages
from imutils.face_utils import FaceAligner
from imutils.face_utils import rect_to_bb
import argparse
import imutils
import dlib
import cv2

# construct the argument parser and parse the arguments
#ap = argparse.ArgumentParser()
#ap.add_argument("-p", "--shape-predictor", default="shape_predictor_68_face_landmarks.dat",
#                help="path to facial landmark predictor")
#ap.add_argument("-i", "--image", required=False,
 #               help="path to input image")
#args = vars(ap.parse_args())


def alignFace(predictotDLIB, imagePath):
    # initialize dlib's face detector (HOG-based) and then create
    # the facial landmark predictor and the face aligner
    detector = dlib.get_frontal_face_detector()
#    print(args["shape_predictor"])
    # predictor = dlib.shape_predictor("face_detection_model/shape_predictor_68_face_landmarks.dat")
    predictor = dlib.shape_predictor(predictotDLIB)
    fa = FaceAligner(predictor, desiredFaceWidth=256)

    # load the input image, resize it, and convert it to grayscale
    image = cv2.imread(imagePath)
    image = imutils.resize(image, width=800)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # show the original input image and detect faces in the grayscale
    # image
    #cv2.imshow("Input", image)
    rects = detector(gray, 2)

    # loop over the face detections
    faceAligned = None
    for rect in rects:
        # extract the ROI of the *original* face, then align the face
        # using facial landmarks
        (x, y, w, h) = rect_to_bb(rect)
        faceOrig = imutils.resize(image[y:y + h, x:x + w], width=256)
        faceAligned = fa.align(image, gray, rect)

        # display the output images
        #cv2.imshow("Original", faceOrig)
        #cv2.imshow("Aligned", faceAligned)
        #cv2.waitKey(0)

    return faceAligned
