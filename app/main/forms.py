from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, BooleanField, SelectField, SubmitField, DateField, PasswordField, DateTimeField
from wtforms.validators import DataRequired, Length, NumberRange, Regexp
from wtforms import ValidationError


class SearchForm(FlaskForm):
    search = StringField('Search...', validators=[DataRequired()])
    submit = SubmitField('搜索')


class LoginForm(FlaskForm):
    account = StringField('账号 : ', validators=[DataRequired(), Length(1, 64)])
    password = PasswordField('密码 : ', validators=[DataRequired()])
    submit = SubmitField('登录')


class TeacherForm(FlaskForm):
    name = StringField('姓 名 : ', validators=[DataRequired(), Length(1, 10)])
    sex = SelectField('性 别 : ', coerce=str)
    update = SubmitField('提 交')

    def __init__(self, *args, **kwargs):
        super(TeacherForm, self).__init__(*args, **kwargs)
        self.sex.choices = [('0', '男'), ('1', '女')]


class StudentForm(FlaskForm):
    name = StringField('姓 名 : ', validators=[DataRequired(), Length(1, 10)])
    sex = SelectField('性 别 : ', coerce=str)
    birthday = DateField('出生日期 : ', format='%Y-%m-%d')
    address = StringField('地 址 : ', validators=[DataRequired(), Length(1, 200)])
    update = SubmitField('提 交')

    def __init__(self, *args, **kwargs):
        super(StudentForm, self).__init__(*args, **kwargs)
        self.sex.choices = [('0', '男'), ('1', '女')]


class CourseForm(FlaskForm):
    teacher = IntegerField('教师编号', validators=[DataRequired()])
    name = StringField('姓 名 : ', validators=[DataRequired(), Length(1, 200)])
    type = StringField('类 型 : ', validators=[DataRequired(), Length(1, 100)])
    term = IntegerField('学 年 : ', validators=[NumberRange(min=2014, max=2019)])
    room = StringField('教 室 : ', validators=[DataRequired(), Length(1, 100)])
    update = SubmitField('提 交')

