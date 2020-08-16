from iSchoolApp.models import Cameras, Classroom
from flask import request, redirect, url_for
from iSchoolApp import db
from iSchoolApp.addClassroom import addClassroomFunc


def registerCamFunc():
    ip = request.form.get("IP")
    class_num = request.form.get("class")
    status_cam = request.form.get("status")
    addClassroomFunc(class_num)

    cam = Cameras(IP=ip, status=status_cam, class_number=class_num)
    db.session.add(cam)
    db.session.commit()
    return "Cameras successful add"
