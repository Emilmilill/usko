from config import db
from app_context import AppContext


class Users(db.Model):
    __bind_key__ = 'usko'
    id = db.Column(db.Integer, primary_key=True)
    sync_id = db.Column(db.Integer)
    user_name = db.Column(db.String, unique=True)
    password = db.Column(db.String)


class UserRole(db.Model):
    __bind_key__ = 'usko'
    id = db.Column(db.Integer, primary_key=True)
    ascid = db.Column(db.Integer)
    role_name = db.Column(db.String)


class Event(db.Model):
    __bind_key__ = 'usko'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    is_active = db.Column(db.Boolean)
    questions = db.relationship("EventQuestions", back_populates="event")

    def __repr__(self):
        return "{} {}".format(type(self).__name__, self.name)

    @staticmethod
    def get_active_event():
        return Event.query.filter_by(is_active=True).first()


class QuestionCategory(db.Model):
    __bind_key__ = 'usko'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    questions = db.relationship("Question", backref="category")

    def __repr__(self):
        return "{} {}".format(type(self).__name__, self.name)

    @staticmethod
    def get_event_categories(event):
        ordered_eq = sorted(event.questions, key=lambda eq: eq.order)
        categories = [eq.question.category for eq in ordered_eq]
        seen = set()
        return [c for c in categories if not (c in seen or seen.add(c))]


class QuestionType(db.Model):
    __bind_key__ = 'usko'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    questions = db.relationship("Question", backref="type")

    def __repr__(self):
        return "{} {}".format(type(self).__name__, self.name)


class Question(db.Model):
    __bind_key__ = 'usko'
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String)
    type_id = db.Column(db.String, db.ForeignKey('question_type.id'))
    category_id = db.Column(db.Integer, db.ForeignKey('question_category.id'))
    answers = db.relationship("Answer", backref="question", lazy="dynamic")
    events = db.relationship("EventQuestions", back_populates="question")
    # category (from QuestionCategory backref)
    # type (from QuestionType backref)
    # options (from Option backref)

    def __repr__(self):
        return "{} {}".format(type(self).__name__, self.description)


class Option(db.Model):
    __bind_key__ = 'usko'
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String)
    questions = db.relationship("Question", secondary="question_options", backref=db.backref("options"),
                                lazy="dynamic")
    # answers (from Answer backref)

    def __repr__(self):
        return "{} {}".format(type(self).__name__, self.description)


class TextAnswer(db.Model):
    __bind_key__ = 'usko'
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String)
    answer = db.relationship("Answer", backref="text_answer")

    def __repr__(self):
        return "{} {}".format(type(self).__name__, self.text)


class Answer(db.Model):
    __bind_key__ = 'usko'
    id = db.Column(db.Integer, primary_key=True)
    text_answer_id = db.Column(db.Integer, db.ForeignKey('text_answer.id'))
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'))
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'))
    teacher_id = db.Column(db.Integer)
    subject_id = db.Column(db.Integer)
    student_class_name = db.Column(db.String)  # lebo kazdy rok sa meni meno triedy, ID zostava
    option_answers = db.relationship("Option", secondary="answer_options", backref=db.backref("answers"),
                                     lazy="dynamic")
    # text_answer (from TextAnswer backref)

    def __repr__(self):
        return "{} {}".format(type(self).__name__, self.id)


class StudentAnsweredTeacher(db.Model):
    __bind_key__ = 'usko'
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), primary_key=True)
    teacher_id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, primary_key=True)

    def __repr__(self):
        return "{} {} {}".format(type(self).__name__, self.student_id, self.teacher_id)


class EventQuestions(db.Model):
    __bind_key__ = 'usko'
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), primary_key=True)
    order = db.Column(db.Integer)
    event = db.relationship("Event", back_populates="questions")
    question = db.relationship("Question", back_populates="events")


question_options = db.Table('question_options',
                            db.Column('question_id', db.Integer, db.ForeignKey('question.id')),
                            db.Column('option_id', db.Integer, db.ForeignKey('option.id')),
                            db.Column('order', db.Integer)
                            )


answer_options = db.Table('answer_options',
                          db.Column('answer_id', db.Integer, db.ForeignKey('answer.id')),
                          db.Column('option_id', db.Integer, db.ForeignKey('option.id'))
                          )

