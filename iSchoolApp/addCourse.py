from iSchoolApp import db
from iSchoolApp.models import Lecture


# Adding a course(Lecture) to our database
def addCourseFunc(course_name, class_number, per):
    lec = Lecture(nameOfLecture=course_name, class_number=class_number, percentage=per)
    db.session.add(lec)
    db.session.commit()
