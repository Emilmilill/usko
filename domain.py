from is_models.is_models import Students, Teachers, Subjects
from usko_models.usko_models import Event, QuestionCategory, StudentAnsweredTeacher, Answer
from flask_login import current_user


class Domain:

    @staticmethod
    def get_context_for(site: str) -> dict:
        if site == "voting":
            return Domain.student_context()
        elif site == "voting_corona":
            return Domain.student_context_corona()
        elif site == "results":
            return Domain.teacher_context()
        elif site == "results2":
            return Domain.special_context()
        elif site == "supervisor":
            return Domain.supervisor_context()
        elif site == "event_management":
            return Domain.event_manager_context()
        else:
            return dict()

    @staticmethod
    def student_context_corona() -> dict:
        event = Event.get_active_event()
        questions = event.questions
        categories = QuestionCategory.get_event_categories(event)
        answered = StudentAnsweredTeacher.query.filter_by(student_id=current_user.ascid, event_id=event.id,
                                                          teacher_id=0, subject_id=0).first() is not None
        return {"name": current_user.ascid, "questions": questions, "categories": categories, "event": event,
                "answered": answered}

    @staticmethod
    def student_context() -> dict:
        event = Event.get_active_event()
        questions = event.questions
        categories = QuestionCategory.get_event_categories(event)
        teachers = Teachers.get_teachers(current_user.ascid)
        student_answered_teacher = StudentAnsweredTeacher.query.filter_by(student_id=current_user.ascid, event_id=event.id)
        answered_teachers_ids = [(o.teacher_id, o.subject_id) for o in student_answered_teacher]
        unanswered_teachers = [t for t in teachers if (t.id, t.subject_id) not in answered_teachers_ids]
        answered_teachers = [t for t in teachers if (t.id, t.subject_id) in answered_teachers_ids]
        student = Students.query.filter_by(id=current_user.ascid).first()
        return {"name": current_user.ascid, "unanswered_teachers": unanswered_teachers, "questions": questions,
                "categories": categories, "answered_teachers": answered_teachers, "student": student, "event": event}

    @staticmethod
    def teacher_context(event) -> dict:
        events = Event.query.filter_by(type_id=1).all()
        answers_count = StudentAnsweredTeacher.query.filter_by(teacher_id=current_user.ascid,
                                                               event_id=event.id).count()
        categories = QuestionCategory.get_event_categories(event)
        teacher = Teachers.query.filter_by(id=current_user.ascid).first()
        subject_ids = [s_id[0] for s_id in Answer.query.
                       with_entities(Answer.subject_id).
                       filter_by(teacher_id=teacher.id, event_id=event.id).distinct().all()]
        subjects = [(s_id, Subjects.query.with_entities(Subjects.name).filter_by(id=s_id).first()[0])
                    for s_id in subject_ids]
        filter_checkboxes = {subject: [answer[0] for answer in Answer.query.with_entities(Answer.student_class_name).
                                                               filter_by(subject_id=subject[0]).distinct().all()]
                             for subject in subjects}
        print(filter_checkboxes)
        return {"teacher": teacher, "event": event, "answers_count": answers_count, "categories": categories,
                "filter_checkboxes": filter_checkboxes, "events": events}

    @staticmethod
    def special_context(event) -> dict:
        events = Event.query.filter_by(type_id=2).all()
        answers_count = StudentAnsweredTeacher.query.filter_by(teacher_id=current_user.ascid,
                                                               event_id=event.id).count()
        categories = QuestionCategory.get_event_categories(event)
        filter_checkboxes = set(answer.student_class_name for answer in event.answers)
        return {"event": event, "answers_count": answers_count, "categories": categories,
                "filter_checkboxes": filter_checkboxes, "events": events}

    @staticmethod
    def supervisor_context() -> dict:
        evaluated_teachers_ids = [t[0] for t in
                                  StudentAnsweredTeacher.query.with_entities(StudentAnsweredTeacher.teacher_id).all()]
        teachers = Teachers.query.order_by(Teachers.lastname).all()
        # todo - vyhod upratovacky a pod (cez join s ldapexport, ascid a gidnumber == 2200)
        evaluated_teachers = [t for t in teachers if t.id in evaluated_teachers_ids]
        not_evaluated_teachers = [t for t in teachers if t.id not in evaluated_teachers_ids]
        answers_count = StudentAnsweredTeacher.query.filter_by(teacher_id=current_user.ascid,  # todo - what?
                                                               event_id=Event.get_active_event().id).count()
        return {"evaluated_teachers": evaluated_teachers, "not_evaluated_teachers": not_evaluated_teachers,
                "event": Event.get_active_event(), "answers_count": answers_count}

    @staticmethod
    def event_manager_context() -> dict:
        events = Event.query.all()
        return {"events": events}



