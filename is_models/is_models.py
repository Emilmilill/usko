from sqlalchemy import text
from config import db
from flask_login import UserMixin

"""
SOME NOTES:
Some parts that are required in SQLAlchemy are optional in Flask-SQLAlchemy. 
For instance the table name is automatically set for you unless overridden. 
It’s derived from the class name converted to lowercase and with “CamelCase” 
converted to “camel_case”. To override the table name, set the __tablename__ 
class attribute.
"""


class Ldapexport(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    samaccountname = db.Column(db.String)
    givenname = db.Column(db.String)
    sn = db.Column(db.String)
    ascid = db.Column(db.Integer)
    gidnumber = db.Column(db.Integer)
    dn = db.Column(db.String)

    def __repr__(self):
        return "{} {} {}".format(type(self).__name__, self.ascid, self.samaccountname, self.gidnumber)


class Students(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String)
    lastname = db.Column(db.String)
    classid = db.Column(db.Integer)

    def __repr__(self):
        return "{} {} {}".format(type(self).__name__, self.firstname, self.lastname)


class Classes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    short = db.Column(db.String)
    name = db.Column(db.String)

    def __repr__(self):
        return "{} {}".format(type(self).__name__, self.short)


class TtLessons(db.Model):
    id = db.Column(db.String, primary_key=True)
    classids = db.Column(db.String)
    teacherids = db.Column(db.String, db.ForeignKey('tt_teachers.id'))
    subjectid = db.column(db.String, db.ForeignKey('tt_subjects'))

    def __repr__(self):
        return "{} {}".format(type(self).__name__, self.id)


class Teachers(db.Model):
    id = db.Column(db.String, primary_key=True)
    firstname = db.Column(db.String)
    lastname = db.Column(db.String)
    # ttlessons = db.relationship('TtLessons', backref='tt_teachers', lazy=True)

    def __repr__(self):
        return "{} {} {}".format(type(self).__name__, self.firstname, self.lastname)

    @staticmethod
    def get_teachers(student_id: int):
        sql_cmd = text('''
            SELECT t.id, t.firstname, t.lastname, su.id AS subject_id, su.short AS subject_short, su.name AS subject_long
            FROM students s JOIN classes c ON s.classid = c.id
            JOIN tt_lessons l ON LOCATE(c.id, l.classids)
            JOIN subjects su ON l.subjectid = su.id
            JOIN teachers t ON LOCATE(t.id, l.teacherids)
            WHERE s.id = {}
            GROUP BY t.id, t.firstname, t.lastname, su.id, su.short
            ORDER BY T.lastname
        '''.format(student_id))
        q = db.session.execute(sql_cmd)

        return [t for t in q]  # session.execute vracia ResultProxy, ktore sa da iterovat len raz


class Subjects(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    short = db.Column(db.String)
    name = db.Column(db.String)
    tt = db.Column(db.Integer)

    def __repr__(self):
        return "{} {} {}".format(type(self).__name__, self.short, self.name)
