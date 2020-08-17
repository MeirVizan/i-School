import os

from flask import request, redirect, url_for
from flask_login import current_user
from iSchoolApp import db
from iSchoolApp.models import User, Lecture, Students
import extract_embeddings
import train_model


def newStudent(first_name, course_list, ID):
    lec_of_std = []
    size = 0
    new_student = Students.query.filter_by(id=ID).first()
    # if student is already in our system? get the lecture he have
    if new_student:
        lec_of_std = new_student.lectures
        size = len(lec_of_std)
    # else create a new one
    else:
        new_student = Students(id=ID, nameOfStudent=first_name)

    for crs_name in course_list:
        if size > 0 and Lecture.query.filter_by(nameOfLecture=crs_name).first() in lec_of_std:
            print("is already exist in our system")
        else:
            lec = Lecture.query.filter_by(nameOfLecture=crs_name).first()
            print(lec)
            lec.students.append(new_student)
    db.session.commit()


def handleImagesFileUpload():
    firstName = "Unknown"
    courseName = []
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
            if not os.path.exists(os.getcwd() + "/dataset" + "/" + ID + "_" + firstName):
                os.makedirs(os.getcwd() + "/dataset" + "/" + ID + "_" + firstName)

            photo.save(os.path.join(os.getcwd() + "/dataset/" + ID + "_" + firstName, photo.filename))
