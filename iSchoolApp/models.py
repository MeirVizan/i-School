# import tool of datetime
from datetime import datetime
# import our database from app folder
from iSchoolApp import db, login_manager
from flask_login import UserMixin
from flask import current_app


# this function to get the user by id
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# class of User with all the attribute the he have in a database
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    lecture = db.relationship('Lecture', backref='year', lazy=True)

    # Ctor of User class
    def __repr__(self):
        return f"User('{self.username}','{self.email}','{self.image_file}')"


assigned = db.Table('assigned',
                    db.Column('lecture_id', db.Integer, db.ForeignKey('lecture.id')),
                    db.Column('students_id', db.Integer, db.ForeignKey('students.id')))


# class of Lecture with all the attribute the he have in a database
class Lecture(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nameOfLecture = db.Column(db.String(20), unique=True, nullable=False)
    class_number = db.Column(db.Integer)
    percentage = db.Column(db.Integer)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    course_att = db.relationship('CourseAttendance', backref='attend', lazy=True)

    # ctor of Lecture class
    def __repr__(self):
        return f"Lecture('{self.nameOfLecture}')"


class Students(db.Model):
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    nameOfStudent = db.Column(db.String(20), unique=False, nullable=False)
    lectures = db.relationship('Lecture', secondary=assigned, backref=db.backref('students', lazy='dynamic'))

    # lecture_id = db.Column(db.Integer, db.ForeignKey('lecture.id'), nullable=False)

    # ctor of Student class
    def __repr__(self):
        return f"Students('{self.nameOfStudent}')"


# class of Administer with all the attribute the he have in a database
class Administer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)

    # Ctor of User class
    def __repr__(self):
        return f"Administer('{self.username}','{self.email}')"


class Cameras(db.Model):
    IP = db.Column(db.Integer, primary_key=True, nullable=False)
    status = db.Column(db.Integer, nullable=False)
    # class_num = db.Column(db.String(5), nullable=False)
    class_number = db.Column(db.Integer, db.ForeignKey('classroom.class_num'))

    # Ctor of User class
    def __repr__(self):
        return f"CamerasIn('{self.IP}','{self.status}')"


"""
class CamerasOut(db.Model):
    IP = db.Column(db.Integer, primary_key=True, nullable=False)
    status = db.Column(db.Integer, default=0)
    class_num = db.Column(db.String(5), nullable=False)
    class_at = db.relationship('Attendance', backref='stu_attOut', lazy=True)

    att = db.Column

    # Ctor of User class
    def __repr__(self):
        return f"CamerasOut('{self.IP}','{self.status}')"
"""


class Classroom(db.Model):
    class_num = db.Column(db.Integer, primary_key=True)
    cam = db.relationship('Cameras', backref='cam', lazy=True)
    course = db.relationship('CourseAttendance', backref='ca', lazy=True)
    student_in_class = db.relationship('StudentsInClassroom', backref='sic', lazy=True)

    # Ctor of Classroom class
    def __repr__(self):
        return f"Classroom('{self.class_num}')"


class StudentsInClassroom(db.Model):
    student_id = db.Column(db.Integer, primary_key=True)
    student_name = db.Column(db.String(20))
    class_room = db.Column(db.Integer, db.ForeignKey('classroom.class_num'))

    # Ctor of StudentsInClassroom class
    def __repr__(self):
        return f"StudentsInClassroom('{self.student_id}','{self.student_name}')"


class CourseAttendance(db.Model):
    lesson_num = db.Column(db.Integer)
    student_id = db.Column(db.Integer, primary_key=True)
    student_name = db.Column(db.String(20))
    entry_time = db.Column(db.DateTime)
    exit_time = db.Column(db.DateTime)
    sum = db.Column(db.DateTime)
    # is_active = db.Column(db.Integer, default=0)

    class_room = db.Column(db.Integer, db.ForeignKey('classroom.class_num'))
    lecture_id = db.Column(db.Integer, db.ForeignKey('lecture.id'))

    # Ctor of CourseAttendance class
    def __repr__(self):
        return f"CourseAttendance('{self.student_id}','{self.student_name}')"


class Report(db.Model):
    course_id = db.Column(db.Integer, primary_key=True)
    course_name = db.Column(db.String(20))
    course_date = db.relationship('Date', backref='cd', lazy=True)

    # Ctor of eReport class
    def __repr__(self):
        return f"Report('{self.course_id}','{self.course_name}')"


"""
finalReport = db.Table('finalReport',
                       db.Column('lesson_date', db.DateTime, db.ForeignKey('date.lesson_date')),
                       db.Column('id', db.Integer, db.ForeignKey('attendance.id')))
"""


class Date(db.Model):
    lesson_date = db.Column(db.DateTime, primary_key=True)
    start_class = db.Column(db.DateTime)
    end_class = db.Column(db.DateTime)
    len_class = db.Column(db.DateTime)
    att = db.relationship('Attendance', backref='at', lazy=True)
    # att = db.relationship('Attendance', secondary=finalReport, backref=db.backref('date', lazy='dynamic'))

    att_rep = db.Column(db.Integer, db.ForeignKey('report.course_id'))

    # Ctor of Date class
    def __repr__(self):
        return f"Date('{self.date}')"


class Attendance(db.Model):
    dateOfLesson = db.Column(db.DateTime, primary_key=True)
    student_id = db.Column(db.Integer)
    student_name = db.Column(db.String(20))
    percentage_att = db.Column(db.Integer)
    sum = db.Column(db.DateTime)
    date_course = db.Column(db.DateTime, db.ForeignKey('date.lesson_date'))

    # Ctor of Attendance class
    def __repr__(self):
        return f"Attendance('{self.student_id}','{self.student_name}')"
