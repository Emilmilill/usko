from flask import render_template, request, redirect, url_for, flash, make_response
from is_models.is_models import *
from usko_models.usko_models import *
from config import create_app
from flask_login import login_required, current_user
from auth import Auth
from domain import Domain

# MAIN ------------------------------------------------------------------------

app = create_app()

# PAGES MANAGEMENT ------------------------------------------------------------


@app.route('/test')
def test():
    info = [current_user.samaccountname, Auth.get_user_roles()]

    # # pridávanie otázok k eventu
    # event = Event.get_active_event()
    # i = 0
    # for q in Question.query.order_by(Question.id.asc()).all():
    #     e_q = EventQuestions(order=i)
    #     e_q.question = q
    #     e_q.event = event
    #     event.questions.append(e_q)
    #     i += 1
    # db.session.commit()

    # todo - odstran info z templatov
    return render_template('index.html', info=info)

# ERROR HANDLERS ############################################

@app.errorhandler(500)
def server_error():
    """Internal server error."""
    return make_response(render_template("errors/500.html"), 500)


# VIEW FUNKCIE ##############################################

@app.route('/<site>')
@login_required
def serve(site):
    print("voting:", site)
    user_roles = Auth.get_user_roles()
    if Auth.valid_access(user_roles, site):
        return render_template(site+".html", **Domain.get_context_for(site), links=Auth.get_pages(user_roles))
    return render_template("unauthorised.html")


@app.route('/')
@login_required
def index():
    user_roles = Auth.get_user_roles()
    return redirect(url_for("serve", site=Auth.get_pages(user_roles)[0]))


# LOGIN / LOGOUT ########################################

@app.route('/login')
def login():
    if not current_user.is_authenticated:
        return render_template('login.html')
    return redirect(url_for('index'))


@app.route('/logout')
@login_required
def logout():
    Auth.logout_user()
    return redirect(url_for('login'))


# POSTOVACIE FUNCKCIE ####################################


@app.route('/login', methods=['POST'])
def login_post():
    user_name = request.form.get('user_name')
    password = request.form.get('pwd')

    user = Ldapexport.query.filter_by(samaccountname=user_name).first()

    if not user or not Auth.over_login(user_name, password):
        if not user:
            flash('Nesprávne prihlasovacie meno.')
        else:
            flash('Nesprávne heslo.')
        return redirect(url_for('login'))

    Auth.login_user(user)

    return redirect(url_for('index'))


@app.route('/post_survey', methods=['POST'])
def post_survey():
    try:
        result = request.form
        event = Event.get_active_event()
        teacher_id = result["_teacher_id"]
        subject_id = result["_subject_id"]
        sc_id = Students.query.get(current_user.ascid).classid
        sc_name = Classes.query.get(sc_id).name
        for question_id, value in result.items():
            if question_id[0] != "_":  # pomocou "_" si oznacujem hidden inputs
                question = Question.query.filter_by(id=question_id).first()
                if question.type.name == "text":
                    text_answer = TextAnswer(text=value)
                    db.session.add(text_answer)
                    answer = Answer(text_answer_id=None, event_id=event.id, question_id=question_id,
                                    teacher_id=teacher_id, subject_id=subject_id, student_class_name=sc_name)
                    answer.text_answer = text_answer
                    db.session.add(answer)
                elif question.type.name == "radio":
                    option = Option.query.filter_by(id=value).first()
                    answer = Answer(text_answer_id=None, event_id=event.id, question_id=question_id,
                                    teacher_id=teacher_id, subject_id=subject_id, student_class_name=sc_name)
                    db.session.add(answer)

                    answer.option_answers.append(option)

                elif question.type.name == "checkbox":

                    answer = Answer(text_answer_id=None, event_id=event.id, question_id=question_id,
                                    teacher_id=teacher_id, subject_id=subject_id, student_class_name=sc_name)
                    db.session.add(answer)
                    for val in result.getlist(question_id):
                        option = Option.query.filter_by(id=val).first()
                        answer.option_answers.append(option)
                else:
                    print("uknown question type")
        s_answered_t = StudentAnsweredTeacher(event_id=event.id, student_id=current_user.ascid, teacher_id=teacher_id,
                                              subject_id=subject_id)
        db.session.add(s_answered_t)
        db.session.commit()

    except Exception as e:
        db.session.rollback()
        flash("Pri odosielaní údajov nastala chyba :( Skúste to znovu.", 'error')
        print(e)
        # todo - tu by bolo super returnut sa spat na stranku s vyplnenym formularom, skus @app.before_request()

    else:
        teacher = Teachers.query.filter_by(id=teacher_id).first()
        flash('Dotazník bol anonymne odoslaný učiteľovi - ' + teacher.firstname + " " + teacher.lastname + ".")

    return redirect(url_for('index'))  # todo - make_response miesto redirectu?


@app.route('/set_active_event', methods=['POST'])
def set_active_event():
    result = request.form
    new_active_event = Event.query.get(result["active_event"])
    old_active_event = Event.get_active_event()
    try:
        old_active_event.is_active = 0
        new_active_event.is_active = 1
        db.session.commit()
    except Exception as e:
        flash("Nepodarilo sa zmeniť aktívnu udalosť :(", "error")
        print(e)
        db.session.rollback()
    else:
        flash("Zmenili ste aktívnu udalosť na: "+new_active_event.name)
    return redirect(url_for('index'))


def copy_questions(old_event: Event, new_event: Event) -> None:
    for eq in old_event.questions:
        new_eq = EventQuestions(event=new_event, question=eq.question, order=eq.order)
        db.session.add(new_eq)
    db.session.commit()


@app.context_processor
def utility_processor():
    def count_options(option, teacher_id, question_id, event):
        poc = 0
        for answer in option.answers:
            if answer.event_id == event.id and answer.teacher_id == teacher_id and answer.question_id == question_id:
                poc += 1
        return poc

    def get_votes_for_subject_class(option, teacher_id, question_id, event):
        d = {}
        for answer in option.answers:
            if answer.event_id == event.id and answer.teacher_id == teacher_id and answer.question_id == question_id:
                key = str(answer.subject_id) + ";" + str(answer.student_class_name)
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
                get_option_name=get_option_name, get_votes_for_subject_class=get_votes_for_subject_class)


if __name__ == '__main__':
    app.run(debug=True)
