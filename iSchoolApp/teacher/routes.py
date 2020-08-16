# import stuff of flask
from flask import render_template, request, redirect, url_for, flash, send_file, Blueprint

from iSchoolApp.teacher.forms import LoginForm, UpdateAccountForm, RegistrationForm

# getting access to application in app folder and to database and to bcrypt of password
from iSchoolApp import db, handleImageUploads, recognize_video, bcrypt

# import flask_login for login account
from flask_login import login_user, current_user, logout_user, login_required

from iSchoolApp.manegeReport import startClassFunc, endClassFunc

import xlsxwriter
from datetime import datetime

# import the database from app folder in file models
from iSchoolApp.models import User, Lecture, Administer, Report, Date, \
    Attendance

teacher = Blueprint('teacher', __name__)


# import form of register and login from app folder


def getListOfCourseAvailable(listOfCourses):
    newListOfCourses = []
    for crs in listOfCourses:
        if not User.query.filter_by(id=crs.user_id).first():
            newListOfCourses.append(crs)
        else:
            print("&&&&&&")
            print(User.query.filter_by(id=crs.user_id).first())
            print("&&&&&&")
    return newListOfCourses


# Handler in register users
@teacher.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main_page.home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        # hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        # user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        user = User(username=form.username.data, email=form.email.data, password=form.password.data)
        # get a connection to save data in database
        db.session.add(user)
        # save data in database
        # db.session.commit()
        courses = request.form.getlist("course[]")
        if courses:
            for cou in courses:
                print(user.get_id())
                c = Lecture.query.filter_by(nameOfLecture=cou).first()
                c.user_id = user.get_id()
                db.session.commit()
                print("===")
                print(cou)
                print("===")
            flash('Your account has been created ! You are now able to log in ', 'success')
            return redirect(url_for('teacher.login'))
        else:
            flash('Register Unsuccessful. Please choice course', 'danger')

    course_list = getListOfCourseAvailable(Lecture.query.all())
    return render_template('register.html', form=form, course_list=course_list)


