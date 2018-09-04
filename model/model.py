from werkzeug.security import generate_password_hash, check_password_hash
from vSQL.vorm import *


class Student(Module):
    s_id = column(zintger(), isNotnull=True, isPrimary=True, isAutocount=True)
    s_class_id = column(zintger(), isNotnull=True)
    s_name = column(zchar(10), isNotnull=True)
    s_sex = column(zchar(2), isNotnull=True)
    s_birthday = column(zdate(), isNotnull=True)
    s_address = column(zchar(200), isNotnull=True)

    def init_item(self):
        self.clazz = Class(c_id=self.s_class_id).select(one=True)
        self.subject = Subject(s_id=self.clazz.c_sub_id).select(one=True)


class Class(Module):
    c_id = column(zintger(), isNotnull=True, isPrimary=True, isAutocount=True)
    c_sub_id = column(zchar(100), isNotnull=True)  # 专业
    c_class = column(zintger(2), isNotnull=True)  # 1-4
    c_year = column(zintger(), isNotnull=True)  # 20XX

    def init_item(self):
        self.subject = Subject(s_id=self.c_sub_id).select(one=True)
        self.department = Department(d_id=self.subject.s_depart_id).select(one=True)

    def get_student(self):
        self.student = Student(s_class_id=self.c_id).select(oder='s_id')


class Subject(Module):
    s_id = column(zintger(), isNotnull=True, isPrimary=True, isAutocount=True)
    s_depart_id = column(zchar(100), isNotnull=True)
    s_name = column(zchar(100), isNotnull=True, isUnique=True)  # 专业名

    def init_item(self):
        self.department = Department(d_id=self.s_depart_id).select(one=True)
        self.clazz = Class(c_sub_id=self.s_id).select()


class Department(Module):
    d_id = column(zintger(), isNotnull=True, isPrimary=True, isAutocount=True)
    d_name = column(zchar(20), isNotnull=True)  # 院系名

    def init_item(self):
        self.subject = Subject(s_depart_id=self.d_id).select(oder='s_id')


class Teacher(Module):
    t_id = column(zintger(), isNotnull=True, isPrimary=True, isAutocount=True)
    t_name = column(zchar(10), isNotnull=True)
    t_sex = column(zchar(2), isNotnull=True)

    def init_item(self):
        self.course = Course(c_tea_id=self.t_id).select(one=True)
        self.subject = Subject(s_id= self.course.c_sub_id).select(one=True)


class Course(Module):
    c_id = column(zintger(), isNotnull=True, isPrimary=True, isAutocount=True)
    c_sub_id = column(zintger(), isNotnull=True)
    c_tea_id = column(zintger(), isNotnull=True)
    c_name = column(zchar(200), isNotnull=True)
    c_type = column(zchar(100), isNotnull=True)
    c_term = column(zintger(2), isNotnull=True)
    c_room = column(zchar(100), isNotnull=True)  # [1-9]-[1-5][0-1][1-9]

    def init_item(self):
        self.subject = Subject(s_id=self.c_sub_id).select(one=True)
        self.teacher = Teacher(s_id=self.c_tea_id).select(one=True)
        self.clazz = Class(c_sub_id=self.c_sub_id, c_year=self.c_term).select()

    def get_student(self):
        clazz = Class(c_sub_id=self.c_sub_id, c_year=self.c_term).select()
        student = []
        for c in clazz:
            student += Student(s_class_id=c.c_id).select()
        return student


class Score(Module):
    s_id = column(zintger(), isNotnull=True, isPrimary=True, isAutocount=True)
    s_stu_id = column(zintger(), isNotnull=True)
    s_cou_id = column(zintger(), isNotnull=True)
    s_score = column(zintger())

    def init_item(self):
        self.student = Student(s_id=self.s_stu_id).select(one=True)
        self.course = Course(c_id=self.s_cou_id).select(one=True)
        self.teacher = Teacher(t_id=self.course.c_tea_id).select(one=True)


STUDENT = 1
TEACHER = 2
ADMIN = 3


class Account(Module):
    id = column(zintger(), isNotnull=True)
    account = column(zchar(30), isPrimary=True, isNotnull=True, )
    password_hash = column(zchar(128), isNotnull=True)
    role = column(zintger(), isNotnull=True)

    def listener_begin(self, do):
        if do is Module.M_INSERT:
            if self.account[0] is '1':
                self.role = 1
            else:
                self.role = 2

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    @staticmethod
    def reset_password(token, new_password):
        account = Account().select(one=True)
        if account.id is None:
            return False
        account.password = new_password
        account.update()
        return True