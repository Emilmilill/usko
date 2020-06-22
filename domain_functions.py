from vote import app
from usko_models.usko_models import Question, StudentAnsweredTeacher, Option
from is_models.is_models import Subjects


def utility_processor():
    def count_options(option, teacher_id, question_id, event):  # todo - to by mal byt aj subject
        poc = 0
        for answer in option.answers:
            if answer.event_id == event.id and answer.teacher_id == teacher_id and answer.question_id == question_id:
                poc += 1
        return poc

    def text_answers4subject_class(teacher_id, question_id, event):
        res = []
        q = Question.query.get(question_id)
        for answer in q.answers:
            if answer.event_id == event.id and answer.teacher_id == teacher_id:
                key = str(answer.subject_id) + ";" + str(answer.student_class_name)
                res.append([key, Subjects.query.get(answer.subject_id).short, answer.text_answer.text])
        return res

    def text_answers4class(question_id, event):
        res = []
        q = Question.query.get(question_id)
        for answer in q.answers:
            if answer.event_id == event.id:
                res.append([answer.student_class_name, answer.text_answer.text])
        return res

    def get_votes4subject_class(option, teacher_id, question_id, event):
        d = {}
        for answer in option.answers:
            if answer.event_id == event.id and answer.teacher_id == teacher_id and answer.question_id == question_id:
                key = str(answer.subject_id) + ";" + str(answer.student_class_name)
                d[key] = d.get(key, 0) + 1
        res = []
        for key, value in d.items():
            res.append([key, value])
        return res

    def get_votes4class(option, question_id, event):
        d = {}
        for answer in option.answers:
            if answer.event_id == event.id and answer.question_id == question_id:
                key = str(answer.student_class_name)
                d[key] = d.get(key, 0) + 1
        l = []
        for key, value in d.items():
            l.append([key, value])
        return l

    def count_answers(teacher_id, event_id):
        return StudentAnsweredTeacher.query.filter_by(teacher_id=teacher_id, event_id=event_id).count()

    def get_subject_name(subject_id):
        res = "None"
        if subject_id is not None:
            res = Subjects.query.get(subject_id).short
        return res

    def get_option_name(option_id):
        return Option.query.filter_by(id=option_id).first()

    return dict(count_options=count_options, count_answers=count_answers, get_subject_name=get_subject_name,
                get_option_name=get_option_name, get_votes_for_subject_class=get_votes4subject_class,
                get_votes_for_class=get_votes4class, text_answers4subject_class=text_answers4subject_class,
                text_answers4class=text_answers4class)