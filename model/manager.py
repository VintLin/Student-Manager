from model.model import *
from random import *


class DepartmentManage:
    @staticmethod
    def get_list():
        items = Department().select(oder='d_id')
        for item in items:
            item.init_item()
        return items


class ScoreManage:
    @staticmethod
    def get_list(page):
        page_items = Score().set_pagination(page, 20).select(oder='s_id')
        for item in page_items.items:
            item.init_item()
        return page_items

    @staticmethod
    def get_student_score(stu_id):
        items = Score(s_stu_id=stu_id).select()
        for item in items:
            item.init_item()
        return items

    @staticmethod
    def get_course_score(cou_id):
        items = Score(s_cou_id=cou_id).select()
        for item in items:
            item.init_item()
        return items


class StudentManage:
    @staticmethod
    def get_list(page, flag, id=None):
        pag_items = []
        if flag is ADMIN:
            pag_items = Student().set_pagination(page, 20).select(oder='s_id')
            for item in pag_items.items:
                item.init_item()
        if flag is STUDENT:
            student = Student(s_id=id).select(one=True)
            pag_items = Student(s_class_id=student.s_class_id).select(oder='s_id')
            for item in pag_items:
                item.init_item()
        if flag is TEACHER:
            teacher = Teacher(t_id=id).select(one=True)
            teacher.init_item()
            teacher.course.init_item()
            clazz = teacher.course.clazz
            for i in clazz:
                pag_items += Student(s_class_id=i.c_id).select(oder='s_id')
            for item in pag_items:
                item.init_item()
        return pag_items

    @staticmethod
    def get_search(page, name, id=None):
        if not name:
            p = Pagination(page, 20)
            p.hasItem = False
            return p
        if id:
            student = Student(s_id=id).select(one=True)
            student = Student(s_class_id=student.s_class_id).Like(s_name=name).set_pagination(page, 40).select()
        else:
            student = Student().Like(s_name=name).set_pagination(page, 20).select()
        for item in student.items:
            item.init_item()
        return student

    @staticmethod
    def get_info(id):
        item = Student(s_id=id).select(one=True)
        item.init_item()
        return item


class TeacherManage:
    @staticmethod
    def get_list(page, flag, id=None):
        pag_items = []
        if flag is ADMIN or flag is TEACHER:
            pag_items = Teacher().set_pagination(page, 20).select(oder='t_id')
            for item in pag_items.items:
                item.init_item()
            return pag_items
        if flag is STUDENT:
            student = Student(s_id=id).select(one=True)
            clazz = Class(c_id=student.s_class_id).select(one=True)
            course = Course(c_sub_id=clazz.c_sub_id, c_term=clazz.c_year).select()
            for c in course:
                tea = Teacher(t_id=c.c_tea_id).select(one=True)
                tea.init_item()
                pag_items.append(tea)
            return pag_items

    @staticmethod
    def get_search(page, name):
        if not name:
            p = Pagination(page, 20)
            p.hasItem = False
            return p
        teacher = Teacher().Like(t_name=name).set_pagination(page, 20).select()
        for item in teacher.items:
            item.init_item()
        return teacher

    @staticmethod
    def get_info(id):
        item = Teacher(t_id=id).select(one=True)
        item.init_item()
        return item


class ClassManage:
    @staticmethod
    def get_list(page, flag, id=None):
        if flag is ADMIN or flag is TEACHER:
            pag_items = Class().set_pagination(page, 20).select(oder='c_id')
            for item in pag_items.items:
                item.init_item()
            return pag_items
        if flag is STUDENT:
            student = Student(s_id=id).select(one=True)
            item = Class(c_id=student.s_class_id).select(one=True)
            item.init_item()
            return item

    @staticmethod
    def get_info(id):
        item = Class(c_id=id).select(one=True)
        item.init_item()
        item.get_student()
        return item


class CourseManage:
    @staticmethod
    def get_info(id):
        item = Course(c_id=id).select(one=True)
        item.init_item()
        return item


class SubjectManage:
    @staticmethod
    def get_info(id):
        item = Subject(s_id=id).select(one=True)
        item.init_item()
        return item


def insert_admin():
    account = Account()
    account.account = '3000001'
    account.password = '3000001'
    account.id = 801
    account.insert()


def random_account():
    student = Student().select(oder='s_id', asc=True)
    for s in student:
        account = Account()
        code = get_account(1, s.s_id)
        account.id = s.s_id
        account.account = code
        account.password = code
        account.insert()

    teacher = Teacher().select(oder='t_id', asc=True)
    for t in teacher:
        account = Account()
        code = get_account(2, t.t_id)
        account.id = t.t_id
        account.account = code
        account.password = code
        account.insert()


def get_account(head, id):
    id = str(id)
    while len(id) < 6:
        id = '0' + id
    return str(head) + id


