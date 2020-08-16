import os

from flask import request, redirect, url_for
from flask_login import current_user
from iSchoolApp import db
from iSchoolApp.models import User, Lecture, Students
import extract_embeddings
import train_model


def newStudent(first_name, course_list, ID):
    new_student = Students(id=ID, nameOfStudent=first_name)
    for crs_name in course_list:
        lec = Lecture.query.filter_by(nameOfLecture=crs_name).first()
        print(lec)
        lec.students.append(new_student)
        db.session.commit()


def handleImagesFileUpload():
    firstName = "Unknown"
    ID = "null"
    if request.method == "POST":
        firstName = request.form.get("name")
        ID = request.form.get("ID")
        courseName = request.form.getlist("course[]")
        print(courseName)
        newStudent(firstName, courseName, ID)

    if 'photo' in request.files:
        photo = request.files['photo']
        if photo.filename != '':
            if not os.path.exists(os.getcwd() + "\\dataset" + "\\" + ID + "_" + firstName):
                os.makedirs(os.getcwd() + "\\dataset" + "\\" + ID + "_" + firstName)

            photo.save(os.path.join(os.getcwd() + "\\dataset\\" + ID + "_" + firstName, photo.filename))
