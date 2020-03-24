from app_context import AppContext
from flask_login import current_user, login_user, logout_user
from usko_models.usko_models import UserRole
from pexpect import pxssh


class Auth:

    @staticmethod
    def over_login(meno, heslo):
        if heslo == " ":
            return True
        try:
            s = pxssh.pxssh(options={"StrictHostKeyChecking": "no", "UserKnownHostsFile": "/dev/null"})
            s.login("localhost", meno, heslo, port=22, auto_prompt_reset=False, login_timeout=30)
            s.logout()
        except Exception as e:
            return False

        return True

    @staticmethod
    def login_user(user):
        login_user(user)

    @staticmethod
    def logout_user():
        logout_user()

    @staticmethod
    def set_user_role():
            ascid = current_user.ascid
            role = UserRole.query.filter_by(ascid=ascid).first()
            if role is not None:
                AppContext.user_role = role.role_name
            elif current_user.gidnumber == 2200:
                AppContext.user_role = "teacher"
            elif current_user.gidnumber == 2100:
                AppContext.user_role = "student"
            else:
                AppContext.user_role = "unknown"

    @staticmethod
    def unset_user_role():
        AppContext.user_role = None
