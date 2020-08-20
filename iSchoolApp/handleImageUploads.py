import os

from flask import request, redirect, url_for
from flask_login import current_user
from iSchoolApp import db
from iSchoolApp.models import User, Lecture, Students
import extract_embeddings
import train_model


# adding student function we get the name of student and ID and course list
# and we check if he not register in our system, we submit him to students table,
# if the student is exist in our system of student, we check the list course
# and if he not submit to course list we register him
# else we go out the account page
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


# In this func we get from client info about a new or not new student
# "First Name", "ID", "Course List", "Photo",
# we check if this student is not exist we create for him a new directory of image in dataset directory
# and we make the "Train Model" on dataset directory
# if this student is already exist we save his new image in his directory and make "Train Model"
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