# Handler in login users
@teacher.route("/login", methods=['GET', 'POST'])
def login():
    # check if the user is authenticated then send him to home page
    if current_user.is_authenticated:
        return redirect(url_for('main_page.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        # check if email and password ok
        # if user and bcrypt.check_password_hash(user.password, form.password.data):
        if user and user.password == form.password.data:
            login_user(user, remember=form.remember.data)
            # if the user try to get to account and he logout so when he will be login he get the page
            next_page = request.args.get('next')
            if next_page:
                print("1")
                return redirect(next_page)
            else:
                print("2")
                return redirect((url_for('main_page.home')))
            # return redirect(next_page) if next_page else redirect((url_for('home')))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', form=form)


@teacher.route("/logout")
def logout():
    logout_user()
    # send the user to home page
    return redirect((url_for('main_page.home')))


@teacher.route("/account")
# check if the user is login before and then he send you to account page
@login_required
def account():
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    course_list = current_user.lecture
    return render_template('account.html', image_file=image_file, course_list=course_list)


@teacher.route("/updateAccountDetails", methods=['GET', 'POST'])
@login_required
def updateAccountDetails():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        current_user.email = form.email.data
        db.session.commit()
        flash('your account has been updated!', 'success')
        return redirect(url_for('teacher.account'))
    elif request.method == 'GET':
        form.email.data = current_user.email
    return render_template('updateAccountDetails.html', form=form)


@teacher.route("/course", methods=['GET'])
@login_required
def course():
    course_list = current_user.lecture
    print(course_list)
    size = len(course_list)
    if size > 0:
        return render_template('course.html', course_list=course_list, size=size)
    else:
        flash('You don\'t  have courses', 'danger')
        return redirect((url_for('teacher.account')))


# execute our software of face recognition
@teacher.route('/execute', methods=['GET', 'POST'])
def execute():
    dataStart = -1
    dataEnd = -1
    print("=====")
    data = request.get_json()
    print(data['id'])
    print(data['name'])
    print("=====")
    flag_bool = False
    lec = Lecture.query.filter_by(id=int(data['id'])).first()
    print("$$$$$$")
    for std in lec.students:
        flag_bool = True
    print(flag_bool)
    print("$$$$$$")
    if not flag_bool:
        print("bla bla")
        flash('You don\'t  have courses', 'danger')
        flash('You dont have students in this class', 'danger')
        return redirect(url_for('teacher.course'))

    if data['name'] == "courseIdStart":
        startClassFunc(int(data['id']))

    if data['name'] == "courseIdEnd":
        endClassFunc(int(data['id']))

    return redirect((url_for('teacher.course')))


@teacher.route('/report', methods=['GET', 'POST'])
def report():
    print("=====")
    # data = request.get_json()
    courseId = request.form.get("courseIdReport")
    print(courseId)
    # print(data['name'])
    print("=====")

    lec = Lecture.query.filter_by(id=courseId).first()
    rep = Report.query.filter_by(course_id=courseId).first()
    list_of_dates = rep.course_date
    std_list_of_lecture = lec.students
    return render_template('report.html', list_of_dates=list_of_dates, std_list_of_lecture=std_list_of_lecture)


def getLenClass(start, end):
    time_1 = datetime.combine(datetime.now().date(), start.time())
    time_2 = datetime.combine(datetime.now().date(), end.time())

    time_elapsed = time_2 - time_1
    print(time_elapsed)
    return (datetime.min + time_elapsed).time()


def getPreOfAtt(sumOfLesson, lenOfClass):
    date_time1 = datetime.strptime(sumOfLesson, "%H:%M:%S.%f")
    date_time2 = datetime.strptime(lenOfClass, "%H:%M:%S.%f")

    print(date_time1)
    print(date_time2)

    a_timedelta1 = date_time1 - datetime(1900, 1, 1)
    seconds1 = a_timedelta1.total_seconds()

    a_timedelta2 = date_time2 - datetime(1900, 1, 1)
    seconds2 = a_timedelta2.total_seconds()
    print(seconds1)
    print(seconds2)
    return seconds1 / seconds2


@teacher.route('/datesExport', methods=['POST'])
def datesExport():
    date = request.form.get("dates")
    justDate = date.split(' ')
    fileName = justDate[0]
    dateObj = Date.query.filter_by(lesson_date=date).first()
    repObj = Report.query.filter_by(course_id=dateObj.att_rep).first()
    pathOfXLSX = "cache\\" + repObj.course_name + fileName + ".xlsx"

    rep = xlsxwriter.Workbook(pathOfXLSX)
    worksheet = rep.add_worksheet()
    worksheet.write(0, 0, "id")
    worksheet.write(0, 1, "name")
    worksheet.write(0, 2, "sum of attendance")
    worksheet.write(0, 3, "percentage")

    i = 1
    attendance = Attendance.query.filter_by(date_course=date).all()
    for att in attendance:
        print(att.student_name)
        sumOfLesson = str(att.sum).split(' ')
        if sumOfLesson[0] != 'None':
            dateCourse = Date.query.filter_by(lesson_date=att.date_course).first()
            len_of_class = getLenClass(dateCourse.start_class, dateCourse.end_class)
            percentageAttendance = getPreOfAtt(sumOfLesson[1], str(len_of_class))
            worksheet.write(i, 2, sumOfLesson[1])
            worksheet.write(i, 3, round(percentageAttendance, 2) * 100)
        else:
            worksheet.write(i, 2, 0)
            worksheet.write(i, 3, 0)

        worksheet.write(i, 0, att.student_id)
        worksheet.write(i, 1, att.student_name)

        i += 1
    rep.close()

    try:
        fileName = pathOfXLSX.split("\\")
        return send_file("../" + pathOfXLSX, attachment_filename=fileName[1], as_attachment=True)
    except Exception as e:
        return str(e)
    print("---------------------")

    return redirect((url_for('teacher.course')))


@teacher.route('/studentsExport', methods=['POST'])
def studentsExport():
    std = request.form.get("student")
    pathOfXLSX = "cache\\" + std + ".xlsx"
    rep = xlsxwriter.Workbook(pathOfXLSX)
    worksheet = rep.add_worksheet()
    worksheet.write(0, 0, "date")
    worksheet.write(0, 1, "sum of attendance")
    worksheet.write(0, 2, "length of class")
    worksheet.write(0, 3, "percentage")

    i = 1
    attendance = Attendance.query.filter_by(student_name=std).all()
    for att in attendance:
        dateCourse = Date.query.filter_by(lesson_date=att.date_course).first()
        len_of_class = getLenClass(dateCourse.start_class, dateCourse.end_class)

        print("*****")
        print(type(len_of_class))
        print("*****")

        dateLesson = str(att.dateOfLesson)
        dl = dateLesson.split(' ')
        worksheet.write(i, 0, dl[0])
        worksheet.write(i, 2, str(len_of_class))

        sumOfLesson = str(att.sum).split(' ')
        if sumOfLesson[0] != 'None':
            worksheet.write(i, 1, sumOfLesson[1])
            percentageAttendance = getPreOfAtt(sumOfLesson[1], str(len_of_class))
            worksheet.write(i, 3, round(percentageAttendance, 2) * 100)
            print("@@@")
            print(round(percentageAttendance, 2) * 100)
            print("@@@")
        else:
            worksheet.write(i, 1, 0)
            worksheet.write(i, 3, 0)

        i += 1

    rep.close()
    try:
        fileName = pathOfXLSX.split("\\")
        return send_file("../" + pathOfXLSX, attachment_filename=fileName[1], as_attachment=True)
    except Exception as e:
        return str(e)
    print("---------------------")

    print(std)
    print("###")
    print(attendance)
    print("###")
    return redirect((url_for('teacher.course')))