def random_score():
    clazz = Class().select(oder='c_id', asc=True)
    course_list = ['C语言', '大学英语', '高等数学', '毛泽东思想和中国特色主义理论体系概论',
                   '中国近代史纲要', '大学体育', '思想道德修养与法律基础', '大学生心理健康教育',
                   '马克思主义基本原理概论', '大学物理']
    sub = set()
    year = set()
    for c in clazz:
        if c.c_sub_id not in sub:
            sub.add(c.c_sub_id)
            year = set()
        if c.c_year not in year:
            for cou in course_list:
                tea = Teacher(t_name=random_name(), t_sex=rand_sex()).insert()
                year.add(c.c_year)
                course = Course()
                course.c_sub_id = c.c_sub_id
                course.c_tea_id = tea.t_id
                course.c_name = cou
                course.c_type = '公共必修'
                course.c_term = c.c_year
                course.c_room = '{}-{}0{}'.format(randint(1, 9), randint(1, 5), randint(1, 9))
                course = course.insert()
                id = c.c_id
                stu1 = Student(s_class_id=id).select(oder='s_id')
                stu2 = Student(s_class_id=id+1).select(oder='s_id')
                for stud in stu1, stu2:
                    for s in stud:
                        score = Score()
                        score.s_score = randint(40, 99)
                        score.s_stu_id = s.s_id
                        score.s_cou_id = course.c_id
                        score.insert()


def random_name():
    xin = ['陈', '刘', '吴', '林', '李', '杨', '周', '郑', '王', '高', '张', '蔡', '贺', '钟', '赖', '许', '姜', '叶',
           '胡', '曹', '关', '孙', '袁', '董', '习', '毛', '江', '邓', '钱']
    name = ['建', '元', '光', '朔', '狩', '鼎', '封', '太', '初', '天', '汉', '太', '始', '征', '和', '后',
            '始', '凤', '平', '本', '始', '地', '节', '元', '康', '神', '爵', '五', '凤', '甘', '露', '黄',
            '龙', '初', '永', '光', '建', '昭', '竟', '宁', '建', '始', '河', '平', '阳', '朔', '鸿', '嘉',
            '永', '始', '延', '绥', '和', '建', '平', '寿', '元', '始', '居', '摄']
    x = xin[randint(0, len(xin) - 1)]
    n = ''
    for k in range(1, 3):
        n += name[randint(0, len(name) - 1)]
    return x + n


def rand_sex():
    Sex = ['男', '女']
    return Sex[randint(0, 1)]


def random_student():
    xin = ['陈', '刘', '吴', '林', '李', '杨', '周', '郑', '王', '高', '张', '蔡', '贺', '钟', '赖', '许', '姜', '叶',
           '胡', '曹', '关', '孙', '袁', '董', '习', '毛', '江', '邓', '钱']
    name = ['建', '元', '光', '朔', '狩', '鼎', '封', '太', '初', '天', '汉', '太', '始', '征', '和', '后',
            '始', '凤', '平', '本', '始', '地', '节', '元', '康', '神', '爵', '五', '凤', '甘', '露', '黄',
            '龙', '初', '永', '光', '建', '昭', '竟', '宁', '建', '始', '河', '平', '阳', '朔', '鸿', '嘉',
            '永', '始', '延', '绥', '和', '建', '平', '寿', '元', '始', '居', '摄']
    subject = ['计算机系', '工商管理系', '土木系']
    department = {'计算机系': ['软件工程', '通信工程', '物联网工程'],
                  '工商管理系': ['国际金融', '市场营销', '广告设计', '电子商务'],
                  '土木系': ['土木工程', '工程造价', '建筑力学']}
    province = ['福建省', '浙江省', '江苏省', '广东省', '四川省']
    address = {'福建省': ['福州市', '宁德市', '漳州市', '厦门市'],
               '浙江省': ['杭州市', '台州市', '金华市', '宁波市'],
               '江苏省': ['南京市', '苏州市', '无锡市', '江阴市'],
               '广东省': ['广东市', '东莞市', '潮州市', '深圳市'],
               '四川省': ['成都市', '绵阳市', '攀枝花市', '都江堰市']}
    course = ['C语言', '大学英语', '高等数学', '毛泽东思想和中国特色主义理论体系概论',
              '中国近代史纲要', '大学体育', '思想道德修养与法律基础', '大学生心理健康教育',
              '马克思主义基本原理概论', '大学物理']
    year = [1995, 1996, 1997, 1998, 1999]
    Sex = ['男', '女']

    for item in subject:
        dep = Department(d_name=item).insert()
        for j in department.get(item):
            su = Subject(s_depart_id=dep.d_id, s_name=j).insert()
            for y in range(2014, 2018):
                for cl in range(1, 3):
                    room = '{}-{}0{}'.format(randint(1, 9), randint(1, 5), randint(1, 9))
                    c = Class(c_sub_id=su.s_id, c_class=cl, c_year=y, c_room=room).insert()
                    for s in range(40):
                        student = Student()
                        x = xin[randint(0, len(xin) - 1)]
                        n = ''
                        for k in range(1, 3):
                            n += name[randint(0, len(name) - 1)]
                        pro = province[randint(0, 4)]
                        add = address.get(pro)[randint(0, len(address.get(pro)) - 1)]
                        month = randint(1, 12)
                        day = randint(1, 28)
                        student.s_name = x + n
                        student.s_class_id = c.c_id
                        student.s_sex = Sex[randint(0, 1)]
                        student.s_address = pro + ' ' + add
                        student.s_birthday = str(y - randint(19, 22)) + '-' + str(month) + '-' + str(day)
                        student.insert()
