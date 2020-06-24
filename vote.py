from flask import render_template, request, redirect, url_for, flash, make_response, session
from is_models.is_models import *
from usko_models.usko_models import *
from config import create_app
from flask_login import login_required, current_user
from auth import Auth
from domain import Domain
import domain_functions
from user_roles import UserRoles

# MAIN ------------------------------------------------------------------------

app = create_app()


# LOGIN MANAGEMENT ------------------------------------------------------------

# paruje cookie s Ldapexport objektom
@app.login_manager.user_loader
def load_user(user_id):
    user = Ldapexport.query.get(int(user_id))
    user.roles = UserRoles(user)
    return user

# PAGES MANAGEMENT ------------------------------------------------------------

@app.route('/test')
def test():
    #info = [current_user.samaccountname, current_user.roles.get()]

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
    #return render_template('index.html', info=info)

    return str(session)

# ERROR HANDLERS ############################################

@app.errorhandler(500)
def server_error():
    """Internal server error."""
    return make_response(render_template("errors/500.html"), 500)


# VIEW FUNKCIE ##############################################

@app.route('/results/<event_name>')
@login_required
def results(event_name=None):
    user_roles = current_user.roles
    event = None
    if event_name is not None:
        event = Event.query.filter_by(name=event_name).first()
    if event_name is None or event is None:
        event = Event.query.filter_by(type_id=1).first()
    return render_template('results.html', **Domain.teacher_context(event), links=user_roles.get_link_tuples(),
                           event_name=event_name)


@app.route('/results2/<event_name>')
@login_required
def results2(event_name=None):
    user_roles = current_user.roles
    event = None
    if event_name is not None:
        event = Event.query.filter_by(name=event_name).first()
    if event_name is None or event is None:
        event = Event.query.filter_by(type_id=2).first()
    return render_template('results2.html', **Domain.special_context(event), links=user_roles.get_link_tuples(),
                           event_name=event_name)


@app.route('/<site>')
@login_required
def serve(site):
    user_roles = current_user.roles
    if user_roles.can_access(site):
        if site == "voting" and Event.get_active_event().type.name == "corona":
            site += "_corona"
        elif site == "results":
            return redirect(url_for("results", event_name=Event.query.filter_by(type_id=1).first().name))
        elif site == "results2":
            return redirect(url_for("results2", event_name=Event.query.filter_by(type_id=2).first().name))
        return render_template(site+".html", **Domain.get_context_for(site), links=user_roles.get_link_tuples())
    return render_template("unauthorised.html")

@app.route('/')
@login_required
def index():
    return redirect(url_for("serve", site=current_user.roles.get_pages()[0]))

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

    if not user or not Auth.validate_login(user_name, password):
        if not user:
            flash('Nesprávne prihlasovacie meno.')
        else:
            flash('Nesprávne heslo.')
        return redirect(url_for('login'))

    Auth.login_user(user)

    return redirect(url_for('index'))


@login_required
@app.route('/post_survey_corona', methods=['POST'])
def post_survey_corona():
    try:
        result = request.form
        event = Event.get_active_event()
        teacher_id = 0
        subject_id = 0
        sc_id = Students.query.get(current_user.ascid).classid
        sc_name = Classes.query.get(sc_id).name
        for question_id, value in result.items():
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
        flash('Dotazník bol anonymne odoslaný.')

    return redirect(url_for('index'))  # todo - make_response miesto redirectu?


@login_required
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


@login_required
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
    return domain_functions.utility_processor()


if __name__ == '__main__':
    app.run(debug=True)
