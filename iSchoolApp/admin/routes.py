# import stuff of flask
from flask import render_template, request, redirect, url_for, flash, send_file, Blueprint, session

# getting access to application in app folder and to database and to bcrypt of password
from flask_login import login_required

from iSchoolApp import db, handleImageUploads, recognize_video, bcrypt

# import form of register and login from app folder
from iSchoolApp.admin.forms import AdministerLogin

# import the database from app folder in file models
from iSchoolApp.models import User, Lecture, Administer, Report, Date, \
    Attendance
import os
import extract_embeddings
import train_model
from iSchoolApp.registerCam import registerCamFunc
from iSchoolApp.addCourse import addCourseFunc

admin = Blueprint('admin', __name__)


# Handler in loginAdmin users
@admin.route("/loginAdmin", methods=['GET', 'POST'])
def loginAdminister():
    form = AdministerLogin()
    if form.validate_on_submit():
        admin = Administer.query.filter_by(email=form.email.data).first()
        # check if email and password ok
        # if admin and bcrypt.check_password_hash(admin.password, form.password.data):
        if admin and bcrypt.check_password_hash(admin.password, form.password.data):
            session['admin'] = form.email.data
            # os.environ['ADMIN'] = 'in'
            return redirect(url_for('admin.AdminAccount'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('loginAdmin.html', form=form)


@admin.route("/logoutAdmin")
def logoutAdmin():
    # os.environ['ADMIN'] = 'out'
    session.pop('admin', None)
    print("bla bla bla")
    return redirect(url_for('main_page.home'))


@admin.route("/AdminAccount", methods=['GET'])
def AdminAccount():
    if 'admin' in session:
        course_list = Lecture.query.all()
        return render_template('AdminAccount.html', course_list=course_list)
    return redirect(url_for('admin.loginAdminister'))


@admin.route("/onOffCameras", methods=["POST"])
def onOffCameras():
    act = request.form.get("button")
    print(act)
    if act == "1":
        os.environ['CAM'] = 'on'
        recognize_video.video_recognizer("face_detection_model", "openface_nn4.small2.v1.t7", "output/recognizer.pickle"
                                         , "output/le.pickle")
        return redirect((url_for('admin.AdminAccount')))

    elif act == "0":
        os.environ['CAM'] = 'off'
        return redirect((url_for('admin.AdminAccount')))


# train our model
@admin.route('/train', methods=['GET'])
def train():
    extract_embeddings.extract_embeddings_func("dataset", "output/embeddings.pickle",
                                               "face_detection_model", "openface_nn4.small2.v1.t7")
    train_model.train("output/embeddings.pickle", "output/recognizer.pickle", "output/le.pickle")
    return "blah"


# handler in upload a new image of new students to our database
@admin.route("/handleImageUpload", methods=['POST'])
def handleImagesFileUpload():
    handleImageUploads.handleImagesFileUpload()
    return redirect((url_for('admin.AdminAccount')))


@admin.route("/registerCam", methods=['POST'])
def registerCam():
    c = registerCamFunc()
    print(c)
    return redirect(url_for('admin.AdminAccount'))


@admin.route("/addCourse", methods=['POST'])
def addCourse():
    course_name = request.form.get("name")
    class_number = request.form.get("classNum")
    per = request.form.get("percentage")

    if Lecture.query.filter_by(nameOfLecture=course_name).first():
        flash('Course is already created. Please choice a different course', 'danger')
    else:
        addCourseFunc(course_name, class_number, per)
    return redirect((url_for('admin.AdminAccount')))


@admin.route("/addCourseToTeacher", methods=['POST'])
def addCourseToTeacher():
    teacher_name = request.form.get("teacher_name")
    teacher_id = request.form.get("teacher_id")

    user = User.query.filter_by(id=teacher_id).first()
    courses = request.form.getlist("course[]")
    message = ""
    if courses:
        for cou in courses:
            print(user.get_id())
            c = Lecture.query.filter_by(nameOfLecture=cou).first()
            if c.user_id is None:
                c.user_id = user.get_id()
                db.session.commit()
                message += cou + " "
    if message != "":
        flash(message + 'successfully added!', 'success')
    else:
        flash('all the courses is already used ', 'danger')
    return redirect((url_for('admin.AdminAccount')))
