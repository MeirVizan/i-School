from iSchoolApp import db
from iSchoolApp.models import Lecture


def addCourseFunc(course_name, class_number, per):
    lec = Lecture(nameOfLecture=course_name, class_number=class_number, percentage=per)
    db.session.add(lec)
    db.session.commit()
