from flask import render_template, redirect, url_for, abort, flash, request, session
from model.manager import *
from .forms import *
from . import main


def login_required():
    id = session.get('id')
    role = session.get('role')
    if not id or not role:
        return False
    return True


@main.route('/', methods=['GET', 'POST'])
def index():
    flag = None
    name = ''
    if login_required():
        flag = session.get('role')
        if flag is 1:
            stu = Student(s_id=session.get('id')).select(one=True)
            name = stu.s_name
        if flag is 2:
            tea = Teacher(t_id=session.get('id')).select(one=True)
            name = tea.t_name
        if flag is 3:
            name = 'ADMIN'
    return render_template('/main/index.html', flag=flag, name=name)


@main.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        account = Account(account=form.account.data).select(one=True)
        if account.password_hash is not None and account.verify_password(form.password.data):
            session['id'] = account.id
            session['role'] = account.role
            flash('登录成功.')
            return redirect(request.args.get('next') or url_for('main.index'))
        flash('账号或密码输入错误.')
    return render_template('/auth/login.html', form=form)


@main.route('/logout', methods=['GET', 'POST'])
def logout():
    session.pop('id', None)
    session.pop('role', None)
    flash('退出登录.')
    return redirect(url_for('main.index'))


@main.route('/score', methods=['GET', 'POST'])
def score():
    if login_required():
        print(session.get('role'))
        if session.get('role') is STUDENT:
            return redirect(url_for('main.student_score', id=session.get('id')))
        if session.get('role') is TEACHER:
            tea = Teacher(t_id=session.get('id')).select(one=True)
            tea.init_item()
            return redirect(url_for('main.course_score', id=tea.course.c_id))
        if session.get('role') is ADMIN:
            page = request.args.get('page', 1, type=int)
            pagination = ScoreManage.get_list(page)
            return render_template('/main/score.html', pagination=pagination)
    else:
        return redirect(url_for('main.login'))


@main.route('/student/score/<int:id>', methods=['GET', 'POST'])
def student_score(id):
    items = ScoreManage.get_student_score(id)
    return render_template('/info/score.html', items=items)


@main.route('/course/score/<int:id>', methods=['GET', 'POST'])
def course_score(id):
    items = ScoreManage.get_course_score(id)
    return render_template('/info/score.html', items=items)


@main.route('/course/<int:id>', methods=['GET', 'POST'])
def course_info(id):
    item = CourseManage.get_info(id)
    return render_template('/info/course.html', item=item)


@main.route('/student', methods=['GET', 'POST'])
def student():
    if login_required():
        page = request.args.get('page', 1, type=int)
        pagination = StudentManage.get_list(page, session.get('role'), session.get('id'))
        return render_template('/main/student.html', pagination=pagination, flag=session.get('role'))
    else:
        return redirect(url_for('main.login'))


@main.route('/student/<int:id>', methods=['GET', 'POST'])
def student_info(id):
    item = StudentManage.get_info(id)
    return render_template('/info/student.html', item=item)


@main.route('/score/set', methods=['GET', 'POST'])
def score_set():
    if login_required():
        course = Course(c_tea_id=session.get('id')).select(one=True)
        items = course.get_student()
        return render_template('/set/score.html', items=items)


@main.route('/teacher/set', methods=['GET', 'POST'])
def teacher_set():
    id = request.args.get('id', 1, type=int)
    insert = request.args.get('insert', 0, type=int)
    form = TeacherForm()
    if login_required():
        if form.validate_on_submit():
            if form.sex.data is 1:
                sex = '女'
            else:
                sex = '男'
            name = form.name.data
            if insert:
                Teacher(t_sex=sex, t_name=name).insert()
                flash('添加成功.')
            else:
                Teacher(t_id=id, t_sex=sex, t_name=name).update()
                flash('更新成功.')
        if not insert:
            teacher = Teacher(t_id=id).select(one=True)
            if teacher.t_sex is '男':
                sex = 0
            else:
                sex = 1
            form.name.data = teacher.t_name
            form.sex.date = sex
        return render_template('/set/teacher.html', form=form)
    else:
        return redirect(url_for('main.login'))


