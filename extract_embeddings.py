# import the necessary packages
from train_model import train
from imutils import paths
from AlignFaces import alignFace
import numpy as np
import argparse
import imutils
import pickle
import cv2
import os


def extract_embeddings_func(dataset, embeddings, detector, embedding_model, confidence_arg=0.5):
    # load our serialized face detector from disk
    print("[INFO] loading face detector...")
    # protoPath = os.path.sep.join([args["detector"], "deploy.prototxt"])
    protoPath = os.path.sep.join([detector, "deploy.prototxt"])
    modelPath = os.path.sep.join([detector, "res10_300x300_ssd_iter_140000.caffemodel"])
    detector = cv2.dnn.readNetFromCaffe(protoPath, modelPath)

    # load our serialized face embedding model from disk
    print("[INFO] loading face recognizer...")
    embedder = cv2.dnn.readNetFromTorch(embedding_model)

    # grab the paths to the input images in our dataset
    print("[INFO] quantifying faces...")
    imagePaths = list(paths.list_images(dataset))

    # initialize our lists of extracted facial embeddings and
    # corresponding people names
    knownEmbeddings = []
    knownNames = []

    # initialize the total number of faces processed
    total = 0

    # loop over the image paths
    for (i, imagePath) in enumerate(imagePaths):
        alignedFace = alignFace("shape_predictor_68_face_landmarks.dat", imagePath)
        if alignedFace is not None:
            try:
                os.remove(imagePath)
                cv2.imwrite(imagePath, alignedFace)

                # extract the person name from the image path
                print("[INFO] processing image {}/{}".format(i + 1,
                                                             len(imagePaths)))
                name = imagePath.split(os.path.sep)[-2]

                # load the image, resize it to have a width of 600 pixels (while
                # maintaining the aspect ratio), and then grab the image
                # dimensions
                image = cv2.imread(imagePath)
                image = imutils.resize(image, width=600)
                (h, w) = image.shape[:2]

                # construct a blob from the image
                imageBlob = cv2.dnn.blobFromImage(
                    cv2.resize(image, (300, 300)), 1.0, (300, 300),
                    (104.0, 177.0, 123.0), swapRB=False, crop=False)

                # apply OpenCV's deep learning-based face detector to localize
                # faces in the input image
                detector.setInput(imageBlob)
                detections = detector.forward()

                # ensure at least one face was found
                if len(detections) > 0:
                    # we're making the assumption that each image has only ONE
                    # face, so find the bounding box with the largest probability
                    i = np.argmax(detections[0, 0, :, 2])
                    confidence = detections[0, 0, i, 2]

                    # ensure that the detection with the largest probability also
                    # means our minimum probability test (thus helping filter out
                    # weak detections)
                    if confidence > confidence_arg:
                        # compute the (x, y)-coordinates of the bounding box for
                        # the face
                        box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                        (startX, startY, endX, endY) = box.astype("int")

                        # extract the face ROI and grab the ROI dimensions
                        face = image[startY:endY, startX:endX]
                        (fH, fW) = face.shape[:2]

                        # ensure the face width and height are sufficiently large
                        if fW < 20 or fH < 20:
                            continue

                        # construct a blob for the face ROI, then pass the blob
                        # through our face embedding model to obtain the 128-d
                        # quantification of the face
                        faceBlob = cv2.dnn.blobFromImage(face, 1.0 / 255,
                                                         (96, 96), (0, 0, 0), swapRB=True, crop=False)
                        embedder.setInput(faceBlob)
                        vec = embedder.forward()

                        # add the name of the person + corresponding face
                        # embedding to their respective lists
                        knownNames.append(name)
                        knownEmbeddings.append(vec.flatten())
                        total += 1


            except:
                os.rename(imagePath, os.path.splitext(imagePath)[0] + ".Error")
                print(imagePath + ": was not aligned")
        else:
            print(imagePath)

    # dump the facial embeddings + names to disk
    print("[INFO] serializing {} encodings...".format(total))
    data = {"embeddings": knownEmbeddings, "names": knownNames}
    f = open(embeddings, "wb")
    f.write(pickle.dumps(data))
    f.close()
