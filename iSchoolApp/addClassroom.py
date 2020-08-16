from iSchoolApp.models import Cameras, Classroom
from flask import request, redirect, url_for
from iSchoolApp import db


def addClassroomFunc(number):
    if not Classroom.query.filter_by(class_num=number).first():
        cr = Classroom(class_num=number)
        db.session.add(cr)
        db.session.commit()