@main.route('/student/set', methods=['GET', 'POST'])
def student_set():
    id = request.args.get('id', 1, type=int)
    insert = request.args.get('insert', 0, type=int)
    clazz = request.args.get('class', 0, type=int)
    form = StudentForm()
    if login_required():
        if form.validate_on_submit():
            if form.sex.data is 1:
                sex = '女'
            else:
                sex = '男'
            name = form.name.data
            address = form.address.data
            birthday = form.birthday.data
            if insert:
                Student(s_class_id=clazz, s_name=name, s_sex=sex, s_address=address, s_birthday=birthday).insert()
                flash('添加成功.')
                return redirect(url_for('main.student'))
            else:
                Student(s_id=id, s_name=name, s_sex=sex, s_address=address, s_birthday=birthday).update()
                flash('更新成功.')
        if not insert:
            student = Student(s_id=id).select(one=True)
            if student.s_sex is '男':
                sex = 0
            else:
                sex = 1
            form.name.data = student.s_name
            form.sex.data = sex
            form.address.data = student.s_address
            form.birthday.data = student.s_birthday
        return render_template('/set/student.html', form=form)
    else:
        return redirect(url_for('main.login'))


@main.route('/course/set', methods=['GET', 'POST'])
def course_set():
    id = request.args.get('id', 1, type=int)
    insert = request.args.get('insert', 0, type=int)
    subject = request.args.get('class', 0, type=int)
    form = CourseForm()
    if login_required():
        if form.validate_on_submit():
            tea_id = form.teacher.data
            name = form.name.data
            type = form.type.data
            term = form.term.data
            room = form.room.data
            if insert:
                Course(c_sub_id=subject, c_tea_id=tea_id,
                       c_name=name, c_type=type, c_term=term, c_room=room).insert()
                flash('添加成功.')
                return redirect(url_for('main.course'))
            else:
                Course(c_id=id, c_sub_id=subject, c_tea_id=tea_id,
                       c_name=name, c_type=type, c_term=term, c_room=room).update()
                flash('更新成功.')
        if not insert:
            course = Course(c_id=id).select(one=True)
            form.teacher.data = course.c_tea_id
            form.name.data = course.c_name
            form.type.data = course.c_type
            form.term.data = course.c_term
            form.room.data = course.c_room
        return render_template('/set/course.html', form=form)
    else:
        return redirect(url_for('main.login'))


@main.route('/teacher/search', methods=['GET', 'POST'])
def teacher_search():
    if login_required():
        page = request.args.get('page', 1, type=int)
        wd = request.args.get('wd', '', type=str)
        form = SearchForm()
        if form.validate_on_submit():
            nwd = form.search.data
            return redirect('/teacher/search?wd={}&page=1'.format(nwd))
        if wd is not None:
            form.search.data = wd
        pagination = TeacherManage.get_search(page, wd)
        return render_template('/search/teacher.html',
                               wd=wd,
                               form=form,
                               pagination=pagination)
    else:
        return redirect(url_for('main.login'))


@main.route('/student/search', methods=['GET', 'POST'])
def student_search():
    if login_required():
        page = request.args.get('page', 1, type=int)
        wd = request.args.get('wd', '', type=str)
        form = SearchForm()
        if form.validate_on_submit():
            nwd = form.search.data
            return redirect('/student/search?wd={}&page=1'.format(nwd))
        if wd is not None:
            form.search.data = wd
        if session.get('role') is STUDENT:
            pagination = StudentManage.get_search(page, wd, session.get('id'))
        else:
            pagination = StudentManage.get_search(page, wd)
        return render_template('/search/student.html',
                               wd=wd,
                               form=form,
                               pagination=pagination)
    else:
        return redirect(url_for('main.login'))


@main.route('/class', methods=['GET', 'POST'])
def clazz():
    if login_required():
        page = request.args.get('page', 1, type=int)
        pagination = ClassManage.get_list(page, session.get('role'), session.get('id'))
        return render_template('/main/class.html', pagination=pagination, flag=session.get('role'))
    else:
        return redirect(url_for('main.login'))


@main.route('/class/<int:id>', methods=['GET', 'POST'])
def class_info(id):
    item = ClassManage.get_info(id)
    return render_template('/info/class.html', item=item)


@main.route('/teacher', methods=['GET', 'POST'])
def teacher():
    if login_required():
        page = request.args.get('page', 1, type=int)
        pagination = TeacherManage.get_list(page, session.get('role'), session.get('id'))
        return render_template('/main/teacher.html', pagination=pagination, flag=session.get('role'))
    else:
        return redirect(url_for('main.login'))


@main.route('/teacher/<int:id>', methods=['GET', 'POST'])
def teacher_info(id):
    item = TeacherManage.get_info(id)
    return render_template('/info/teacher.html', item=item)


@main.route('/department', methods=['GET', 'POST'])
def department():
    department = DepartmentManage.get_list()
    return render_template('/main/department.html', items=department)


@main.route('/subject/<int:id>', methods=['GET', 'POST'])
def subject_info(id):
    item = SubjectManage.get_info(id)
    return render_template('/info/subject.html', item=item)
