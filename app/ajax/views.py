from flask import render_template, redirect, url_for, abort, flash, request
from . import ajax
from model.model import *


@ajax.route('/ajax/score', methods=['GET', 'POST'])
def score_insert():
    id = request.args.get('id', 1, type=int)
    value = request.args.get('score', 1, type=int)
    tea_id = request.args.get('tea_id', 1, type=int)
    course = Course(c_tea_id=tea_id).select(one=True)
    score = Score(s_stu_id=id, s_cou_id=course.c_id).select(one=True)
    if score.s_score:
        score.s_score = value
        score.update()
        return '1'
    else:
        score.s_score = value
        score.insert()
        return '2'