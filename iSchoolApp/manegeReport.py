from datetime import datetime, timedelta, time
from iSchoolApp.models import Classroom, StudentsInClassroom, CourseAttendance, Students, Report, Date, Attendance
from flask import request
from flask_login import current_user
from sqlalchemy import Time, cast
from iSchoolApp import db

dict_of_start_class = dict()


def updateReport(lst, st, class_number, course_at, t):
    # first time in class
    print("===")
    print(st)
    print("===")
    print(type(lst[0]))
    for ct in course_at:
        if ct.student_id == int(lst[0]):
            if st == 1:
                if not ct.entry_time:
                    ct.entry_time = t
                    db.session.commit()
                else:
                    updateEntry(ct)
            elif st == 0:
                print("exit1")
                updateExit(ct)

    # not first time

    return


def updateExit(std_from_crs_att):
    if std_from_crs_att.entry_time is not None and \
            (std_from_crs_att.exit_time is None or std_from_crs_att.exit_time < std_from_crs_att.entry_time):
        print("exit2")
        std_from_crs_att.exit_time = datetime.now()
        db.session.commit()
        time = datetime.now().time()

        first_time = std_from_crs_att.entry_time.time()
        time_1 = datetime.combine(datetime.now().date(), first_time)
        time_2 = datetime.combine(datetime.now().date(), time)

        time_elapsed = time_2 - time_1
        print(type(time_elapsed))
        print(time_elapsed)

        if std_from_crs_att.sum is None:
            sum_of_time = (datetime.min + time_elapsed).time()
            print(sum_of_time)
            print(type(sum_of_time))

            std_from_crs_att.sum = datetime.combine(datetime.now().date(), sum_of_time)
            db.session.commit()
        else:
            last_sum = std_from_crs_att.sum.time()
            print(last_sum)

            last_sum = timedelta(hours=last_sum.hour, minutes=last_sum.minute, seconds=last_sum.second,
                                 microseconds=last_sum.microsecond)
            print(last_sum)

            new_sum = time_elapsed + last_sum
            print(new_sum)

            sum_of_time = (datetime.min + new_sum).time()
            print(sum_of_time)
            print(type(sum_of_time))

            std_from_crs_att.sum = datetime.combine(datetime.now().date(), sum_of_time)
            db.session.commit()
            # std_fr_crs_att.sum = datetime.combine(start_time.date, time_elapsed)


def updateEntry(std_fr_crs_att):
    if std_fr_crs_att.exit_time:
        if std_fr_crs_att.exit_time > std_fr_crs_att.entry_time:
            std_fr_crs_att.entry_time = datetime.now()
            db.session.commit()


def startClassFunc(lec_id):
    print(lec_id)
    class_number = -1
    for crs in current_user.lecture:
        if crs.id == lec_id:
            list_std = crs.students
            class_number = crs.class_number
    now = datetime.now()
    dict_of_start_class[class_number] = now
    print(type(now))
    current_time = now.strftime("%H:%M:%S")
    print(current_time)
    print(type(current_time))
    print(class_number)
    if class_number != -1:
        classroom = Classroom.query.filter_by(class_num=class_number).first()
        stuInClassroom = classroom.student_in_class
        print(stuInClassroom)
        print(list_std)
        flag = False
        for std in list_std:
            for stu in stuInClassroom:
                if stu.student_id == std.id:
                    st = CourseAttendance(student_id=std.id, student_name=std.nameOfStudent, entry_time=now,
                                          class_room=class_number, lecture_id=lec_id)
                    db.session.add(st)
                    db.session.commit()
                    flag = True
                    break
                flag = False
            if not flag:
                st = CourseAttendance(student_id=std.id, student_name=std.nameOfStudent,
                                      class_room=class_number, lecture_id=lec_id)
                db.session.add(st)
                db.session.commit()


def endClassFunc(lec_id):
    courses_att = CourseAttendance.query.filter_by(lecture_id=lec_id).all()
    for std in courses_att:
        updateExit(std)
    print(lec_id)
    class_number = -1
    name_of_course = ""
    start_class = None
    for crs in current_user.lecture:
        if crs.id == lec_id:
            list_std = crs.students
            class_number = crs.class_number
            start_class = dict_of_start_class[class_number]
            print(start_class)
            del dict_of_start_class[class_number]
            name_of_course = crs.nameOfLecture
    if class_number != -1:
        # time of len class
        time_elapsed = datetime.now() - start_class
        sum_of_time = (datetime.min + time_elapsed).time()
        len_of_class = datetime.combine(datetime.now().date(), sum_of_time)

        # create a Report for this class
        classroom = Classroom.query.filter_by(class_num=class_number).first()
        stuInCourse = classroom.course
        # create Report
        if not Report.query.filter_by(course_id=lec_id).first():
            rep = Report(course_id=lec_id, course_name=name_of_course)
            db.session.add(rep)
            db.session.commit()

        c_t = datetime.now()
        # create Date for Report
        date_of_lec = Date(lesson_date=c_t, start_class=start_class, end_class=datetime.now(), len_class=len_of_class,
                           att_rep=lec_id)
        db.session.add(date_of_lec)
        db.session.commit()
        dt = Date.query.filter_by(lesson_date=c_t).first()
        for std in stuInCourse:
            # pass any students and update the attendance in percentage

            # pass on all sum of any student and create a
            stud_att = Attendance(dateOfLesson=datetime.now(), student_id=std.student_id,
                                  student_name=std.student_name, sum=std.sum, date_course=dt.lesson_date)
            db.session.add(stud_att)
            db.session.commit()
            print("att work 1")
            # dt.attendance.append(stud_att)
            print("att work 2")
            # dt.attendance.append(stud_att)
            # db.session.add(stud_att)
            print("att work 3")

        for std in stuInCourse:
            db.session.delete(std)
            db.session.commit()
