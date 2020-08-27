# import the necessary packages
from datetime import datetime
from iSchoolApp.manegeReport import updateReport
from imutils.video import VideoStream, WebcamVideoStream
from imutils.video import FPS
from iSchoolApp.models import User, Lecture, Students, Cameras, CourseAttendance, Classroom, StudentsInClassroom
from iSchoolApp import db
import numpy as np
import argparse
import imutils
import pickle
import time
import cv2
import os


# ip = ip of current cam
# era, stud_id= captured student, locateIP = list that holds the ips,
# dictsOfCapturedStuds = list of dictionaries
def updateDictOfCapturedStuds(ip, stud_id, locateIP, dictsOfCapturedStuds, delete):
    index = locateIP.index(ip)
    if delete == 0:
        if stud_id not in dictsOfCapturedStuds[index].keys():
            dictsOfCapturedStuds[index][stud_id] = 1
        else:
            dictsOfCapturedStuds[index][stud_id] = dictsOfCapturedStuds[index][stud_id] + 1
        return dictsOfCapturedStuds[index][stud_id]
    else:
        dictsOfCapturedStuds[index].clear()
        return 0


def loopOverDetections(class_number, st, detections, frame, h, w, embedder, recognizer, le, confidence_arg, locateIP,
                       dictsOfCapturedStuds, ip):
    # loop over the detections

    for i in range(0, detections.shape[2]):
        # extract the confidence (i.e., probability) associated with
        # the prediction
        confidence = detections[0, 0, i, 2]

        # filter out weak detections
        if confidence > confidence_arg:
            # compute the (x, y)-coordinates of the bounding box for
            # the face
            box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
            (startX, startY, endX, endY) = box.astype("int")
            # extract the face ROI
            face = frame[startY:endY, startX:endX]
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

            # perform classification to recognize the face
            preds = recognizer.predict_proba(vec)[0]
            j = np.argmax(preds)
            proba = preds[j]
            name = le.classes_[j]

            # draw the bounding box of the face along with the
            # associated probability
            idAndName = name.split('_')
            if name != "unknown":
                if updateDictOfCapturedStuds(ip, idAndName[0], locateIP, dictsOfCapturedStuds, 0) == 5:
                    updateDictOfCapturedStuds(ip, idAndName[0], locateIP, dictsOfCapturedStuds, 1)
                    cr = Classroom.query.filter_by(class_num=class_number).first()
                    crAt = cr.course
                    if crAt:
                        t = datetime.now()
                        updateReport(idAndName, st, class_number, crAt, t)
                    if st == 1:  # status 1 means entry
                        if not StudentsInClassroom.query.filter_by(student_id=idAndName[0]).first():
                            sic = StudentsInClassroom(student_id=idAndName[0], student_name=idAndName[1],
                                                      class_room=class_number)
                            db.session.add(sic)
                            db.session.commit()
                    else:
                        sic = StudentsInClassroom.query.filter_by(student_id=idAndName[0]).first()
                        if sic:
                            db.session.delete(sic)
                            db.session.commit()

            text = "{}: {:.2f}%".format(name, proba * 100)
            y = startY - 10 if startY - 10 > 10 else startY + 10
            cv2.rectangle(frame, (startX, startY), (endX, endY),
                          (0, 0, 255), 2)
            cv2.putText(frame, text, (startX, y),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 255), 2)


def isCameraAvailable(ip):
    print("1")
    cap = cv2.VideoCapture(ip)
    print("1.2")

    if cap is None or not cap.isOpened():
        return False
    print("1.3")
    cap.release()
    return True


def video_recognizer(detector, embedding_model, recognizer, le, confidence_arg=0.5):
    # load our serialized face detector from disk
    print("[INFO] loading face detector...")
    protoPath = os.path.sep.join([detector, "deploy.prototxt"])
    modelPath = os.path.sep.join([detector, "res10_300x300_ssd_iter_140000.caffemodel"])

    # detector_1 = cv2.dnn.readNetFromCaffe(protoPath, modelPath)
    # detector_2 = cv2.dnn.readNetFromCaffe(protoPath, modelPath)

    # load our serialized face embedding model from disk
    print("[INFO] loading face recognizer...")
    embedder = cv2.dnn.readNetFromTorch(embedding_model)
    print("cv2")
    # load the actual face recognition model along with the label encoder
    recognizer = pickle.loads(open(recognizer, "rb").read())
    le = pickle.loads(open(le, "rb").read())

    # initialize the video stream, then allow the camera sensor to warm up
    print("[INFO] starting video stream...")

    vs = []
    detectors = []
    cams = Cameras.query.all()
    locateIP = []
    dictsOfCapturedStuds = []

    for c in cams:

        print(c)
        if isCameraAvailable(c.IP):
            locateIP.append(c.IP)
            dictsOfCapturedStuds.append(dict())
            vs.append(VideoStream(src=c.IP).start())
            detectors.append(cv2.dnn.readNetFromCaffe(protoPath, modelPath))
            print("vs:" + str(len(vs)) + "detector:" + str(len(detectors)))


    time.sleep(2.0)

    # start the FPS throughput estimator
    fps = FPS().start()

    frame_dict = {}

    # loop over frames from the video file stream
    while True:

        # grab the frame from the threaded video stream

        frame = []
        h_w = []
        imageBlob = []

        for v in vs:
            frame.append(v.read())

        for f in frame:
            # resize the frame to have a width of 600 pixels (while
            # maintaining the aspect ratio), and then grab the image
            # dimensions
            f = imutils.resize(f, width=600)
            h_w.append(f.shape[:2])
            # construct a blob from the image
            imageBlob.append(cv2.dnn.blobFromImage(
                cv2.resize(f, (300, 300)), 1.0, (300, 300),
                (104.0, 177.0, 123.0), swapRB=False, crop=False))

        # (h_1, w_1) = frame_1.shape[:2]
        # apply OpenCV's deep learning-based face detector to localize
        # faces in the input image
        # detector.setInput(imageBlob_1)

        detections = []
        for i in range(0, len(imageBlob)):
            detectors[i].setInput(imageBlob[i])
            detections.append(detectors[i].forward())

        # detector_1.setInput(imageBlob_1)
        # detector_2.setInput(imageBlob_2)

        # detections_1 = detector_1.forward()
        # detections_2 = detector_2.forward()

        for i in range(0, len(detections)):
            (h, w) = h_w[i]
            loopOverDetections(cams[i].class_number, cams[i].status, detections[i], frame[i], h, w, embedder,
                               recognizer, le, confidence_arg, locateIP, dictsOfCapturedStuds, cams[i].IP)

        # update the FPS counter
        fps.update()
        join_frame = cv2.hconcat(frame)
        # cv2.imshow('frame', join_frame)

        # show the output frame

        # cv2.imshow("Frame", frame)
        cv2.imshow("Frame", join_frame)

        key = cv2.waitKey(1) & 0xFF

        # if the `q` key was pressed, break from the loop
        if key == ord("q"):
            break
        if os.environ.get('CAM') == 'off':
            break
    # stop the timer and display FPS information
    fps.stop()
    print("[INFO] elasped time: {:.2f}".format(fps.elapsed()))
    print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))
    # do a bit of cleanup
    cv2.destroyAllWindows()

    for v in vs:
        print("stop camera")
        v.stop()
    print("hhhhhhhhhhhhhhhhhhhh")